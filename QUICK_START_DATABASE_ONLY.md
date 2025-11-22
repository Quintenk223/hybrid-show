# Quick Start: Database-Only Mode

## You're All Set! ✅

The system is already configured to work **entirely with database files** - no APIs needed.

## How It Works

1. **Edit JSON files** in the `data/` folder with your real data
2. **System automatically uses** the database data
3. **No configuration needed** - it's already set up this way!

## Files to Edit

### 1. Supplier Database
**File**: `data/supplier_database.json`

Add your real suppliers here. Example:
```json
{
  "SUPPLIER_ABC": {
    "supplier_id": "SUPPLIER_ABC",
    "supplier_name": "Real Company Name",
    "country": "China",
    "company_type": "Private",
    "location_prefecture": "Shenzhen (PRD)",
    "port_cluster": "PRD",
    "pcb_revenue_percent": 30.0,
    "export_share_western": 0.45
  }
}
```

### 2. Economic Geography
**File**: `data/economic_geography.json`

Add location data:
```json
{
  "Shenzhen (PRD)": {
    "location_type": "Coastal",
    "migration_vulnerability": 0.15
  }
}
```

### 3. Labor Friction
**File**: `data/labor_friction.json`

Add LFD scores:
```json
{
  "Shenzhen (PRD)": {
    "lfd_score": 0.85,
    "std_deviation": 0.82
  }
}
```

### 4. Port Clusters
**File**: `data/port_clusters.json`

Add port assessments:
```json
{
  "PRD": {
    "foreland_vulnerability": 60.0,
    "geopolitical_risk": "Moderate"
  }
}
```

### 5. Critical Minerals & Geopolitical Scores
**File**: `data/critical_minerals.json`

Add country-level metrics:
```json
{
  "China": {
    "supply_concentration": 0.90,
    "gas_score": 0.20,
    "tfrf_penalty": 0.31
  }
}
```

## Using Your Data

Once you've edited the files, the system automatically uses them:

```python
from data_sources import DataAdapter

adapter = DataAdapter()

# Uses your database data automatically!
supplier = adapter.get_intra_country_supplier_data("SUPPLIER_ABC")
country_data = adapter.get_country_level_supplier_data("China")
```

## That's It!

- ✅ No API keys needed
- ✅ No environment variables
- ✅ Just edit JSON files
- ✅ System uses them automatically

See `DATABASE_ONLY_SETUP.md` for detailed examples.



