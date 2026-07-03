#!/usr/bin/env python3
"""
Automates https://grail.moe/library :

1. Opens the library page in Chromium via Playwright.
2. Fills in the headlessui combobox fields (Category / Subject / Year /
   Document Type, or whatever labels you define) with the values you supply.
3. Waits for the results to load (scrolling to trigger any lazy-loading),
   then collects every link matching https://api.grail.moe/note/download/*.
4. Downloads each file (reusing the browser's session/cookies) and saves it
   under:  <OUTPUT_DIR>/<year>/
   - If the download is a zip file, it is extracted into a subfolder named
     after the file (from Content-Disposition, falling back to the id).
   - Otherwise the raw file is saved directly, named/extension inferred
     from Content-Disposition or Content-Type.

Edit the CONFIG section below, then run:
    python grail_scraper.py
"""

import time
import io
import re
import zipfile
from pathlib import Path
import re

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ----------------------------------------------------------------------
# CONFIG — edit these values
# ----------------------------------------------------------------------

URL = "https://grail.moe/library"

# Maps the *visible label text* of each combobox to the value you want typed
# into it. Add/remove entries as needed — the script handles them generically.
FIELDS = {
    "Category": ("eg. A Levels","GCE 'A' Levels"),
    "Subject": ("eg. H2 Math","H2 Physics"),
    # "Year": ("eg. 2026","2023"),
    "Document Type": ("eg. Exam Papers","Exam Papers"),
}

# Where downloaded / extracted files should go. A subfolder named after the
# "Year" field's value will be created inside this directory.
OUTPUT_DIR = Path("test")

# If the page paginates results with a button instead of infinite scroll,
# put its visible text here (leave as None to disable).
LOAD_MORE_BUTTON_TEXT = "Next"

HEADLESS = False  # set False to watch the browser while debugging

# ----------------------------------------------------------------------


def fill_combobox(page, label_text:str, info: list) -> None:
    """Find a headlessui combobox by its visible label text and type
    `value` into it, selecting a matching option if a listbox pops up."""
    placeholder_text,value = info
    input_box = page.get_by_placeholder(placeholder_text)

    # input_box.wait_for(state="visible", timeout=10_000)
    input_box.click()
    input_box.fill("")  # clear any existing value
    input_box.type(value, delay=30)  # type char-by-char so the app's JS listeners fire
    input_box.press("Enter")

    print(f"[FIELD] {label_text} -> {value}")

def get_page(page):
    text = page.locator("p", has_text=re.compile(r"Page \d+ of \d+")).inner_text()
    return int(re.search(r"Page (\d+)", text).group(1))

def collect_download_links(page,pattern:str = "https://api.grail.moe/note/download") -> set[str]:
    next_button = page.locator(f"button:has-text('{LOAD_MORE_BUTTON_TEXT}')").first
    prev = 1
    seen: set[str] = set()

    while True:
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(800)

        hrefs = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.href)"
        )
        new_links = {str(h)+"\n" for h in hrefs if h.startswith(pattern)}
        seen.update(new_links)
        state = next_button.get_attribute("data-headlessui-state")

        if state == "disabled":
            break

        next_button.click()

        # Wait for Load
        time.sleep(0.5)
    return seen

# def collect_download_links(page, pattern: str = "https://api.grail.moe/note/download/") -> set[str]:
#     """Scroll the page to trigger lazy-loading and collect every unique
#     download link matching `pattern`."""
#     seen: set[str] = set()
#     stagnant_rounds = 0
#     max_stagnant_rounds = 4  # stop after several scrolls with no new links

#     while stagnant_rounds < max_stagnant_rounds:
#         hrefs = page.eval_on_selector_all(
#             "a[href]", "els => els.map(e => e.href)"
#         )
#         new_links = {h for h in hrefs if h.startswith(pattern)}
#         before = len(seen)
#         seen.update(new_links)

#         if LOAD_MORE_BUTTON_TEXT:
#             btn = page.locator(f"button:has-text('{LOAD_MORE_BUTTON_TEXT}')").first
#             if btn.count() and btn.is_visible():
#                 btn.click()
#                 page.wait_for_timeout(1000)
#                 continue

#         page.mouse.wheel(0, 2000)
#         page.wait_for_timeout(800)

#         if len(seen) == before:
#             stagnant_rounds += 1
#         else:
#             stagnant_rounds = 0

#     print(f"[INFO] Found {len(seen)} download link(s)")
#     return seen


def guess_extension(content_type: str) -> str:
    mapping = {
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "application/x-zip-compressed": ".zip",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "image/png": ".png",
        "image/jpeg": ".jpg",
    }
    return mapping.get(content_type.split(";")[0].strip().lower(), "")


def save_download(request_context, url: str, out_dir: Path) -> None:
    """Fetch `url` (reusing the browser session) and save/extract it."""
    idx = url.rstrip("/").split("/")[-1]  # trailing id, used as a fallback name

    try:
        resp = request_context.get(url, timeout=30_000)
    except Exception as e:
        print(f"[FAIL] {url}: {e}")
        return

    if resp.status != 200:
        print(f"[FAIL] {url}: HTTP {resp.status}")
        return

    data = resp.body()
    headers = resp.headers
    cd = headers.get("content-disposition", "")
    content_type = headers.get("content-type", "")

    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd)
    filename = m.group(1) if m else None

    out_dir.mkdir(parents=True, exist_ok=True)

    is_zip = zipfile.is_zipfile(io.BytesIO(data))

    if is_zip:
        folder_name = Path(filename).stem if filename else idx
        extract_dir = out_dir / folder_name
        extract_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(extract_dir)
            print(f"[OK] Extracted -> {extract_dir}")
        except Exception as e:
            print(f"[FAIL] Extracting {url}: {e}")
        return

    # Non-zip: save the raw file directly into out_dir
    if filename:
        save_name = filename
    else:
        ext = guess_extension(content_type) or ""
        save_name = f"{idx}{ext}"

    save_path = out_dir / save_name
    save_path.write_bytes(data)
    print(f"[OK] Saved -> {save_path}")


def main() -> None:
    year_value = FIELDS.get("Year", "unknown_year")
    out_dir = OUTPUT_DIR / str(year_value)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        page.goto(URL)

        for label_text, value in FIELDS.items():
            fill_combobox(page, label_text, value)

        page.wait_for_timeout(1500)  # let results settle

        links = collect_download_links(page)

        with open("test.txt", "w") as f:
            f.writelines(list(links))

        if not links:
            print("[INFO] No download links found — nothing to do.")
            browser.close()
            return

        # for link in sorted(links):
        #     save_download(page.context.request, link, out_dir)

        # browser.close()


if __name__ == "__main__":
    main()
