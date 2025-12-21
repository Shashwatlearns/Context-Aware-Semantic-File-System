# run_ranking.py
from context_engine.main import run_context_engine
from context_engine.ranking import rank_documents, print_ranked_documents

# Step 1: Get contexts from context engine
contexts = run_context_engine()

# Step 2: User query
query = "machine learning research papers"

# Step 3: Rank documents
ranked_docs = rank_documents(query, contexts, top_n=5)

# Step 4: Print ranked results
print_ranked_documents(ranked_docs)
