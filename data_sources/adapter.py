"""
Data Adapter
Integrates data sources with decision engines
Provides unified interface for fetching all required metrics
"""

from typing import Dict, Any, Optional
from .geopolitical_data import GeopoliticalDataSource
from .supplier_data import SupplierDataSource
from .logistics_data import LogisticsDataSource
from .economic_data import EconomicDataSource
from .ahp_data import AHPDataSource
from .config import DataSourceConfig
import logging

logger = logging.getLogger(__name__)


class DataAdapter:
    """
    Adapter layer that connects data sources to decision engines
    Handles data fetching, caching, and fallback logic
    """
    
    def __init__(self, config: DataSourceConfig = None):
        self.config = config or DataSourceConfig()
        self.geopolitical = GeopoliticalDataSource(self.config)
        self.supplier = SupplierDataSource(self.config)
        self.logistics = LogisticsDataSource(self.config)
        self.economic = EconomicDataSource(self.config)
        self.ahp = AHPDataSource(self.config)
    
    def get_country_level_supplier_data(self, country: str, importer_country: str = "USA") -> Dict[str, Any]:
        """
        Get country-level supplier data for V2 decision engine
        
        Returns: SupplierData-compatible dictionary
        """
        # Try to get geopolitical data from database first
        geo_data = {}
        try:
            geo_data = self.geopolitical.get_data(
                importer_country=importer_country,
                supplier_country=country
            )
        except Exception:
            # Fallback: try reading directly from critical_minerals.json
            from pathlib import Path
            import json
            minerals_path = Path(self.config.CRITICAL_MINERALS_DB_PATH)
            if minerals_path.exists():
                try:
                    with open(minerals_path, 'r') as f:
                        minerals_db = json.load(f)
                        if country in minerals_db:
                            country_data = minerals_db[country]
                            geo_data = {
                                'gas_score': country_data.get('gas_score'),
                                'tfrf_penalty': country_data.get('tfrf_penalty'),
                                'cmdi': country_data.get('supply_concentration')
                            }
                except Exception as e:
                    import logging
                    logging.warning(f"Error reading critical_minerals.json: {e}")
        
        # Fetch logistics data (default port cluster)
        port_cluster = self._get_default_port_cluster(country)
        logistics_data = self.logistics.get_data(
            port_cluster=port_cluster,
            origin_country=country,
            destination_country=importer_country
        )
        
        # Determine SSP flag (would need supplier lookup for actual data)
        # For now, use country defaults
        ssp_flag = "State-Subsidiary" if country == "China" else "Private"
        
        return {
            "country": country,
            "base_freight_cost": logistics_data.get("base_freight_cost", 0.05),
            "gas_score": geo_data.get("gas_score", 0.5),
            "tfrf_penalty": geo_data.get("tfrf_penalty", 0.2),
            "fvm_multiplier": logistics_data.get("fvm_multiplier", 1.15),
            "ssp_flag": ssp_flag,
            "cm_dependency": geo_data.get("cmdi", geo_data.get("supply_concentration", 0.7)),
            "historical_loss_pct": 0.25 if country == "China" else 0.10,
            "tariffs_percent": 25.0 if country == "China" else 0.0
        }
    
    def get_intra_country_supplier_data(self, supplier_id: str) -> Dict[str, Any]:
        """
        Get firm-level supplier data for intra-country decision engine
        
        Returns: IntraCountrySupplierData-compatible dictionary
        """
        # Fetch supplier profile
        supplier_profile = self.supplier.get_data(supplier_id=supplier_id)
        
        # Fetch economic data for location
        location = supplier_profile.get("location_prefecture")
        location_type = supplier_profile.get("location_type")
        
        economic_data = self.economic.get_data(
            location_prefecture=location,
            location_type=location_type
        )
        
        # Fetch logistics data
        port_cluster = supplier_profile.get("port_cluster", "YRD")
        logistics_data = self.logistics.get_data(
            port_cluster=port_cluster,
            origin_country=supplier_profile.get("country", "China")
        )
        
        # Combine all data
        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier_profile.get("supplier_name", ""),
            "company_type": supplier_profile.get("company_type", "Private"),
            "is_strategic_jewel": supplier_profile.get("is_strategic_jewel", False),
            "location_prefecture": location,
            "location_type": location_type,
            "port_cluster": port_cluster,
            "pcb_revenue_percent": supplier_profile.get("pcb_revenue_percent", 30.0),
            "export_share_western": supplier_profile.get("export_share_western", 0.5),
            "base_price_unit": supplier_profile.get("base_price_unit", 3.5),
            "base_freight_cost": logistics_data.get("base_freight_cost", 0.05),
            "labor_friction_dispersion": economic_data.get("labor_friction_dispersion", 1.0),
            "wealth_efficiency_multiplier": economic_data.get("wealth_efficiency_multiplier", 0.085),
            "migration_vulnerability": economic_data.get("migration_vulnerability", 0.3),
            "port_foreland_vulnerability_score": logistics_data.get("port_foreland_vulnerability_score", 60.0),
            "capacity_deterrence_benefit": 0.50,  # Default, could be calculated
            "roundabout_trade_exposure": 0.25,  # Default, could be calculated from trade data
            "historical_loss_pct": supplier_profile.get("historical_loss_pct", 0.20),
            "tariffs_percent": supplier_profile.get("tariffs_percent", 25.0)
        }
    
    def _get_default_port_cluster(self, country: str) -> str:
        """Get default port cluster for a country"""
        defaults = {
            "China": "YRD",
            "Vietnam": "PRD"  # Approximate, Vietnam has different clusters
        }
        return defaults.get(country, "YRD")
    
    def update_supplier_profile(self, supplier_id: str, data: Dict[str, Any]):
        """Update supplier profile in database"""
        self.supplier.update_supplier(supplier_id, data)
        logger.info(f"Updated supplier profile: {supplier_id}")
    
    def search_suppliers(self, country: str, location: Optional[str] = None) -> list:
        """Search for suppliers by country and location"""
        return self.supplier.search_suppliers(country, location)
    
    def get_ahp_scores(self, supplier_id: str):
        """Get AHP scores for a supplier"""
        return self.ahp.get_ahp_scores_object(supplier_id)

