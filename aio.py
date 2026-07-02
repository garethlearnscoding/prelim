import asyncio
import aiohttp
import zipfile
import io
import re
from pathlib import Path

BASE = "https://api.grail.moe/note/download/"
OUTDIR = Path("papers")
OUTDIR.mkdir(exist_ok=True)

START = 10000
END = 50000

CONCURRENCY = 50  # adjust: 20–100 safe range

sem = asyncio.Semaphore(CONCURRENCY)


def extract_zip(data: bytes, extract_path: Path, idx: int):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(extract_path)
        print(f"[OK] {idx} extracted",flush=True)
    except Exception as e:
        print(f"[FAIL] unzip {idx}: {e}",flush=True)


async def fetch(session: aiohttp.ClientSession, url: str, idx: int):
    async with sem:
        for attempt in range(5):
            try:
                async with session.get(url, timeout=20) as r:

                    if r.status == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue

                    if r.status != 200:
                        return None

                    data = await r.read()
                    return data

            except Exception:
                await asyncio.sleep(1)

        return None


def is_zip(data: bytes):
    return zipfile.is_zipfile(io.BytesIO(data))


async def worker(session, idx):
    url = BASE + str(idx)

    data = await fetch(session, url, idx)
    if not data:
        return

    if not is_zip(data):
        return

    extract_path = OUTDIR / str(idx)
    extract_path.mkdir(exist_ok=True)

    extract_zip(data, extract_path, idx)


async def main():
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [worker(session, i) for i in range(START, END)]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())