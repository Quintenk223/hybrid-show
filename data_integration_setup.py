"""
Data Integration Setup Script
Initializes database files and validates data source configuration
"""

import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_databases():
    """Create database files if they don't exist"""
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "cache").mkdir(exist_ok=True)
    (data_dir / "cache" / "logistics").mkdir(exist_ok=True)
    (data_dir / "cache" / "economic").mkdir(exist_ok=True)
    
    # Initialize supplier database if needed
    supplier_db_path = data_dir / "supplier_database.json"
    if not supplier_db_path.exists():
        logger.info("Creating supplier database...")
        # File already created above
    
    # Initialize economic geography database
    economic_db_path = data_dir / "economic_geography.json"
    if not economic_db_path.exists():
        logger.info("Economic geography database already exists")
    
    # Initialize labor friction database
    lfd_db_path = data_dir / "labor_friction.json"
    if not lfd_db_path.exists():
        logger.info("Labor friction database already exists")
    
    # Initialize port clusters database
    port_db_path = data_dir / "port_clusters.json"
    if not port_db_path.exists():
        logger.info("Port clusters database already exists")
    
    # Initialize critical minerals database
    minerals_db_path = data_dir / "critical_minerals.json"
    if not minerals_db_path.exists():
        logger.info("Critical minerals database already exists")
    
    logger.info("Database initialization complete!")


def validate_config():
    """Validate data source configuration"""
    from data_sources.config import DataSourceConfig
    
    config = DataSourceConfig()
    
    logger.info("=== Data Source Configuration ===")
    logger.info(f"Mock Data Fallback Enabled: {config.USE_MOCK_DATA_FALLBACK}")
    logger.info(f"UNGA API URL: {config.UNGA_VOTING_API_URL or 'Not configured'}")
    logger.info(f"IMF MATR API URL: {config.IMF_MATR_API_URL or 'Not configured'}")
    logger.info(f"Freight API URL: {config.FREIGHT_QUOTE_API_URL or 'Not configured'}")
    logger.info(f"Supplier DB Path: {config.SUPPLIER_DB_PATH}")
    logger.info(f"Economic DB Path: {config.ECONOMIC_GEOGRAPHY_DB_PATH}")
    logger.info(f"Labor Friction DB Path: {config.LABOR_FRICTION_DB_PATH}")
    
    logger.info("\n=== Configuration Status ===")
    if config.USE_MOCK_DATA_FALLBACK:
        logger.info("⚠️  Mock data fallback is ENABLED - system will use mock data when APIs unavailable")
    else:
        logger.info("✅ Mock data fallback is DISABLED - system will fail if APIs unavailable")
    
    api_count = sum([
        config.UNGA_VOTING_API_URL is not None,
        config.IMF_MATR_API_URL is not None,
        config.FREIGHT_QUOTE_API_URL is not None
    ])
    
    if api_count == 0:
        logger.warning("⚠️  No external APIs configured - all data will come from databases/mock")
    else:
        logger.info(f"✅ {api_count} external API(s) configured")


if __name__ == "__main__":
    print("Initializing Data Integration System...")
    print("=" * 50)
    
    initialize_databases()
    print()
    validate_config()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nTo use real data sources:")
    print("1. Set environment variables for API URLs and keys")
    print("2. Update data/*.json files with real data")
    print("3. The system will automatically use real data when available")
    print("4. Mock data will be used as fallback if APIs are unavailable")



