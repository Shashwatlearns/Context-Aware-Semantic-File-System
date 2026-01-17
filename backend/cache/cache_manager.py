"""
Caching Layer for NeuroDrive
"""

import hashlib
import time
import pickle
from typing import Any, Optional, Dict
from collections import OrderedDict
import threading


class CacheManager:
    """Thread-safe in-memory cache with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
    
    def _generate_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, str):
            key_data = data.encode('utf-8')
        else:
            key_data = pickle.dumps(data)
        
        return hashlib.md5(key_data).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            value, timestamp, ttl = self.cache[key]
            
            if time.time() - timestamp > ttl:
                del self.cache[key]
                self.stats['expirations'] += 1
                self.stats['misses'] += 1
                return None
            
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl if ttl is not None else self.default_ttl
        
        with self.lock:
            if len(self.cache) >= self.max_size and key not in self.cache:
                self.cache.popitem(last=False)
                self.stats['evictions'] += 1
            
            self.cache[key] = (value, time.time(), ttl)
            self.cache.move_to_end(key)
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'expirations': 0
            }
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (
                self.stats['hits'] / total_requests 
                if total_requests > 0 
                else 0
            )
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': f"{hit_rate:.2%}",
                **self.stats
            }


class QueryCache:
    """Specialized cache for search queries"""
    
    def __init__(self):
        self.embedding_cache = CacheManager(max_size=500, default_ttl=7200)
        self.result_cache = CacheManager(max_size=200, default_ttl=1800)
    
    def get_embedding(self, query: str):
        """Get cached embedding for query"""
        key = self.embedding_cache._generate_key(query.lower().strip())
        return self.embedding_cache.get(key)
    
    def set_embedding(self, query: str, embedding):
        """Cache embedding for query"""
        key = self.embedding_cache._generate_key(query.lower().strip())
        self.embedding_cache.set(key, embedding)
    
    def get_results(self, query: str, k: int):
        """Get cached search results"""
        key = self.result_cache._generate_key((query.lower().strip(), k))
        return self.result_cache.get(key)
    
    def set_results(self, query: str, k: int, results):
        """Cache search results"""
        key = self.result_cache._generate_key((query.lower().strip(), k))
        self.result_cache.set(key, results)
    
    def clear_all(self):
        """Clear both caches"""
        self.embedding_cache.clear()
        self.result_cache.clear()
    
    def get_stats(self) -> Dict:
        """Get statistics for both caches"""
        return {
            'embedding_cache': self.embedding_cache.get_stats(),
            'result_cache': self.result_cache.get_stats()
        }


query_cache = QueryCache()
