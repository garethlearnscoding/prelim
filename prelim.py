import requests
import io
import zipfile
from pathlib import Path
import re

BASE = "https://api.grail.moe/note/download/"
OUTDIR = Path("papers")
OUTDIR.mkdir(exist_ok=True)

for i in range(0, 100000):
    url = BASE + str(i)

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        continue

    data = r.content

    try:
        if not zipfile.is_zipfile(io.BytesIO(data)):
            continue

        cd = r.headers.get("Content-Disposition", "")
        m = re.search(r'filename="?([^"]+)"?', cd)

        folder_name = (
            Path(m.group(1)).stem
            if m
            else str(i)
        )

        extract_dir = OUTDIR / folder_name
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(extract_dir)

        print(f"Extracted: {extract_dir}")

    except Exception as e:
        print(f"Failed {i}: {e}")