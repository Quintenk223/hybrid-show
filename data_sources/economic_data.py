"""
Economic Data Source
Handles localized economic metrics for intra-country comparisons
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from .base import DataSourceBase, MockDataMixin
from .config import DataSourceConfig
import logging

logger = logging.getLogger(__name__)


class EconomicDataSource(DataSourceBase, MockDataMixin):
    """
    Handles economic geography data:
    - Labor Friction Dispersion (LFD) by prefecture
    - Location efficiency multipliers (coastal vs inland)
    - Migration vulnerability by region
    - Wealth and productivity correlations
    """
    
    def __init__(self, config: DataSourceConfig = None):
        super().__init__(cache_dir="data/cache/economic", use_cache=True)
        self.config = config or DataSourceConfig()
        self.economic_db: Dict[str, Any] = {}
        self.lfd_db: Dict[str, Any] = {}
        self._load_database()
    
    def _get_cache_ttl(self) -> int:
        return self.config.ECONOMIC_REFRESH_INTERVAL
    
    def _load_database(self):
        """Load economic geography database"""
        db_path = Path(self.config.ECONOMIC_GEOGRAPHY_DB_PATH)
        if db_path.exists():
            try:
                with open(db_path, 'r') as f:
                    self.economic_db = json.load(f)
                logger.info(f"Loaded economic database from {db_path}")
            except Exception as e:
                logger.error(f"Error loading economic database: {e}")
        
        # Also load labor friction data
        lfd_path = Path(self.config.LABOR_FRICTION_DB_PATH)
        if lfd_path.exists():
            try:
                with open(lfd_path, 'r') as f:
                    self.lfd_db = json.load(f)
                logger.info(f"Loaded labor friction database from {lfd_path}")
            except Exception as e:
                logger.error(f"Error loading LFD database: {e}")
                self.lfd_db = {}
        else:
            self.lfd_db = {}
    
    def fetch_data(self, location_prefecture: str, location_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch economic data for a specific location
        """
        result = {}
        
        # Fetch LFD
        lfd = self._fetch_lfd(location_prefecture)
        if lfd is not None:
            result['labor_friction_dispersion'] = lfd
        else:
            raise Exception("Failed to fetch LFD")
        
        # Fetch efficiency multiplier
        efficiency = self._fetch_efficiency_multiplier(location_prefecture, location_type)
        if efficiency is not None:
            result['wealth_efficiency_multiplier'] = efficiency
        else:
            raise Exception("Failed to fetch efficiency multiplier")
        
        # Fetch migration vulnerability
        migration_risk = self._fetch_migration_vulnerability(location_prefecture)
        if migration_risk is not None:
            result['migration_vulnerability'] = migration_risk
        
        return result
    
    def _fetch_lfd(self, prefecture: str) -> Optional[float]:
        """
        Fetch Labor Friction Dispersion score
        
        LFD is substantially higher (avg std dev 1.18) than output frictions (0.11)
        Higher LFD = greater payroll volatility and input market distortion
        """
        if prefecture in self.lfd_db:
            lfd_score = self.lfd_db[prefecture].get('lfd_score', 1.0)
            logger.info(f"Fetched LFD for {prefecture}: {lfd_score}")
            return lfd_score
        
        # Try to infer from location type if exact match not found
        if prefecture in self.economic_db:
            location_data = self.economic_db[prefecture]
            # Estimate LFD based on region characteristics
            # Coastal/wealthy = lower LFD, Inland/poor = higher LFD
            if location_data.get('location_type') == 'Coastal':
                estimated_lfd = 0.85  # Lower friction
            else:
                estimated_lfd = 1.15  # Higher friction
            
            logger.info(f"Estimated LFD for {prefecture}: {estimated_lfd}")
            return estimated_lfd
        
        return None
    
    def _fetch_efficiency_multiplier(self, prefecture: str, location_type: Optional[str] = None) -> Optional[float]:
        """
        Fetch wealth-adjusted efficiency multiplier
        
        Coastal prefectures: 0.085 friction
        Inland prefectures: 0.108 friction
        """
        # Determine location type if not provided
        if not location_type and prefecture in self.economic_db:
            location_type = self.economic_db[prefecture].get('location_type')
        
        if location_type == 'Coastal':
            return 0.085
        elif location_type == 'Inland':
            return 0.108
        else:
            # Default based on prefecture name patterns
            coastal_keywords = ['Shanghai', 'Shenzhen', 'Guangzhou', 'Ningbo', 'Qingdao']
            if any(keyword in prefecture for keyword in coastal_keywords):
                return 0.085
            else:
                return 0.108
    
    def _fetch_migration_vulnerability(self, prefecture: str) -> Optional[float]:
        """
        Fetch migration vulnerability score (0-1)
        
        Less developed regions vulnerable to labor outflow during policy shifts
        """
        if prefecture in self.economic_db:
            return self.economic_db[prefecture].get('migration_vulnerability', 0.3)
        
        # Estimate based on location type
        if 'Coastal' in prefecture or any(city in prefecture for city in ['Shanghai', 'Shenzhen', 'Beijing']):
            return 0.15  # Lower vulnerability (developed regions)
        else:
            return 0.35  # Higher vulnerability (less developed)
    
    def get_mock_data(self, location_prefecture: str = "Shanghai (YRD)", **kwargs) -> Dict[str, Any]:
        """Mock data fallback"""
        self.log_mock_data_usage("EconomicData", "Database unavailable")
        
        # Determine location type from name
        location_type = "Coastal" if any(x in location_prefecture for x in ["Shanghai", "Shenzhen", "YRD", "PRD"]) else "Inland"
        
        return {
            "labor_friction_dispersion": 1.10 if location_type == "Coastal" else 1.20,
            "wealth_efficiency_multiplier": 0.085 if location_type == "Coastal" else 0.108,
            "migration_vulnerability": 0.20 if location_type == "Coastal" else 0.40
        }

