from context_builder import build_context
from ranking import rank_files
import os

# 1️⃣ Prepare sample results (simulate FAISS results)
# Make sure the paths exist in your data/sample_files folder
sample_results = [
    {
        "path": "../../data/sample_files/pdf_text_extraction.pdf",
        "similarity": 0.82,
        "context": build_context("../../data/sample_files/pdf_text_extraction.pdf")
    },
    {
        "path": "../../data/sample_files/txt_text_extraction.txt",
        "similarity": 0.75,
        "context": build_context("../../data/sample_files/txt_text_extraction.txt")
    },
    {
        "path": "../../data/sample_files/docx_text_extraction.docx",
        "similarity": 0.65,
        "context": build_context("../../data/sample_files/docx_text_extraction.docx")
    }
]

# 2️⃣ Rank them using your ranking.py
final_results = rank_files(sample_results)

# 3️⃣ Print ranked results
print("Ranked Files:\n")
for idx, r in enumerate(final_results, 1):
    context = r["context"]
    print(f"{idx}. {os.path.basename(r['path'])} | Final Score: {r['final_score']}")
    print(f"   Type: {context['file_type']}, Size: {context['size_kb']} KB, Last Modified: {context['last_modified']}\n")
