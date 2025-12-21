import os
from typing import List, Dict

from PyPDF2 import PdfReader
from docx import Document


# ---------------- TEXT EXTRACTION ----------------

def extract_text(file_path: str) -> str:
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    if file_path.endswith(".docx"):
        doc = Document(file_path)
        return " ".join(p.text for p in doc.paragraphs)

    return ""


# ---------------- CONTEXT ENGINE ----------------

def detect_topic(text: str) -> str:
    t = text.lower()

    if "machine learning" in t or "neural network" in t:
        return "Machine Learning"
    if "database" in t or "sql" in t:
        return "Database"
    if "java" in t or "class" in t:
        return "Programming"

    return "General"


def detect_category(filename: str) -> str:
    name = filename.lower()

    if "assignment" in name:
        return "Assignment"
    if "notes" in name:
        return "Notes"
    if "report" in name:
        return "Report"

    return "Document"


# ---------------- MAIN PROCESS FUNCTION ----------------

def process_documents(folder_path: str) -> List[Dict]:
    contexts = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        text = extract_text(file_path)

        context = {
            "name": filename,
            "topic": detect_topic(text),
            "category": detect_category(filename),
            "preview": text[:100].replace("\n", " ")
        }

        contexts.append(context)

    return contexts
