import requests
import zipfile
from pathlib import Path


URL = "https://www.tse.go.cr/zip/movimientos/nac_febrero2026_01_05.zip"

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DOWNLOAD_DIR = PROJECT_ROOT / "data" / "downloads"
EXTRACT_DIR = PROJECT_ROOT / "data" / "raw"


def download_file(url: str, output_file: Path) -> None:
    """Download a ZIP file from a URL."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_file.write_bytes(response.content)

    print(f"Downloaded: {output_file}")


def extract_zip(zip_file: Path, extract_dir: Path) -> None:
    """Extract only TXT files from the ZIP file."""
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        for file in zip_ref.namelist():
            if file.lower().endswith(".txt"):
                zip_ref.extract(file, extract_dir)
                print(f"Extracted: {file}")

    print(f"TXT files extracted to: {extract_dir}")


def main() -> None:
    """Download and extract the TSE file."""

    zip_file = DOWNLOAD_DIR / "nac_febrero2026_01_05.zip"

    download_file(URL, zip_file)
    extract_zip(zip_file, EXTRACT_DIR)


if __name__ == "__main__":
    main()
