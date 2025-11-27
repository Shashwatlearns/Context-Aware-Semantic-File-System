import os
from pathlib import Path
from typing import List, Dict, Union


def scan_directory(folder_path: str) -> Union[List[Dict], Dict]:
    """
    Scans the given folder and returns a list of files with basic metadata.
    """
    folder = Path(folder_path)

    if not folder.exists():
        return {"error": f"Folder does not exist: {folder_path}"}

    files: List[Dict] = []

    for root, dirs, filenames in os.walk(folder):
        for name in filenames:
            path = Path(root) / name
            try:
                stat = path.stat()
                files.append(
                    {
                        "name": name,
                        "path": str(path),
                        "size": stat.st_size,
                        "ext": path.suffix.lower(),
                        "created": stat.st_ctime,
                        "modified": stat.st_mtime,
                    }
                )
            except OSError:
                continue

    return files
