"""
Logistics Data Source
Fetches freight costs, port data, and maritime risk metrics
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from .base import DataSourceBase, MockDataMixin
from .config import DataSourceConfig
import logging

logger = logging.getLogger(__name__)


class LogisticsDataSource(DataSourceBase, MockDataMixin):
    """
    Handles logistics data:
    - Foreland Volatility Multiplier (FVM)
    - Port Foreland Vulnerability Scores
    - Real-time freight costs
    - Maritime route disruptions
    """
    
    def __init__(self, config: DataSourceConfig = None):
        super().__init__(cache_dir="data/cache/logistics", use_cache=True)
        self.config = config or DataSourceConfig()
    
    def _get_cache_ttl(self) -> int:
        return self.config.LOGISTICS_REFRESH_INTERVAL
    
    def fetch_data(self, port_cluster: str, origin_country: str, destination_country: str = "USA", **kwargs) -> Dict[str, Any]:
        """
        Fetch logistics data for port cluster and route
        """
        result = {}
        
        # Fetch FVM
        fvm = self._fetch_fvm(port_cluster, origin_country, destination_country)
        if fvm is not None:
            result['fvm_multiplier'] = fvm
        else:
            raise Exception("Failed to fetch FVM")
        
        # Fetch Port Foreland Vulnerability Score
        port_fvs = self._fetch_port_foreland_vulnerability(port_cluster)
        if port_fvs is not None:
            result['port_foreland_vulnerability_score'] = port_fvs
        else:
            raise Exception("Failed to fetch port FVS")
        
        # Fetch base freight cost
        freight_cost = self._fetch_freight_cost(origin_country, destination_country)
        if freight_cost is not None:
            result['base_freight_cost'] = freight_cost
        else:
            raise Exception("Failed to fetch freight cost")
        
        return result
    
    def _fetch_fvm(self, port_cluster: str, origin_country: str, destination_country: str) -> Optional[float]:
        """
        Fetch Foreland Volatility Multiplier
        
        Based on AIS data, geopolitical events, and maritime route stability
        """
        if not self.config.AIS_DATA_API_URL:
            return None
        
        try:
            params = {
                'port_cluster': port_cluster,
                'origin': origin_country,
                'destination': destination_country
            }
            
            response = requests.get(
                self.config.AIS_DATA_API_URL,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Calculate FVM from route volatility metrics
                route_stability = data.get('route_stability', 0.8)
                disruption_level = data.get('disruption_level', 0.2)
                
                # FVM = 1.0 + disruption_adjustment
                # Higher disruption = higher FVM multiplier
                fvm = 1.0 + (disruption_level * 0.5)  # Max 1.5x multiplier
                
                logger.info(f"Fetched FVM for {port_cluster}: {fvm}")
                return fvm
                
        except Exception as e:
            logger.error(f"Error fetching FVM from API: {e}")
        
        return None
    
    def _fetch_port_foreland_vulnerability(self, port_cluster: str) -> Optional[float]:
        """
        Fetch Port Foreland Vulnerability Score (0-100)
        
        Based on geopolitical events affecting port foreland expansion
        """
        # Try to load from port data API or database
        port_data_path = Path('data/port_clusters.json')
        if port_data_path.exists():
            try:
                with open(port_data_path, 'r') as f:
                    port_data = json.load(f)
                
                if port_cluster in port_data:
                    fvs = port_data[port_cluster].get('foreland_vulnerability', 50.0)
                    logger.info(f"Fetched port FVS for {port_cluster}: {fvs}")
                    return fvs
            except Exception as e:
                logger.error(f"Error loading port FVS: {e}")
        
        return None
    
    def _fetch_freight_cost(self, origin_country: str, destination_country: str) -> Optional[float]:
        """
        Fetch real-time freight cost per unit
        
        Uses freight quote APIs or historical data
        """
        if self.config.FREIGHT_QUOTE_API_URL:
            try:
                params = {
                    'origin': origin_country,
                    'destination': destination_country,
                    'mode': 'sea'  # or 'air'
                }
                
                response = requests.get(
                    self.config.FREIGHT_QUOTE_API_URL,
                    params=params,
                    headers={'Authorization': f'Bearer {self.config.FREIGHT_API_KEY}'} if self.config.FREIGHT_API_KEY else {},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    freight_cost = data.get('cost_per_unit', 0.05)
                    logger.info(f"Fetched freight cost {origin_country}->{destination_country}: ${freight_cost}")
                    return freight_cost
                    
            except Exception as e:
                logger.error(f"Error fetching freight cost from API: {e}")
        
        return None
    
    def get_mock_data(self, port_cluster: str = "YRD", origin_country: str = "China", **kwargs) -> Dict[str, Any]:
        """Mock data fallback"""
        self.log_mock_data_usage("LogisticsData", "API unavailable")
        
        mock_data = {
            "YRD": {
                "fvm_multiplier": 1.20,
                "port_foreland_vulnerability_score": 75.0,
                "base_freight_cost": 0.05
            },
            "PRD": {
                "fvm_multiplier": 1.15,
                "port_foreland_vulnerability_score": 60.0,
                "base_freight_cost": 0.04
            },
            "Bohai Rim": {
                "fvm_multiplier": 1.25,
                "port_foreland_vulnerability_score": 80.0,
                "base_freight_cost": 0.06
            }
        }
        
        return mock_data.get(port_cluster, mock_data["YRD"])

