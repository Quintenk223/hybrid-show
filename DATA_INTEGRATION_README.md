# Data Integration Architecture

## Overview

This module provides a complete data integration system for replacing mock data with real, verifiable sources. The architecture is designed for **gradual migration** - the system continues to work with mock data while you integrate real APIs and databases.

## Architecture

```
data_sources/
├── __init__.py          # Module exports
├── config.py            # Configuration (API URLs, keys, paths)
├── base.py              # Base classes with caching and fallback
├── geopolitical_data.py # GAS, TFRF, CMDI data sources
├── supplier_data.py     # Supplier profiles and company data
├── logistics_data.py    # FVM, port data, freight costs
├── economic_data.py     # LFD, location efficiency, migration risk
└── adapter.py           # Unified interface for decision engines

data/
├── supplier_database.json      # Supplier profiles
├── economic_geography.json     # Location efficiency data
├── labor_friction.json         # LFD scores by prefecture
├── port_clusters.json          # Port vulnerability data
├── critical_minerals.json      # CMDI data
└── cache/                      # API response caching
```

## Data Sources

### 1. Geopolitical Data (`geopolitical_data.py`)

**Metrics:**
- **GAS (Geopolitical Alignment Score)**: From UNGA voting similarity
- **TFRF (Trade Fragmentation Risk Factor)**: From IMF MATR data
- **CMDI (Critical Mineral Dependency Index)**: From critical minerals database

**API Targets:**
- UNGA Voting API (voting similarity indices)
- IMF MATR API (Measure of Aggregate Trade Restrictions)
- USGS Minerals API or internal database

**Calibration:**
- GAS: 10% voting similarity increase = 0.762% trade flow increase
- TFRF: One std dev MATR increase = 31% trade reduction

### 2. Supplier Data (`supplier_data.py`)

**Data Sources:**
- Internal supplier database (JSON file)
- Future: Supplier information APIs, company databases

**Fields:**
- Company type (State Enterprise/Private)
- Strategic jewel status
- Location and port cluster
- PCB revenue percentage
- Export share to Western markets
- Historical loss percentages

### 3. Logistics Data (`logistics_data.py`)

**Metrics:**
- **FVM (Foreland Volatility Multiplier)**: Maritime route volatility
- **Port Foreland Vulnerability Score**: Port cluster risk
- **Freight Costs**: Real-time or historical freight quotes

**API Targets:**
- AIS trajectory data APIs
- Freight quote APIs (Sea/Air)
- Port operations APIs

**Calibration:**
- FVM adjusts based on geopolitical events (e.g., Suez Canal disruptions)

### 4. Economic Data (`economic_data.py`)

**Metrics:**
- **LFD (Labor Friction Dispersion)**: By prefecture/region
- **Location Efficiency Multipliers**: Coastal (0.085) vs Inland (0.108)
- **Migration Vulnerability**: Regional labor outflow risk

**Data Sources:**
- Labor friction database (JSON)
- Economic geography database (JSON)
- Future: Economic research APIs, regional data sources

**Calibration:**
- LFD is substantially higher (avg 1.18) than output frictions (0.11)
- Coastal prefectures show less friction dispersion

## Usage

### Basic Usage with Mock Data (Current State)

```python
from data_sources import DataAdapter

adapter = DataAdapter()

# Get country-level supplier data (automatically uses mock if APIs unavailable)
china_data = adapter.get_country_level_supplier_data("China", "USA")
print(china_data)  # Returns SupplierData-compatible dict

# Get firm-level supplier data
supplier_data = adapter.get_intra_country_supplier_data("CHINA_SUPPLIER_A")
print(supplier_data)  # Returns IntraCountrySupplierData-compatible dict
```

### Integration with Decision Engines

The adapter provides methods that return data in the exact format expected by the decision engines:

```python
from data_sources import DataAdapter
from decision_engine import SKUInputs, SupplierData
from decision_engine_intra_country import IntraCountrySupplierData

adapter = DataAdapter()

# For country-to-country comparison
china_dict = adapter.get_country_level_supplier_data("China")
vietnam_dict = adapter.get_country_level_supplier_data("Vietnam")

# Convert to SupplierData objects
china_supplier = SupplierData(**china_dict)
vietnam_supplier = SupplierData(**vietnam_dict)

# Use with decision engine
from decision_engine import generate_report
sku = SKUInputs(...)
report = generate_report(sku, china_supplier, vietnam_supplier)
```

### Setting Up Real Data Sources

#### 1. Configure API URLs and Keys

Set environment variables:

```bash
export UNGA_VOTING_API_URL="https://api.example.com/unga/voting"
export UNGA_API_KEY="your_api_key_here"
export IMF_MATR_API_URL="https://api.imf.org/matr"
export IMF_API_KEY="your_imf_key_here"
export FREIGHT_QUOTE_API_URL="https://api.freight.com/quotes"
export FREIGHT_API_KEY="your_freight_key_here"
```

Or edit `data_sources/config.py` directly (not recommended for production).

#### 2. Update Database Files

**Supplier Database** (`data/supplier_database.json`):
```json
{
  "SUPPLIER_ID": {
    "supplier_id": "SUPPLIER_ID",
    "supplier_name": "Company Name",
    "country": "China",
    "company_type": "Private",
    "is_strategic_jewel": false,
    "location_prefecture": "Shenzhen (PRD)",
    "location_type": "Coastal",
    "port_cluster": "PRD",
    "pcb_revenue_percent": 30.0,
    "export_share_western": 0.45,
    "historical_loss_pct": 0.15
  }
}
```

**Labor Friction Database** (`data/labor_friction.json`):
```json
{
  "Shanghai (YRD)": {
    "lfd_score": 1.10,
    "std_deviation": 1.08,
    "output_friction": 0.10,
    "data_source": "Research Paper X",
    "last_updated": "2024-01-01"
  }
}
```

#### 3. Enable Data Sources

The system automatically:
1. Tries to fetch from APIs/databases
2. Falls back to mock data if unavailable
3. Caches API responses for performance

To disable mock data fallback (stricter mode):
```python
from data_sources.config import DataSourceConfig
config = DataSourceConfig()
config.USE_MOCK_DATA_FALLBACK = False
```

## Data Flow

```
Decision Engine Request
    ↓
Data Adapter
    ↓
├── Geopolitical Data Source
│   ├── Try API (UNGA, IMF)
│   ├── Try Database
│   └── Fallback to Mock
│
├── Supplier Data Source
│   ├── Try Database
│   └── Fallback to Mock
│
├── Logistics Data Source
│   ├── Try API (Freight, AIS)
│   ├── Try Database
│   └── Fallback to Mock
│
└── Economic Data Source
    ├── Try Database
    └── Fallback to Mock
    ↓
Combined Data Returned to Decision Engine
```

## Caching

All data sources implement caching:
- API responses cached to `data/cache/`
- Cache TTL configurable per source
- Geopolitical: 24 hours
- Logistics: 1 hour
- Economic: 1 week

## Validation and Calibration

### Geopolitical Metrics

**GAS Calibration:**
```python
# Voting similarity → GAS score
# 10% increase in voting similarity = 0.762% increase in trade flows
gas_score = voting_similarity  # Direct mapping (0-1 scale)
```

**TFRF Calibration:**
```python
# MATR value → TFRF penalty
# One std dev MATR increase = 31% trade reduction
tfrf = (matr_value / max_matr) * 0.31
```

### Economic Metrics

**LFD Validation:**
- Labor friction dispersion (avg 1.18) >> output frictions (0.11)
- Higher LFD = greater payroll volatility

**Efficiency Multipliers:**
- Coastal: 0.085 friction
- Inland: 0.108 friction
- Based on empirical research

## Next Steps for Production

### Phase 1: Database Population
1. Populate `supplier_database.json` with real supplier profiles
2. Add real location data to `economic_geography.json`
3. Import LFD scores from research data
4. Update port cluster data with real vulnerability assessments

### Phase 2: API Integration
1. Integrate UNGA voting API (or build internal database)
2. Connect to IMF MATR data feed
3. Set up freight quote API integration
4. Add AIS/maritime data feeds

### Phase 3: Real-Time Updates
1. Implement scheduled data refresh jobs
2. Add data validation and anomaly detection
3. Create data quality monitoring
4. Build data provenance tracking

### Phase 4: Advanced Features
1. Historical trend analysis
2. Predictive modeling for risk scores
3. Multi-source data fusion
4. Machine learning for data calibration

## Testing

Test with mock data:
```python
from data_sources import DataAdapter

adapter = DataAdapter()
# Automatically uses mock data
data = adapter.get_country_level_supplier_data("China")
assert data['gas_score'] == 0.20  # Mock value
```

Test with real data (when APIs available):
```python
# Set environment variables or config
# System automatically uses real data if available
data = adapter.get_country_level_supplier_data("China")
# Real data will be returned if API accessible
```

## Error Handling

The system gracefully handles:
- API timeouts → Falls back to cache or mock
- Missing API keys → Falls back to mock
- Invalid API responses → Falls back to mock
- Database file errors → Falls back to mock

All fallbacks are logged for monitoring.

## Configuration Reference

See `data_sources/config.py` for all configuration options:
- API URLs and keys
- Database paths
- Cache TTL values
- Calibration parameters
- Fallback settings



