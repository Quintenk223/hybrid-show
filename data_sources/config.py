"""
Configuration for data sources
Store API keys and endpoints here (use environment variables in production)
"""

import os
from typing import Optional

class DataSourceConfig:
    """Configuration for all data sources"""
    
    # Geopolitical Data APIs
    UNGA_VOTING_API_URL: Optional[str] = os.getenv('UNGA_VOTING_API_URL', None)
    IMF_MATR_API_URL: Optional[str] = os.getenv('IMF_MATR_API_URL', None)
    WTO_TRADE_API_URL: Optional[str] = os.getenv('WTO_TRADE_API_URL', None)
    
    # Critical Minerals Data
    CRITICAL_MINERALS_DB_PATH: str = os.getenv('CRITICAL_MINERALS_DB_PATH', 'data/critical_minerals.json')
    USGS_MINERALS_API_URL: Optional[str] = os.getenv('USGS_MINERALS_API_URL', None)
    
    # Logistics Data
    AIS_DATA_API_URL: Optional[str] = os.getenv('AIS_DATA_API_URL', None)
    FREIGHT_QUOTE_API_URL: Optional[str] = os.getenv('FREIGHT_QUOTE_API_URL', None)
    PORT_DATA_API_URL: Optional[str] = os.getenv('PORT_DATA_API_URL', None)
    
    # Economic Data
    LABOR_FRICTION_DB_PATH: str = os.getenv('LABOR_FRICTION_DB_PATH', 'data/labor_friction.json')
    ECONOMIC_GEOGRAPHY_DB_PATH: str = os.getenv('ECONOMIC_GEOGRAPHY_DB_PATH', 'data/economic_geography.json')
    
    # Internal Database
    SUPPLIER_DB_PATH: str = os.getenv('SUPPLIER_DB_PATH', 'data/supplier_database.json')
    
    # API Keys (use environment variables!)
    UNGA_API_KEY: Optional[str] = os.getenv('UNGA_API_KEY', None)
    IMF_API_KEY: Optional[str] = os.getenv('IMF_API_KEY', None)
    FREIGHT_API_KEY: Optional[str] = os.getenv('FREIGHT_API_KEY', None)
    
    # Data refresh intervals (seconds)
    GEOPOLITICAL_REFRESH_INTERVAL: int = 86400  # 24 hours
    LOGISTICS_REFRESH_INTERVAL: int = 3600  # 1 hour
    ECONOMIC_REFRESH_INTERVAL: int = 604800  # 1 week
    
    # Fallback to mock data if APIs unavailable
    # Set to False only if you want strict API-only mode (not recommended)
    USE_MOCK_DATA_FALLBACK: bool = os.getenv('USE_MOCK_DATA_FALLBACK', 'true').lower() == 'true'
    
    # Database-first mode: prefer databases over APIs (good for database-only setup)
    PREFER_DATABASES: bool = os.getenv('PREFER_DATABASES', 'true').lower() == 'true'
    
    # Calibration parameters
    TFRF_CALIBRATION_FACTOR: float = 0.31  # One std dev MATR = 31% trade reduction
    GAS_TRADE_FLOW_COEFFICIENT: float = 0.0762  # 10% voting similarity = 0.762% trade flow increase

