from sentence_transformers import SentenceTransformer

# Load lightweight BERT-based model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    """
    Convert input text into numerical vector (embedding)
    """
    return model.encode(text)
# Embedding module implemented by ASEP embeddings-vector-db contributor