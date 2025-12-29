import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

class ContextBuilder:
    def __init__(self, data_path="sample_files/", index_path="context_engine/index.pkl"):
        self.data_path = data_path
        self.index_path = index_path
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.file_metadata = []

    def extract_text(self, file_path):
        """Extracts text content based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".txt":
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext == ".json":
                with open(file_path, 'r') as f:
                    return str(json.load(f))
            elif ext == ".csv":
                df = pd.read_csv(file_path)
                return " ".join(df.astype(str).values.flatten())
            # Add PDF/Docx support here if needed using PyMuPDF or docx2txt
            return ""
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return ""

    def build_index(self):
        documents = []
        file_names = []

        for root, _, files in os.walk(self.data_path):
            for file in files:
                path = os.path.join(root, file)
                content = self.extract_text(path)
                if content.strip():
                    documents.append(content)
                    file_names.append(path)
                    self.file_metadata.append({
                        "path": path,
                        "name": file,
                        "size": os.path.getsize(path)
                    })

        # Generate TF-IDF Matrix (The "Semantic" part)
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        # Save index
        with open(self.index_path, 'wb') as f:
            pickle.dump((self.vectorizer, tfidf_matrix, self.file_metadata), f)
        print(f"Index built with {len(file_names)} files.")

if __name__ == "__main__":
    builder = ContextBuilder()
    builder.build_index()