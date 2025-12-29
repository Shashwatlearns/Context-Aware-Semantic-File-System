"""
Ranking System for NeuroDrive
Author: Manvi (Member 4) - Refactored by Team Lead
Purpose: Re-rank FAISS search results with context awareness
"""

from typing import List, Dict
from .context_builder import ContextBuilder


class ContextAwareRanker:
    """Re-ranks search results using context"""
    
    def __init__(self):
        self.context_builder = ContextBuilder()
        
        # Weights for different ranking factors
        self.weights = {
            'similarity': 0.5,    # 50% - semantic similarity from FAISS
            'recency': 0.2,       # 20% - how recent the file is
            'type': 0.2,          # 20% - file type importance
            'size': 0.1           # 10% - file size
        }
    
    def rerank(self, faiss_results: List[Dict], query: str = None) -> List[Dict]:
        """
        Re-rank FAISS results with context awareness
        
        Args:
            faiss_results: Results from FAISS search
            query: Optional query for additional context
            
        Returns:
            Re-ranked results with combined scores
        """
        ranked_results = []
        
        for result in faiss_results:
            # Get base similarity score from FAISS
            similarity_score = result.get('similarity_score', 0.5)
            
            # Build context for this file
            context = self.context_builder.build_context(result)
            
            # Calculate combined score
            combined_score = (
                self.weights['similarity'] * similarity_score +
                self.weights['recency'] * context['recency_score'] +
                self.weights['type'] * context['type_score'] +
                self.weights['size'] * context['size_score']
            )
            
            # Add to result
            result['context_score'] = combined_score
            result['context_breakdown'] = {
                'similarity': similarity_score,
                'recency': context['recency_score'],
                'type': context['type_score'],
                'size': context['size_score']
            }
            
            ranked_results.append(result)
        
        # Sort by combined score (highest first)
        ranked_results.sort(key=lambda x: x['context_score'], reverse=True)
        
        # Update ranks
        for i, result in enumerate(ranked_results, 1):
            result['rank'] = i
        
        return ranked_results
    
    def explain_ranking(self, result: Dict) -> str:
        """Generate explanation for why a file was ranked this way"""
        breakdown = result.get('context_breakdown', {})
        
        explanation = f"Ranked #{result.get('rank', '?')} with score {result.get('context_score', 0):.3f}:\n"
        explanation += f"  - Similarity: {breakdown.get('similarity', 0):.3f}\n"
        explanation += f"  - Recency: {breakdown.get('recency', 0):.3f}\n"
        explanation += f"  - File Type: {breakdown.get('type', 0):.3f}\n"
        explanation += f"  - Size: {breakdown.get('size', 0):.3f}"
        
        return explanation


# Test
if __name__ == '__main__':
    ranker = ContextAwareRanker()
    
    # Mock FAISS results
    test_results = [
        {
            'name': 'old_small.txt',
            'ext': '.txt',
            'size': 5000,
            'similarity_score': 0.8,
            'text': 'test'
        },
        {
            'name': 'recent_large.pdf',
            'ext': '.pdf',
            'size': 20000,
            'similarity_score': 0.75,
            'text': 'test'
        }
    ]
    
    ranked = ranker.rerank(test_results)
    
    for r in ranked:
        print(ranker.explain_ranking(r))
        print()
