"""
Context Builder for NeuroDrive
Author: Manvi (Member 4) - Refactored by Team Lead
Purpose: Add context-aware enhancements to search results
"""

from datetime import datetime
from typing import Dict, List
import os


class ContextBuilder:
    """Builds context information from file metadata"""
    
    def __init__(self):
        self.file_type_weights = {
            '.pdf': 1.2,    # PDFs slightly more important
            '.docx': 1.1,   # Word docs important
            '.txt': 1.0     # Text files baseline
        }
    
    def build_context(self, file_metadata: Dict) -> Dict:
        """
        Build context from file metadata
        
        Args:
            file_metadata: Dictionary with file info
            
        Returns:
            Context dictionary with scores and features
        """
        context = {
            'recency_score': self._calculate_recency_score(file_metadata),
            'type_score': self._calculate_type_score(file_metadata),
            'size_score': self._calculate_size_score(file_metadata),
            'keywords': self._extract_keywords(file_metadata.get('text', ''))
        }
        
        return context
    
    def _calculate_recency_score(self, metadata: Dict) -> float:
        """Score based on how recent the file is (0-1)"""
        # For now, return 1.0 (can enhance with actual timestamps later)
        return 1.0
    
    def _calculate_type_score(self, metadata: Dict) -> float:
        """Score based on file type importance"""
        ext = metadata.get('ext', '.txt')
        return self.file_type_weights.get(ext, 1.0)
    
    def _calculate_size_score(self, metadata: Dict) -> float:
        """Score based on file size (larger = more content = higher score)"""
        size = metadata.get('size', 0)
        
        # Normalize: files > 10KB get score 1.0, smaller get proportional
        if size > 10000:
            return 1.0
        return size / 10000
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction (can be enhanced)
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return top 10 most frequent
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]


# Test
if __name__ == '__main__':
    builder = ContextBuilder()
    
    test_metadata = {
        'name': 'test.pdf',
        'ext': '.pdf',
        'size': 15000,
        'text': 'machine learning artificial intelligence data science'
    }
    
    context = builder.build_context(test_metadata)
    print('Context:', context)

