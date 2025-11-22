"""
AHP Data Source - Loads technical viability scores for suppliers
"""

from ahp_criteria import AHPSupplierScores, get_mock_ahp_scores
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict


class AHPDataSource:
    """Data source for AHP (Analytic Hierarchy Process) technical viability scores"""
    
    def __init__(self, config=None):
        self.config = config
        self.db_path = Path('data/ahp_scores.json')
        self.logger = logging.getLogger(__name__)
    
    def _fetch_from_database(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Load AHP scores from JSON database"""
        if not self.db_path.exists():
            return None
        
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                ahp_db = json.load(f)
            
            if supplier_id in ahp_db:
                return ahp_db[supplier_id]
        except Exception as e:
            self.logger.warning(f"Error loading AHP scores from database: {e}")
        
        return None
    
    def get_data(self, supplier_id: str) -> Dict[str, Any]:
        """
        Get AHP scores for a supplier
        
        Args:
            supplier_id: Supplier identifier (e.g., "CHINA_ALPHA")
        
        Returns:
            Dictionary with AHP criterion scores (0-1 scale)
        """
        # Try database first (database-first approach)
        data = self._fetch_from_database(supplier_id)
        
        if data is None:
            # Fallback to mock
            self.logger.info(f"Using mock AHP data for {supplier_id}: Database unavailable")
            ahp_scores = get_mock_ahp_scores(supplier_id)
            data = {k: v for k, v in asdict(ahp_scores).items() if k != 'supplier_id'}
        
        return data
    
    def get_ahp_scores_object(self, supplier_id: str) -> AHPSupplierScores:
        """Get AHP scores as AHPSupplierScores dataclass object"""
        data = self.get_data(supplier_id)
        
        # Ensure supplier_id is set
        if 'supplier_id' not in data:
            data['supplier_id'] = supplier_id
        
        # Remove notes field if present
        data = {k: v for k, v in data.items() if k != 'notes'}
        
        return AHPSupplierScores(**data)

