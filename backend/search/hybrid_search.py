"""
Hybrid Search Engine combining Semantic (FAISS) and Keyword (BM25) search
"""

from typing import List, Dict, Optional
import numpy as np
from collections import Counter
import math


class BM25:
    """BM25 algorithm for keyword-based search"""
    
    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.corpus_size = len(corpus)
        
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        self.doc_freqs = self._calculate_doc_frequencies()
        self.idf = self._calculate_idf()
        self.avgdl = sum(len(doc) for doc in self.tokenized_corpus) / self.corpus_size
        self.doc_lens = [len(doc) for doc in self.tokenized_corpus]
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        tokens = text.lower().split()
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be'
        }
        return [token for token in tokens if token not in stop_words]
    
    def _calculate_doc_frequencies(self) -> Dict[str, int]:
        """Calculate document frequency for each term"""
        df = {}
        for doc in self.tokenized_corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] = df.get(term, 0) + 1
        return df
    
    def _calculate_idf(self) -> Dict[str, float]:
        """Calculate IDF for each term"""
        idf = {}
        for term, df in self.doc_freqs.items():
            idf[term] = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1)
        return idf
    
    def get_scores(self, query: str) -> np.ndarray:
        """Calculate BM25 scores for query against all documents"""
        query_tokens = self._tokenize(query)
        scores = np.zeros(self.corpus_size)
        
        for doc_idx, doc in enumerate(self.tokenized_corpus):
            doc_len = self.doc_lens[doc_idx]
            score = 0
            term_freqs = Counter(doc)
            
            for term in query_tokens:
                if term not in term_freqs:
                    continue
                
                idf = self.idf.get(term, 0)
                tf = term_freqs[term]
                
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                
                score += idf * (numerator / denominator)
            
            scores[doc_idx] = score
        
        return scores


class HybridSearchEngine:
    """Combines semantic (FAISS) and keyword (BM25) search"""
    
    def __init__(self, embedder, faiss_db, alpha: float = 0.7):
        self.embedder = embedder
        self.faiss_db = faiss_db
        self.alpha = alpha
        self.bm25 = None
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        """Build BM25 index from FAISS metadata"""
        if not self.faiss_db.metadata:
            print("[WARN]  No documents in database, BM25 index not built")
            return
        
        documents = [m.get('text', '') for m in self.faiss_db.metadata]
        self.bm25 = BM25(documents)
        print(f"[OK] BM25 index built with {len(documents)} documents")
    
    def rebuild_index(self):
        """Rebuild BM25 index"""
        self._build_bm25_index()
    
    def search(
        self, 
        query: str, 
        k: int = 10,
        alpha: Optional[float] = None,
        min_score: float = 0.0
    ) -> List[Dict]:
        """Hybrid search combining semantic and keyword matching"""
        if alpha is None:
            alpha = self.alpha
        
        if self.bm25 is None:
            self._build_bm25_index()
        
        if self.bm25 is None:
            print("[WARN]  BM25 not available, using semantic search only")
            return self._semantic_only_search(query, k)
        
        # Semantic search
        query_embedding = self.embedder.encode(query)
        semantic_results = self.faiss_db.search(query_embedding, k=min(k * 3, 100))
        
        if not semantic_results:
            return []
        
        # Get BM25 scores
        bm25_scores = self.bm25.get_scores(query)
        
        # Normalize BM25 scores
        if bm25_scores.max() > 0:
            bm25_scores_normalized = bm25_scores / bm25_scores.max()
        else:
            bm25_scores_normalized = bm25_scores
        
        # Combine scores
        combined_results = {}
        
        for result in semantic_results:
            doc_idx = result.get('rank', 1) - 1
            semantic_score = result.get('similarity_score', 0)
            bm25_score = (
                bm25_scores_normalized[doc_idx] 
                if doc_idx < len(bm25_scores_normalized) 
                else 0
            )
            
            hybrid_score = alpha * semantic_score + (1 - alpha) * bm25_score
            
            if hybrid_score >= min_score:
                result['semantic_score'] = float(semantic_score)
                result['bm25_score'] = float(bm25_score)
                result['hybrid_score'] = float(hybrid_score)
                result['search_method'] = 'hybrid'
                combined_results[result['path']] = result
        
        # Sort by hybrid score
        final_results = sorted(
            combined_results.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )[:k]
        
        for i, result in enumerate(final_results, 1):
            result['rank'] = i
        
        return final_results
    
    def _semantic_only_search(self, query: str, k: int) -> List[Dict]:
        """Fallback to semantic-only search"""
        query_embedding = self.embedder.encode(query)
        results = self.faiss_db.search(query_embedding, k=k)
        
        for result in results:
            result['semantic_score'] = result.get('similarity_score', 0)
            result['hybrid_score'] = result['semantic_score']
            result['search_method'] = 'semantic_only'
        
        return results
    
    def explain_score(self, result: Dict) -> str:
        """Generate explanation for search result score"""
        explanation = f" Score Breakdown for '{result['name']}':\n"
        explanation += f"  • Final Score: {result.get('hybrid_score', 0):.3f}\n"
        
        if 'semantic_score' in result:
            explanation += f"  • Semantic Match: {result['semantic_score']:.3f} "
            explanation += f"(weight: {self.alpha:.1%})\n"
        
        if 'bm25_score' in result:
            explanation += f"  • Keyword Match: {result['bm25_score']:.3f} "
            explanation += f"(weight: {1-self.alpha:.1%})\n"
        
        explanation += f"  • Method: {result.get('search_method', 'unknown')}"
        
        return explanation

