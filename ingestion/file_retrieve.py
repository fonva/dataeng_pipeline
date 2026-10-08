import requests
import zipfile
from pathlib import Path

from date_ranges import generate_file_names


BASE_URL = "https://www.tse.go.cr/zip/movimientos"

YEAR = 2026
MONTH = 2

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOWNLOAD_DIR = PROJECT_ROOT / "data" / "downloads"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def download_file(url: str, output_file: Path) -> None:
    """Download a ZIP file from a URL."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_file.write_bytes(response.content)

    print(f"Downloaded: {output_file.name}")


def extract_txt(zip_file: Path, extract_dir: Path) -> None:
    """Extract TXT file and give it a unique name based on the ZIP file."""

    extract_dir.mkdir(parents=True, exist_ok=True)

    output_file = extract_dir / f"{zip_file.stem}.txt"

    # Skip extraction if the TXT already exists.
    if output_file.exists():
        print(f"Already extracted: {output_file.name}")
        return

    with zipfile.ZipFile(zip_file, "r") as zip_ref:

        txt_files = [
            file_name
            for file_name in zip_ref.namelist()
            if file_name.lower().endswith(".txt")
        ]

        if len(txt_files) != 1:
            raise ValueError(
                f"Expected exactly one TXT file in "
                f"{zip_file.name}, found {len(txt_files)}"
            )

        source_file = txt_files[0]

        with zip_ref.open(source_file) as source:
            output_file.write_bytes(source.read())

        print(f"Extracted: {output_file.name}")


def main() -> None:
    """Download and extract TSE files for the selected month."""

    file_names = generate_file_names(YEAR, MONTH)

    for file_name in file_names:

        zip_file = DOWNLOAD_DIR / file_name

        # Download only if the ZIP does not already exist.
        if zip_file.exists():
            print(f"Already downloaded: {zip_file.name}")
        else:
            url = f"{BASE_URL}/{file_name}"

            download_file(url, zip_file)

        # Extract only if the TXT does not already exist.
        extract_txt(zip_file, RAW_DIR)


if __name__ == "__main__":
    main()
