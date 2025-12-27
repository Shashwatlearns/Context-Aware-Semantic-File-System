from pypdf import PdfReader
import docx


def extract_content(path: str, ext: str) -> str:
    """
    Extracts text from a file based on its extension.

    :param path: Full file path.
    :param ext: File extension (e.g. '.pdf', '.docx', '.txt').
    :return: Extracted text as a string (may be empty or contain an error message).
    """
    ext = (ext or "").lower().strip()

    if ext == ".pdf":
        return _extract_pdf(path)
    elif ext == ".docx":
        return _extract_docx(path)
    elif ext == ".txt":
        return _extract_txt(path)
    else:
        return ""


def _extract_pdf(path: str) -> str:
    """
    Extract text from a PDF file.
    """
    try:
        reader = PdfReader(path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

        return "\n".join(text_parts).strip()

    except Exception as e:
        return f"Error reading PDF ({path}): {e}"


def _extract_docx(path: str) -> str:
    """
    Extract text from a DOCX file.
    """
    try:
        document = docx.Document(path)
        paragraphs = [para.text for para in document.paragraphs]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        return f"Error reading DOCX ({path}): {e}"


def _extract_txt(path: str) -> str:
    """
    Extract text from a TXT file.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading TXT ({path}): {e}"
