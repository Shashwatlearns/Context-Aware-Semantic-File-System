import pickle
from sklearn.metrics.pairwise import cosine_similarity

class ContextEngine:
    def __init__(self, index_path="context_engine/index.pkl"):
        try:
            with open(index_path, 'rb') as f:
                self.vectorizer, self.tfidf_matrix, self.file_metadata = pickle.load(f)
        except FileNotFoundError:
            print("Index not found. Please run the Context Builder first.")

    def get_relevant_files(self, query_context, top_n=5):
        """
        Ranks files based on the similarity to the query context.
        query_context: A string (e.g., 'Current project documents' or 'Financial reports')
        """
        # Transform query into the same vector space
        query_vec = self.vectorizer.transform([query_context])
        
        # Calculate Cosine Similarity
        cosine_sim = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Rank indices by score
        related_indices = cosine_sim.argsort()[::-1]
        
        results = []
        for i in related_indices[:top_n]:
            if cosine_sim[i] > 0:  # Only return matches
                results.append({
                    "file": self.file_metadata[i]['name'],
                    "path": self.file_metadata[i]['path'],
                    "score": round(float(cosine_sim[i]), 4)
                })
        
        return results

if __name__ == "__main__":
    engine = ContextEngine()
    # Sample Usage:
    user_context = "Find data related to machine learning" 
    rankings = engine.get_relevant_files(user_context)
    
    print(f"\nResults for context: '{user_context}'")
    for item in rankings:
        print(f"[{item['score']}] {item['file']} ({item['path']})")