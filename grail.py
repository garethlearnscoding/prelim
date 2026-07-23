#!/usr/bin/env python3
import time
import io
import re
import zipfile
from pathlib import Path
import re
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ----------------------------------------------------------------------
# CONFIG — edit these values
# ----------------------------------------------------------------------

URL = "https://grail.moe/library"


OUTPUT_DIR = Path("manual/2ma")

LOAD_MORE_BUTTON_TEXT = "Next"

HEADLESS = False
YEARS = (2025,2024,2023,2022,2021)

# ----------------------------------------------------------------------
def get_page(page):
    text = page.locator("p", has_text=re.compile(r"Page \d+ of \d+")).inner_text()
    return int(re.search(r"Page (\d+)", text).group(1))

def collect_download_links(page,pattern:str = "https://api.grail.moe/note/download") -> set[str]:
    next_button = page.locator(f"button:has-text('{LOAD_MORE_BUTTON_TEXT}')").first
    prev = 1
    seen: set[str] = set()

    while True:
        page.mouse.wheel(0, 2000)

        hrefs = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.href)"
        )
        new_links = {str(h) for h in hrefs if h.startswith(pattern)}
        seen.update(new_links)
        state = next_button.get_attribute("data-headlessui-state")

        if state == "disabled":
            break

        next_button.click()

        # Wait for Load
        time.sleep(0.5)
    return seen

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


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.rstrip(" .")
    return name

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
    save_name = sanitize_filename(save_name)
    save_path = out_dir / save_name
    save_path.write_bytes(data)
    print(f"[OK] Saved -> {save_path}")


params = {
    "category": "GCE 'A' Levels",
    "subject": "H2 Mathematics",
    "doc_type": "Exam Papers",
}



def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        

        page.wait_for_timeout(1500)  # let results settle
        for year in (2020,):
            params["year"] = year
            page.goto(f"https://grail.moe/library?{urlencode(params)}")
            missing = page.locator("h2", has_text="We couldn't find any results :(")
            # print(missing.count())
            # print(missing.is_visible())
            if missing.is_visible():
                continue

            out_dir = OUTPUT_DIR / str(year)
            
            links = collect_download_links(page)

            with open("test.txt", "w") as f:
                f.writelines([i+"\n" for i in list(links)])

            if not links:
                print("[INFO] No download links found — nothing to do.")
                browser.close()
                return

            for link in sorted(links):
                save_download(page.context.request, link, out_dir)

        browser.close()


if __name__ == "__main__":
    main()
