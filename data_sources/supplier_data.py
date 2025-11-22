"""
Supplier Data Source
Manages supplier profiles and company data
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base import DataSourceBase, MockDataMixin
from .config import DataSourceConfig
import logging

logger = logging.getLogger(__name__)


class SupplierDataSource(DataSourceBase, MockDataMixin):
    """
    Handles supplier-specific data:
    - Company type and SSP status
    - Location and port cluster
    - Export share and revenue breakdown
    - Historical performance data
    """
    
    def __init__(self, config: DataSourceConfig = None):
        super().__init__()
        self.config = config or DataSourceConfig()
        self.supplier_db: Dict[str, Any] = {}
        self._load_database()
    
    def _load_database(self):
        """Load supplier database from file"""
        db_path = Path(self.config.SUPPLIER_DB_PATH)
        if db_path.exists():
            try:
                with open(db_path, 'r') as f:
                    self.supplier_db = json.load(f)
                logger.info(f"Loaded supplier database from {db_path}")
            except Exception as e:
                logger.error(f"Error loading supplier database: {e}")
        else:
            logger.warning(f"Supplier database not found at {db_path}, using mock data only")
    
    def fetch_data(self, supplier_id: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch supplier data by ID
        """
        if supplier_id in self.supplier_db:
            supplier_data = self.supplier_db[supplier_id]
            
            # Validate required fields
            required_fields = ['company_type', 'location_prefecture', 'port_cluster']
            if all(field in supplier_data for field in required_fields):
                logger.info(f"Found supplier data for {supplier_id}")
                return supplier_data
            else:
                logger.warning(f"Supplier {supplier_id} missing required fields")
                raise Exception(f"Invalid supplier data for {supplier_id}")
        else:
            raise Exception(f"Supplier {supplier_id} not found in database")
    
    def search_suppliers(self, country: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for suppliers by country and optionally location"""
        results = []
        for supplier_id, supplier_data in self.supplier_db.items():
            if supplier_data.get('country') == country:
                if location is None or supplier_data.get('location_prefecture') == location:
                    results.append({
                        'supplier_id': supplier_id,
                        **supplier_data
                    })
        return results
    
    def update_supplier(self, supplier_id: str, data: Dict[str, Any]):
        """Update or add supplier data"""
        self.supplier_db[supplier_id] = data
        self._save_database()
    
    def _save_database(self):
        """Save supplier database to file"""
        db_path = Path(self.config.SUPPLIER_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(db_path, 'w') as f:
                json.dump(self.supplier_db, f, indent=2)
            logger.info(f"Saved supplier database to {db_path}")
        except Exception as e:
            logger.error(f"Error saving supplier database: {e}")
    
    def get_mock_data(self, supplier_id: str = "CHINA_SUPPLIER_A", **kwargs) -> Dict[str, Any]:
        """Mock data fallback"""
        self.log_mock_data_usage("SupplierData", "Supplier not in database")
        
        mock_suppliers = {
            "CHINA_SUPPLIER_A": {
                "supplier_id": "CHINA_SUPPLIER_A",
                "supplier_name": "ChinaTech State Manufacturing",
                "country": "China",
                "company_type": "State Enterprise",
                "is_strategic_jewel": True,
                "location_prefecture": "Shanghai (YRD)",
                "location_type": "Coastal",
                "port_cluster": "YRD",
                "pcb_revenue_percent": 45.0,
                "export_share_western": 0.65,
                "historical_loss_pct": 0.25
            },
            "CHINA_SUPPLIER_B": {
                "supplier_id": "CHINA_SUPPLIER_B",
                "supplier_name": "Shenzhen Precision Circuits",
                "country": "China",
                "company_type": "Private",
                "is_strategic_jewel": False,
                "location_prefecture": "Shenzhen (PRD)",
                "location_type": "Coastal",
                "port_cluster": "PRD",
                "pcb_revenue_percent": 25.0,
                "export_share_western": 0.45,
                "historical_loss_pct": 0.15
            }
        }
        
        return mock_suppliers.get(supplier_id, mock_suppliers["CHINA_SUPPLIER_A"])



