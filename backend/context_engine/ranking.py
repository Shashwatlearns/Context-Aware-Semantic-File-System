# context_engine_run.py
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from context_engine.context_builder import process_documents

# ---------- Context Engine ----------
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data/sample_files")

def run_context_engine(data_folder=DATA_FOLDER):
    """Process all supported files and return list of context dicts"""
    contexts = process_documents(data_folder)
    return contexts

# ---------- Ranking Functions ----------
def rank_documents(query, contexts, top_n=5):
    """Rank documents by similarity to the user query"""
    if not contexts:
        return []

    documents = [c['preview'] for c in contexts]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([query] + documents)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    for i, c in enumerate(contexts):
        c['score'] = float(similarities[i])
    ranked = sorted(contexts, key=lambda x: x['score'], reverse=True)
    return ranked[:top_n]

def print_ranked_documents(ranked_docs):
    """Nicely print ranked documents with scores"""
    print("\n===== RANKED DOCUMENTS =====\n")
    for idx, doc in enumerate(ranked_docs, 1):
        print(f"{idx}. File: {doc['name']}")
        print(f"   Topic: {doc['topic']}")
        print(f"   Category: {doc['category']}")
        print(f"   Score: {doc['score']:.4f}")
        preview = doc['preview']
        if len(preview) > 150:
            preview = preview[:150] + "..."
        print(f"   Preview: {preview}\n")

# ---------- Main ----------
if __name__ == "__main__":
    print("Running Context Engine...")
    contexts = run_context_engine()
    print(f"Processed {len(contexts)} files.")

    query = input("\nEnter your search query: ")
    ranked_docs = rank_documents(query, contexts, top_n=5)
    print_ranked_documents(ranked_docs)
