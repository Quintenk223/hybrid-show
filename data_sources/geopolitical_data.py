"""
Geopolitical Data Source
Fetches and calibrates geopolitical risk metrics
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from .base import DataSourceBase, MockDataMixin
from .config import DataSourceConfig
import logging

logger = logging.getLogger(__name__)


class GeopoliticalDataSource(DataSourceBase, MockDataMixin):
    """
    Handles geopolitical risk data:
    - GAS (Geopolitical Alignment Score) from UNGA voting
    - TFRF (Trade Fragmentation Risk Factor) from MATR data
    - CMDI (Critical Mineral Dependency Index)
    """
    
    def __init__(self, config: DataSourceConfig = None):
        super().__init__()
        self.config = config or DataSourceConfig()
    
    def fetch_data(self, importer_country: str = "USA", supplier_country: str = "China", **kwargs) -> Dict[str, Any]:
        """
        Fetch geopolitical data for country pair
        """
        result = {}
        
        # Fetch GAS from UNGA voting similarity
        gas_score = self._fetch_gas_score(importer_country, supplier_country)
        if gas_score is not None:
            result['gas_score'] = gas_score
        else:
            raise Exception("Failed to fetch GAS score")
        
        # Fetch TFRF from MATR data
        tfrf = self._fetch_tfrf(supplier_country)
        if tfrf is not None:
            result['tfrf_penalty'] = tfrf
        else:
            raise Exception("Failed to fetch TFRF")
        
        # Fetch CMDI for supplier country
        cmdi = self._fetch_cmdi(supplier_country)
        if cmdi is not None:
            result['cmdi'] = cmdi
        else:
            raise Exception("Failed to fetch CMDI")
        
        return result
    
    def _fetch_gas_score(self, country_a: str, country_b: str) -> Optional[float]:
        """
        Fetch Geopolitical Alignment Score based on UNGA voting similarity
        
        Calibration: 10% increase in voting similarity = 0.762% increase in trade flows
        """
        if not self.config.UNGA_VOTING_API_URL:
            return None
        
        try:
            # Example API call structure (adjust based on actual API)
            params = {
                'country_a': country_a,
                'country_b': country_b,
                'year': 'latest'
            }
            
            response = requests.get(
                self.config.UNGA_VOTING_API_URL,
                params=params,
                headers={'Authorization': f'Bearer {self.config.UNGA_API_KEY}'} if self.config.UNGA_API_KEY else {},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Parse voting similarity (0-1 scale)
                voting_similarity = data.get('voting_similarity', 0.5)
                
                # Calibrate to GAS score (0-1 scale)
                # Higher similarity = higher alignment = lower risk
                gas_score = voting_similarity
                
                logger.info(f"Fetched GAS: {country_a}-{country_b} = {gas_score}")
                return gas_score
                
        except Exception as e:
            logger.error(f"Error fetching GAS from API: {e}")
        
        return None
    
    def _fetch_tfrf(self, supplier_country: str) -> Optional[float]:
        """
        Fetch Trade Fragmentation Risk Factor from MATR data
        
        Calibration: One std dev increase in MATR = 31% reduction in trade
        Fragmentation can reduce trade flows by 22%-57% between blocs
        """
        if not self.config.IMF_MATR_API_URL:
            return None
        
        try:
            params = {
                'country': supplier_country,
                'indicator': 'MATR',
                'year': 'latest'
            }
            
            response = requests.get(
                self.config.IMF_MATR_API_URL,
                params=params,
                headers={'Authorization': f'Bearer {self.config.IMF_API_KEY}'} if self.config.IMF_API_KEY else {},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matr_value = data.get('MATR_value', 0)
                
                # Calibrate MATR to TFRF (0-1 scale)
                # Higher MATR = higher fragmentation risk
                # Normalize based on historical max MATR (adjust as needed)
                max_matr = 100  # Example normalization factor
                tfrf = min(matr_value / max_matr, 1.0) * self.config.TFRF_CALIBRATION_FACTOR
                
                logger.info(f"Fetched TFRF for {supplier_country}: {tfrf}")
                return tfrf
                
        except Exception as e:
            logger.error(f"Error fetching TFRF from API: {e}")
        
        return None
    
    def _try_database(self, importer_country: str = "USA", supplier_country: str = "China", **kwargs) -> Optional[Dict[str, Any]]:
        """Try to get all geopolitical data from database files"""
        try:
            db_path = Path(self.config.CRITICAL_MINERALS_DB_PATH)
            if db_path.exists():
                with open(db_path, 'r') as f:
                    minerals_db = json.load(f)
                    
                if supplier_country in minerals_db:
                    country_data = minerals_db[supplier_country]
                    
                    # Return complete geopolitical data from database if available
                    result = {}
                    
                    # CMDI
                    if 'supply_concentration' in country_data:
                        result['cmdi'] = country_data['supply_concentration']
                    
                    # GAS and TFRF if stored in database
                    if 'gas_score' in country_data:
                        result['gas_score'] = country_data['gas_score']
                    if 'tfrf_penalty' in country_data:
                        result['tfrf_penalty'] = country_data['tfrf_penalty']
                    
                    if result:
                        logger.info(f"Loaded geopolitical data from database for {supplier_country}")
                        return result
        except Exception as e:
            logger.error(f"Error loading geopolitical data from database: {e}")
        
        return None
    
    def _fetch_cmdi(self, supplier_country: str) -> Optional[float]:
        """
        Fetch Critical Mineral Dependency Index
        
        Based on supply concentration of key minerals (REEs, lithium, cobalt, etc.)
        """
        # Try database first (preferred)
        try:
            db_path = Path(self.config.CRITICAL_MINERALS_DB_PATH)
            if db_path.exists():
                with open(db_path, 'r') as f:
                    minerals_db = json.load(f)
                    
                if supplier_country in minerals_db:
                    country_data = minerals_db[supplier_country]
                    # Calculate CMDI based on supply concentration
                    # Higher concentration = higher dependency risk
                    cmdi = country_data.get('supply_concentration', 0.5)
                    logger.info(f"Fetched CMDI from DB for {supplier_country}: {cmdi}")
                    return cmdi
        except Exception as e:
            logger.error(f"Error loading CMDI from DB: {e}")
        
        # Try API if available (only if database doesn't have it)
        if self.config.USGS_MINERALS_API_URL and not self.config.PREFER_DATABASES:
            try:
                response = requests.get(
                    self.config.USGS_MINERALS_API_URL,
                    params={'country': supplier_country},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    cmdi = data.get('dependency_index', 0.5)
                    return cmdi
            except Exception as e:
                logger.error(f"Error fetching CMDI from API: {e}")
        
        return None
    
    def get_mock_data(self, importer_country: str = "USA", supplier_country: str = "China", **kwargs) -> Dict[str, Any]:
        """Mock data fallback"""
        self.log_mock_data_usage("GeopoliticalData", "API unavailable")
        
        # Default mock values based on supplier country
        mock_values = {
            "China": {
                "gas_score": 0.20,  # Low alignment with US
                "tfrf_penalty": 0.31,  # High fragmentation risk
                "cmdi": 0.90  # High critical mineral dependency
            },
            "Vietnam": {
                "gas_score": 0.65,  # Higher alignment with US
                "tfrf_penalty": 0.15,  # Lower fragmentation risk
                "cmdi": 0.45  # Moderate dependency
            }
        }
        
        return mock_values.get(supplier_country, mock_values["China"])

