#!/usr/bin/env python3
"""
Watches a folder indefinitely for .zip files, extracts them into the same
folder, then deletes the zip file.

Usage:
    python watch_unzip.py /path/to/folder [--interval 5]
"""

import argparse
import shutil
import sys
import time
import zipfile
from pathlib import Path


def clean_macos_cruft(extract_dir: Path) -> None:
    """Remove macOS-specific junk (__MACOSX folders, .DS_Store files)
    that may have been introduced by extracting this zip."""
    # Remove __MACOSX directories anywhere under extract_dir
    for macosx_dir in extract_dir.rglob("__MACOSX"):
        if macosx_dir.is_dir():
            shutil.rmtree(macosx_dir, ignore_errors=True)
            print(f"[CLEAN] Removed folder: {macosx_dir}")

    # Remove .DS_Store files anywhere under extract_dir
    for ds_store in extract_dir.rglob(".DS_Store"):
        try:
            ds_store.unlink()
            print(f"[CLEAN] Removed file: {ds_store}")
        except OSError:
            pass

    # Remove AppleDouble files (e.g. "._filename") anywhere under extract_dir
    for dot_underscore in extract_dir.rglob("._*"):
        if dot_underscore.is_file():
            try:
                dot_underscore.unlink()
                print(f"[CLEAN] Removed file: {dot_underscore}")
            except OSError:
                pass


def unzip_and_remove(zip_path: Path) -> None:
    """Extract zip_path into a subfolder named after the zip (same stem),
    then delete the zip."""
    extract_dir = zip_path.parent / zip_path.stem

    # Avoid clobbering an existing folder/file with the same name
    if extract_dir.exists():
        suffix = 1
        candidate = extract_dir
        while candidate.exists():
            candidate = zip_path.parent / f"{zip_path.stem}_{suffix}"
            suffix += 1
        extract_dir = candidate

    try:
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
        clean_macos_cruft(extract_dir)
        zip_path.unlink()
        print(f"[OK] Extracted to '{extract_dir.name}/' and removed: {zip_path.name}")
    except zipfile.BadZipFile:
        print(f"[SKIP] Not a valid zip (yet?): {zip_path.name}")
    except PermissionError:
        # File might still be mid-copy/write; skip this round, try again later
        print(f"[SKIP] File in use, will retry later: {zip_path.name}")
    except Exception as e:
        print(f"[ERROR] Failed on {zip_path.name}: {e}")


def watch_folder(folder: Path, interval: float) -> None:
    print(f"Watching '{folder}' every {interval}s for .zip files... (Ctrl+C to stop)")
    while True:
        try:
            for zip_path in sorted(folder.glob("*.zip")):
                if zip_path.is_file():
                    unzip_and_remove(zip_path)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[ERROR] Loop error: {e}")

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Watch a folder and auto-unzip .zip files.")
    parser.add_argument("folder", type=str, help="Path to the folder to watch")
    parser.add_argument(
        "--interval", type=float, default=5.0,
        help="Seconds between checks (default: 5)"
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    try:
        watch_folder(folder, args.interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")


if __name__ == "__main__":
    main()