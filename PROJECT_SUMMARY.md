# PCB Sourcing Decision Engine - Project Summary

## Overview
A comprehensive decision engine for electronics importers to analyze sourcing decisions with advanced geopolitical risk modeling and financial analysis. The system supports both **country-to-country** comparisons (China → Vietnam) and **intra-country** supplier comparisons (China Supplier A ↔ China Supplier B).

---

## Project Structure

### Core Engine Files

#### 1. **decision_engine.py** (V2 - Country-to-Country Comparison)
- **Purpose**: Advanced geopolitical risk modeling for country-level supplier comparisons
- **Key Features**:
  - NPV Delta calculation with TFRF and FVM adjustments
  - Geopolitical Composite Risk Score (GAS, FVM, CMDI, SSP)
  - Weighted Decision Model (W_Decision = NPV_Δ - E_Loss)
  - Expected Loss analysis
  - Strategic scenario modeling (Deterrence vs Accommodation)
  
- **Mock/Demo Data Used**:
  - ✅ Geopolitical Alignment Score (GAS): China (0.20), Vietnam (0.65)
  - ✅ Trade Fragmentation Risk Factor (TFRF): China (0.31), Vietnam (0.15)
  - ✅ Foreland Volatility Multiplier (FVM): China (1.20), Vietnam (1.10)
  - ✅ Critical Mineral Dependency Index (CMDI): China (0.90), Vietnam (0.45)
  - ✅ Strategic Shielding Potential (SSP): State Enterprise flags
  - ✅ Historical loss percentages: China (25%), Vietnam (10%)
  - ✅ Base freight costs and tariff rates

#### 2. **decision_engine_intra_country.py** (Intra-Country Comparison)
- **Purpose**: Firm-level stability analysis for comparing suppliers within the same country
- **Key Features**:
  - Supplier Identity Risk (SSP, Core Product Vulnerability, Embargo Exposure)
  - Operational Stability Analysis (Labor Friction Dispersion, Wealth Efficiency, Migration Vulnerability)
  - Localized Logistics Risk (Port Foreland Vulnerability, Capacity Deterrence, Roundabout Trade)
  - Friction Heatmap visualization
  - Adjusted cost calculations with friction premiums
  
- **Mock/Demo Data Used**:
  - ✅ Supplier A (ChinaTech State Manufacturing):
    - State Enterprise, Strategic Jewel = True
    - Location: Shanghai (YRD), Coastal
    - PCB Revenue %: 45%
    - Export Share Western: 65%
    - LFD: 1.10, Port FVS: 75
  - ✅ Supplier B (Shenzhen Precision Circuits):
    - Private Company, Strategic Jewel = False
    - Location: Shenzhen (PRD), Coastal
    - PCB Revenue %: 25%
    - Export Share Western: 45%
    - LFD: 0.85, Port FVS: 60
  - ✅ Location-based efficiency multipliers (Coastal: 0.085, Inland: 0.108)
  - ✅ Capacity deterrence benefits and roundabout trade exposure

### Web Interface Files

#### 3. **app.py** (Original Flask Backend - V1)
- **Status**: Initial prototype (superseded by V2)
- **Purpose**: Basic country-to-country comparison with simple HTML/CSS/JS

#### 4. **app_v2.py** (Flask Backend - V2)
- **Status**: Standalone V2 interface
- **Purpose**: Web interface for country-to-country comparisons
- **Port**: 5001

#### 5. **app_unified.py** (Unified Interface - Current)
- **Status**: ✅ **ACTIVE - Recommended**
- **Purpose**: Unified web interface supporting both comparison modes
- **Features**:
  - Mode selection (Country-to-Country vs Intra-Country)
  - Dynamic form fields
  - Visual friction heatmap for intra-country mode
  - Comprehensive results display
- **Port**: 5002
- **URL**: http://localhost:5002

#### 6. **index.html** (Standalone HTML - V1)
- **Status**: Legacy standalone version
- **Purpose**: Single-file HTML application (no server required)
- **Note**: Uses simplified calculations, not the advanced V2 logic

### Supporting Files

#### 7. **data/suppliers.json**
- Mock supplier data (used by original V1 interface)
- Contains China and Vietnam supplier records

#### 8. **example_usage.py**
- Example scripts demonstrating engine usage
- Shows different SKU scenarios

#### 9. **README.md** / **README_V2.md**
- Documentation files
- Setup and usage instructions

---

## Feature Summary

### ✅ Implemented Features

#### Financial Analysis
- **NPV Delta Calculation**: Net present value difference between suppliers
- **Adjusted Price (AP)**: Base price × (1 + TFRF penalty)
- **Adjusted Freight (AF)**: Base freight × FVM multiplier
- **Total Landed Cost (TLC)**: Complete per-unit cost including all adjustments
- **Tariff Calculations**: Import duty calculations
- **Efficiency Adjustments**: Wealth-based friction adjustments (intra-country)

#### Risk Modeling

**Country-to-Country Mode:**
1. **Geopolitical Alignment Score (GAS)**: Measures alignment with importer country
2. **Trade Fragmentation Risk Factor (TFRF)**: Models trade bloc fragmentation impact
3. **Foreland Volatility Multiplier (FVM)**: Maritime/port risk adjustments
4. **Critical Mineral Dependency Index (CMDI)**: Supply-side targeting vulnerability
5. **Strategic Shielding Potential (SSP)**: State enterprise risk amplification

**Intra-Country Mode:**
1. **Supplier Identity Risk**: SSP, core product vulnerability, embargo exposure
2. **Operational Stability**: Labor friction dispersion, wealth efficiency, migration vulnerability
3. **Logistics Risk**: Port foreland vulnerability, capacity deterrence, roundabout trade

#### Decision Logic
- **Weighted Decision Model**: W_Decision = NPV_Δ - (Risk Score × E_Loss)
- **Expected Loss Calculation**: Based on risk scores and historical loss data
- **Recommendation Engine**: Switch/Stay recommendations with rationale

#### Output & Insights
- **Decision Recommendations**: Clear Switch/Stay guidance
- **Cost Breakdowns**: Detailed per-unit cost analysis
- **Risk Scores**: Composite risk scores (0-100 scale) with component breakdowns
- **Contingency Warnings**: Targeted alerts for high-risk factors
- **Strategic Scenarios**: Deterrence vs Accommodation analysis (country mode)
- **Friction Heatmap**: Visual comparison of operational frictions (intra-country mode)
- **Legal/Security Questions**: Dynamic question generation for vetting teams

---

## Mock/Demo Data Usage

### All Data Sources Are Currently Mock/Demo

#### Country-Level Supplier Data (China & Vietnam)
- **Source**: Hardcoded in `decision_engine.py` → `get_mock_supplier_data()`
- **Includes**:
  - Geopolitical alignment scores (GAS)
  - Trade fragmentation risk factors (TFRF)
  - Foreland volatility multipliers (FVM)
  - Critical mineral dependency indices (CMDI)
  - Strategic shielding flags
  - Freight costs and tariff rates
  - Historical loss percentages

#### Intra-Country Supplier Data (China Supplier A & B)
- **Source**: Hardcoded in `decision_engine_intra_country.py` → `get_mock_supplier_a()` / `get_mock_supplier_b()`
- **Includes**:
  - Company type and strategic jewel status
  - Location data (prefecture, coastal/inland classification)
  - Port cluster assignments
  - PCB revenue percentages
  - Export share to Western markets
  - Labor friction dispersion (LFD) scores
  - Port foreland vulnerability scores
  - Capacity deterrence benefits
  - Roundabout trade exposure metrics

#### Economic Data
- **Location Efficiency Multipliers**: Coastal (0.085) vs Inland (0.108)
- **LFD Ranges**: Based on academic research (0-2 scale, with 1.18 as high)
- **Historical Loss Percentages**: Based on Russian firm sanction data references

---

## What Needs Real Data Integration

### To Make Production-Ready:

1. **Geopolitical Data APIs**:
   - UNGA voting similarity data (for GAS calculations)
   - MATR (Measure of Aggregate Trade Restrictions) data (for TFRF)
   - Real-time maritime route risk assessments (for FVM)

2. **Supplier Database**:
   - Company type verification
   - Strategic importance classification
   - Actual location/prefecture data
   - Port cluster assignments

3. **Economic Data Sources**:
   - Labor friction dispersion by prefecture/region
   - Wealth/efficiency metrics by location
   - Migration policy impact data

4. **Trade Data**:
   - Actual export share to Western markets
   - Trade finance dependency
   - Roundabout trade pattern detection
   - Port foreland structure analysis

5. **Pricing & Freight Data**:
   - Real-time freight costs
   - Current tariff rates
   - Port fee structures

6. **Historical Incident Data**:
   - Actual sanction impact data
   - Historical loss percentages by firm type
   - Regional disruption patterns

---

## Current Capabilities

### ✅ Fully Functional (with Mock Data)

1. **Financial Calculations**: All NPV, cost, and pricing calculations work correctly
2. **Risk Modeling Algorithms**: All risk score calculations are implemented
3. **Decision Logic**: Weighted decision model fully functional
4. **Web Interface**: Complete UI with mode switching
5. **Data Visualization**: Risk scores, heatmaps, breakdowns all display
6. **Report Generation**: JSON and formatted text outputs

### ⚠️ Requires Real Data

1. **Supplier Lookup**: Currently uses hardcoded supplier profiles
2. **Geopolitical Metrics**: Uses static mock values
3. **Economic Friction Data**: Uses academic research ranges
4. **Historical Loss Data**: Uses general references

---

## Recommended Usage

### For Development/Testing:
- Use **app_unified.py** (port 5002) - This is the most complete interface
- All calculations work with mock data
- Perfect for testing logic and UI

### For Production:
- Replace mock data functions with real API calls
- Integrate with supplier databases
- Add real-time geopolitical data feeds
- Connect to trade data sources

---

## File Status Summary

| File | Status | Purpose | Uses Mock Data |
|------|--------|---------|----------------|
| `decision_engine.py` | ✅ Active | V2 Country-to-Country Engine | ✅ Yes (all supplier metrics) |
| `decision_engine_intra_country.py` | ✅ Active | Intra-Country Comparison Engine | ✅ Yes (all supplier data) |
| `app_unified.py` | ✅ **RECOMMENDED** | Unified Web Interface | ✅ Yes (via engines) |
| `app_v2.py` | ⚠️ Legacy | V2-only interface | ✅ Yes |
| `app.py` | ⚠️ Legacy | V1 prototype | ✅ Yes |
| `index.html` | ⚠️ Legacy | Standalone HTML (V1) | ✅ Yes (embedded) |
| `example_usage.py` | ✅ Helper | Usage examples | ✅ Yes |
| `data/suppliers.json` | ⚠️ Legacy | V1 supplier data | ✅ Yes |

---

## Next Steps for Production

1. **Data Integration Layer**: Create abstraction layer for data sources
2. **API Integration**: Connect to geopolitical and trade data APIs
3. **Supplier Database**: Build/connect to supplier information database
4. **Real-time Updates**: Implement data refresh mechanisms
5. **Validation**: Add data validation and error handling for missing data
6. **Caching**: Implement caching for expensive data lookups
7. **Audit Logging**: Track data sources and calculation provenance

---

## Summary

**What You Have:**
- ✅ Complete decision engine with advanced risk modeling
- ✅ Two comparison modes (Country-to-Country and Intra-Country)
- ✅ Fully functional web interface
- ✅ All calculation logic implemented and tested

**What Uses Demo Data:**
- ⚠️ **ALL** geopolitical metrics (GAS, TFRF, FVM, CMDI, SSP)
- ⚠️ **ALL** supplier profiles and company data
- ⚠️ **ALL** economic friction and location data
- ⚠️ **ALL** freight costs, tariffs, and pricing adjustments

**What Works:**
- ✅ All financial calculations
- ✅ All risk score algorithms
- ✅ All decision logic
- ✅ Complete UI and visualization

The system is **functionally complete** with **mock data throughout**. To make it production-ready, you would replace the mock data sources with real API integrations and databases.



