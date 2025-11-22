"""
Data Sources Module
Abstracts data fetching from external APIs and internal databases
"""

from .geopolitical_data import GeopoliticalDataSource
from .supplier_data import SupplierDataSource
from .logistics_data import LogisticsDataSource
from .economic_data import EconomicDataSource
from .adapter import DataAdapter

__all__ = [
    'GeopoliticalDataSource',
    'SupplierDataSource',
    'LogisticsDataSource',
    'EconomicDataSource',
    'DataAdapter'
]

