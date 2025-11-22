# Database-Only Setup Guide

## Overview

The system works perfectly **without any external APIs**. You can use real data by simply updating the database JSON files. This is often easier and more reliable than API integration.

## How It Works

Instead of APIs, you populate these database files with real data:
- `data/supplier_database.json` - Supplier profiles
- `data/labor_friction.json` - LFD scores by prefecture
- `data/economic_geography.json` - Location efficiency data
- `data/port_clusters.json` - Port vulnerability assessments
- `data/critical_minerals.json` - CMDI data by country

The system automatically uses this data when available.

## Quick Start

### 1. Edit Supplier Database

Open `data/supplier_database.json` and add your real suppliers:

```json
{
  "YOUR_SUPPLIER_ID": {
    "supplier_id": "YOUR_SUPPLIER_ID",
    "supplier_name": "Real Company Name",
    "country": "China",
    "company_type": "Private",
    "is_strategic_jewel": false,
    "location_prefecture": "Shenzhen (PRD)",
    "location_type": "Coastal",
    "port_cluster": "PRD",
    "pcb_revenue_percent": 35.0,
    "export_share_western": 0.50,
    "historical_loss_pct": 0.15,
    "base_price_unit": 3.45,
    "base_freight_cost": 0.045,
    "tariffs_percent": 25.0
  }
}
```

### 2. Add Economic Data

Edit `data/labor_friction.json`:

```json
{
  "Shenzhen (PRD)": {
    "lfd_score": 0.85,
    "std_deviation": 0.82,
    "output_friction": 0.09,
    "data_source": "Your Research Source",
    "last_updated": "2024-01-15"
  }
}
```

Edit `data/economic_geography.json`:

```json
{
  "Shenzhen (PRD)": {
    "location_type": "Coastal",
    "region": "Pearl River Delta",
    "wealth_tier": "High",
    "migration_vulnerability": 0.15,
    "productivity_index": 1.20
  }
}
```

### 3. Update Port Data

Edit `data/port_clusters.json`:

```json
{
  "PRD": {
    "port_cluster": "Pearl River Delta",
    "major_ports": ["Shenzhen", "Guangzhou", "Hong Kong"],
    "foreland_vulnerability": 60.0,
    "primary_trade_routes": ["North America", "Southeast Asia"],
    "geopolitical_risk": "Moderate",
    "notes": "Your assessment notes"
  }
}
```

### 4. Add Critical Minerals Data

Edit `data/critical_minerals.json`:

```json
{
  "China": {
    "supply_concentration": 0.90,
    "key_minerals": ["REEs", "Graphite", "Tungsten"],
    "market_share_rare_earth": 0.85,
    "market_share_graphite": 0.75,
    "dependency_risk": "Very High"
  }
}
```

## Using Real Data

Once you've populated the databases, the system automatically uses them:

```python
from data_sources import DataAdapter

adapter = DataAdapter()

# This will use your real database data!
supplier_data = adapter.get_intra_country_supplier_data("YOUR_SUPPLIER_ID")
print(supplier_data['supplier_name'])  # Your real company name
print(supplier_data['labor_friction_dispersion'])  # Real LFD from database
```

## Geopolitical Metrics (Country-Level)

For country-level comparisons (GAS, TFRF, CMDI), you have two options:

### Option 1: Add to Critical Minerals JSON

The CMDI is already loaded from `critical_minerals.json`. For GAS and TFRF, you can add country-level defaults:

Edit `data/critical_minerals.json` to include geopolitical scores:

```json
{
  "China": {
    "supply_concentration": 0.90,
    "gas_score": 0.20,
    "tfrf_penalty": 0.31,
    "key_minerals": ["REEs", "Graphite"]
  },
  "Vietnam": {
    "supply_concentration": 0.45,
    "gas_score": 0.65,
    "tfrf_penalty": 0.15,
    "key_minerals": ["REEs"]
  }
}
```

Then update `data_sources/geopolitical_data.py` to read from this file for GAS/TFRF as well.

### Option 2: Update Mock Data with Real Values

Simply edit the mock data functions in:
- `data_sources/geopolitical_data.py` → `get_mock_data()` method

Replace mock values with your real research-based values.

## Configuration

No API configuration needed! The system is already set to work with databases only.

You can verify this in `data_sources/config.py`:

```python
# All API URLs are None by default - system uses databases/mock
USE_MOCK_DATA_FALLBACK: bool = True  # This ensures it never fails
```

## Benefits of Database-Only Approach

1. **Reliable**: No API downtime or rate limits
2. **Fast**: No network calls needed
3. **Controlled**: You control all data updates
4. **Simple**: Just edit JSON files
5. **Versioned**: Easy to track data changes in git

## Example: Adding a New Supplier

1. Open `data/supplier_database.json`
2. Add your supplier profile
3. Save the file
4. System immediately uses the new data!

```python
# Now you can use it
adapter = DataAdapter()
supplier = adapter.get_intra_country_supplier_data("NEW_SUPPLIER_ID")
# Returns your real data!
```

## Updating Data

Simply edit the JSON files and save. The system will:
1. Load the updated data on next request
2. Cache it for performance
3. Use it automatically

No restarts or configuration changes needed!

## Data Sources for Population

Here are some sources you can use to populate the databases:

### Supplier Data
- Company websites
- Trade directories
- Industry databases
- Your own supplier records

### Labor Friction (LFD)
- Academic research papers
- Economic geography studies
- Regional economic reports

### Port Vulnerability
- Maritime security reports
- Port operations data
- Trade route analysis

### Critical Minerals
- USGS reports
- Industry publications
- Supply chain research

## Next Steps

1. **Start with supplier database**: Add your real suppliers
2. **Add location data**: Populate economic geography
3. **Update port assessments**: Add real port cluster data
4. **Refine over time**: Update as you get better data

The system works immediately - just start populating the files!



