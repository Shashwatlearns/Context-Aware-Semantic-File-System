@echo off
echo Setting up Context Engine files...

REM ---------- Create folders ----------
mkdir backend 2>nul
mkdir backend\context_engine 2>nul
mkdir data 2>nul
mkdir data\sample_files 2>nul

REM ---------- Create context_builder.py ----------
if not exist backend\context_engine\context_builder.py (
echo Creating context_builder.py
(
echo import os
echo.
echo def detect_topic(text):
echo     t = text.lower()
echo     if "machine learning" in t or "neural network" in t:
echo         return "Machine Learning"
echo     if "database" in t or "sql" in t:
echo         return "Database"
echo     if "java" in t:
echo         return "Programming"
echo     return "General"
echo.
echo def detect_category(filename):
echo     f = filename.lower()
echo     if "assignment" in f:
echo         return "Assignment"
echo     if "notes" in f:
echo         return "Notes"
echo     if "report" in f:
echo         return "Report"
echo     return "Document"
echo.
echo def process_documents(folder_path):
echo     contexts = []
echo     for filename in os.listdir(folder_path):
echo         path = os.path.join(folder_path, filename)
echo         if not os.path.isfile(path):
echo             continue
echo         with open(path, "r", encoding="utf-8", errors="ignore") as f:
echo             text = f.read()
echo         contexts.append({
echo             "name": filename,
echo             "topic": detect_topic(text),
echo             "category": detect_category(filename),
echo             "preview": text[:100].replace("\n"," ")
echo         })
echo     return contexts
) > backend\context_engine\context_builder.py
)

REM ---------- Create app.py ----------
if not exist backend\app.py (
echo Creating app.py
(
echo from context_engine.context_builder import process_documents
echo.
echo DATA_FOLDER = "../data/sample_files"
echo.
echo def main():
echo     contexts = process_documents(DATA_FOLDER)
echo     print("\n===== CONTEXT ENGINE OUTPUT =====\n")
echo     for c in contexts:
echo         print(f"File: {c['name']}")
echo         print(f"  Topic: {c['topic']}")
echo         print(f"  Category: {c['category']}")
echo         print(f"  Preview: {c['preview']}\n")
echo.
echo if __name__ == "__main__":
echo     main()
) > backend\app.py
)

REM ---------- Create sample files ----------
if not exist data\sample_files\txt_text_extraction.txt (
echo Creating sample text file
echo This document explains machine learning concepts and neural networks. > data\sample_files\txt_text_extraction.txt
)

if not exist data\sample_files\pdf_text_extraction.txt (
echo Creating sample pdf text
echo This report discusses database systems, SQL queries and normalization. > data\sample_files\pdf_text_extraction.txt
)

if not exist data\sample_files\docx_text_extraction.txt (
echo Creating sample docx text
echo This document describes Java classes, OOP principles and inheritance. > data\sample_files\docx_text_extraction.txt
)

echo.
echo ✅ Context Engine setup completed successfully.
pause
