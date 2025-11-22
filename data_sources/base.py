"""
Base classes for data sources
Provides common functionality for caching, error handling, and fallback
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataSourceBase(ABC):
    """Base class for all data sources"""
    
    def __init__(self, cache_dir: str = "data/cache", use_cache: bool = True):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_cache = use_cache
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.last_fetch_time: Dict[str, float] = {}
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    def get_mock_data(self, **kwargs) -> Dict[str, Any]:
        """Get mock data as fallback"""
        pass
    
    def get_data(self, use_cache: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Get data with caching and fallback support
        """
        cache_key = self._generate_cache_key(**kwargs)
        
        # Try cached data first
        if use_cache and self.use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Using cached data for {self.__class__.__name__}")
                return cached
        
        # Try to fetch real data
        try:
            data = self.fetch_data(**kwargs)
            if data:
                self._save_to_cache(cache_key, data)
                return data
        except Exception as e:
            logger.warning(f"Failed to fetch data from {self.__class__.__name__}: {e}")
        
        # Fallback to mock data
        logger.info(f"Using mock data fallback for {self.__class__.__name__}")
        return self.get_mock_data(**kwargs)
    
    def _generate_cache_key(self, **kwargs) -> str:
        """Generate a cache key from kwargs"""
        sorted_kwargs = sorted(kwargs.items())
        return f"{self.__class__.__name__}_{hash(str(sorted_kwargs))}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    
                # Check if cache is still valid (based on timestamp)
                if 'timestamp' in cached_data:
                    age = time.time() - cached_data['timestamp']
                    if age < self._get_cache_ttl():
                        return cached_data['data']
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_entry = {
                'timestamp': time.time(),
                'data': data
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_cache_ttl(self) -> int:
        """Get cache time-to-live in seconds"""
        return 3600  # Default 1 hour
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate fetched data structure"""
        # Override in subclasses for specific validation
        return isinstance(data, dict)


class MockDataMixin:
    """Mixin for mock data fallback"""
    
    @staticmethod
    def log_mock_data_usage(source_name: str, reason: str = "API unavailable"):
        """Log when mock data is used"""
        logger.warning(f"Using mock data for {source_name}: {reason}")



