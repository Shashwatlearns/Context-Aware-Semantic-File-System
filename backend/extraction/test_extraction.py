import os

from file_scanner.scanner import scan_directory
from extraction_module import extract_content

# Compute absolute path to data/sample_files
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(PROJECT_ROOT, "data", "sample_files")


def main():
    print(f"Scanning folder: {FOLDER}\n")

    files = scan_directory(FOLDER)
    if isinstance(files, dict) and "error" in files:
        print(files["error"])
        return

    print(f"Found {len(files)} files in folder.\n")

    print("All files detected (name, ext):")
    for f in files:
        print(f"  - {f['name']}  (ext: '{f['ext']}')")

    # Filter to only supported file types
    supported_exts = {".pdf", ".docx", ".txt"}
    usable_files = [f for f in files if f.get("ext") in supported_exts]

    print("\nSupported files (PDF/DOCX/TXT):")
    if not usable_files:
        print("  - None found. Make sure your sample files have .pdf, .docx or .txt extensions.")
        return

    for f in usable_files:
        print(f"  - {f['name']}  (ext: '{f['ext']}')")

    # Take the first supported file
    sample = usable_files[0]
    print("\nUsing this file for extraction:")
    print(sample)

    text = extract_content(sample["path"], sample["ext"])
    print("\nExtracted text preview (first 500 chars):\n")
    print(text[:500] or "[No text extracted]")


if __name__ == "__main__":
    main()
