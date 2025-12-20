import os
from file_scanner.scanner import scan_directory
from extraction.extraction_module import extract_content

# Path to sample files (relative to backend/)
FOLDER = os.path.join("..", "data", "sample_files")

def main():
    print(f"Scanning folder: {FOLDER}\n")
    files = scan_directory(FOLDER)
    
    if isinstance(files, dict) and "error" in files:
        print(files["error"])
        return
    
    print(f"Found {len(files)} files in folder.\n")
    
    print("All files detected:")
    for f in files:
        print(f"  - {f['name']} (ext: '{f['ext']}')")
    
    # Filter supported files
    supported_exts = {".pdf", ".docx", ".txt"}
    usable_files = [f for f in files if f.get("ext") in supported_exts]
    
    print(f"\nSupported files: {len(usable_files)}")
    
    # Test extraction
    for f in usable_files:
        print(f"\n--- {f['name']} ---")
        text = extract_content(f["path"], f["ext"])
        
        if "Error" in text:
            print(f"❌ {text}")
        else:
            print(f"✅ Extracted {len(text)} chars")
            print(f"Preview: {text[:200]}...\n")

if __name__ == "__main__":
    main()
