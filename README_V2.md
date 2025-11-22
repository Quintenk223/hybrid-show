# PCB Sourcing Decision Engine V2

Advanced Geopolitical Risk and Financial Modeling for China vs Vietnam Supplier Analysis

## Overview

This is the **second prototype** of the decision engine, focused on implementing sophisticated quantitative risk and financial modeling logic. The engine integrates geopolitical and logistical risk factors into financial calculations to provide actionable sourcing decisions.

## Key Features

### Enhanced Risk Modeling

- **Geopolitical Alignment Score (GAS)**: Measures alignment with importer country (e.g., US)
- **Trade Fragmentation Risk Factor (TFRF)**: Models the impact of trade bloc fragmentation
- **Foreland Volatility Multiplier (FVM)**: Adjusts freight costs based on maritime/port risk
- **Strategic Shielding Potential (SSP)**: Amplifies risk for state-subsidiary suppliers
- **Critical Mineral Dependency Index (CMDI)**: Assesses vulnerability to supply-side targeting

### Financial Calculations

- **Adjusted Price (AP)**: Base price adjusted for trade fragmentation risk
  - `AP = Price_unit × (1 + TFRF_penalty)`
- **Adjusted Freight (AF)**: Freight costs adjusted for maritime volatility
  - `AF = Base Freight Cost × FVM_multiplier`
- **Total Landed Cost (TLC)**: Complete per-unit cost including all adjustments
- **NPV Delta**: Net present value difference between suppliers

### Composite Risk Score

```
Risk Score = (0.4 × GAS_Penalty + 0.3 × FVM_Score + 0.3 × CMDI_Score) × SSP_Multiplier
```

Where:
- **GAS_Penalty** = (1 - GAS_score) × 100 (inverse of alignment)
- **FVM_Score** = (FVM - 1) × 100
- **CMDI_Score** = cm_dependency × 100
- **SSP_Multiplier** = 1.2 if State-Subsidiary, else 1.0

### Weighted Decision Model

```
W_Decision = NPV_Δ - E_Loss
```

Where Expected Loss is calculated as:
```
E_Loss = NPV_China × China_Risk_Score_normalized × Historical_Loss_Pct
```

## Usage

### Basic Usage

```python
from decision_engine import (
    SKUInputs, SupplierData, generate_report, print_report, get_mock_supplier_data
)

# Define SKU inputs
sku_inputs = SKUInputs(
    sku_id="PCB-XYZ-101",
    quantity_po_cycle=50000,
    current_price_unit=3.50,  # China Price ($)
    proposed_price_unit=3.20,  # Vietnam Price ($)
    current_lead_time_days=45,
    proposed_lead_time_days=55,
    importer_country="USA",
    strategic_importance_score=8
)

# Load supplier data
suppliers = get_mock_supplier_data()
china_supplier = suppliers["china"]
vietnam_supplier = suppliers["vietnam"]

# Generate report
report = generate_report(sku_inputs, china_supplier, vietnam_supplier)

# Print report
print_report(report)
```

### Running from Command Line

```bash
python decision_engine.py
```

This will:
1. Run with example SKU data
2. Print a comprehensive formatted report to the console
3. Save the report as JSON to `decision_report.json`

### Customizing Supplier Data

You can customize the supplier data by modifying the `get_mock_supplier_data()` function or passing custom `SupplierData` objects:

```python
custom_china_supplier = SupplierData(
    country="China",
    base_freight_cost=0.05,
    gas_score=0.20,
    tfrf_penalty=0.31,
    fvm_multiplier=1.20,
    ssp_flag="State-Subsidiary",
    cm_dependency=0.90,
    historical_loss_pct=0.25,
    tariffs_percent=25.0
)
```

## Output Structure

The engine generates a comprehensive report dictionary containing:

### 1. Decision Section
- Final recommendation (SWITCH TO VIETNAM or STAY WITH CHINA)
- Weighted decision value
- Recommendation rationale
- Net weighted savings

### 2. Cost Analysis
- NPV Delta (potential savings)
- Total costs for both suppliers
- Detailed cost breakdown showing:
  - Base prices
  - TFRF adjustments
  - Adjusted prices (AP)
  - Freight adjustments (FVM multipliers)
  - Tariffs

### 3. Risk Analysis
- Composite risk scores (0-100 scale) for both suppliers
- Component breakdown (GAS, FVM, CMDI)
- SSP multiplier effects
- Risk delta comparison

### 4. Expected Loss Analysis
- Calculated expected loss if sanctions hit
- Basis of calculation

### 5. Contingency Warnings
- Targeted sanctions vulnerability alerts
- Strategic shielding risk warnings
- Based on high-risk indicators (CMDI > 75%, State-Subsidiary status)

### 6. Strategic Scenarios
- **Deterrence Scenario**: Higher capacity, lower prices (15-20% additional savings)
- **Accommodation Scenario**: Moderate improvements (5-10% savings)

### 7. Legal/Security Questions
- Regulatory exposure questions
- Supply chain security considerations
- Strategic planning inquiries

## Report Format

### Console Output

The `print_report()` function provides a formatted, human-readable output with clear sections and visual separators.

### JSON Output

The report is also saved as structured JSON for programmatic use:

```python
import json

report = generate_report(sku_inputs, china_supplier, vietnam_supplier)
report_json = json.dumps(report, indent=2, default=str)
```

## Example Output

```
================================================================================
DECISION RECOMMENDATION
================================================================================
Recommendation: SWITCH TO VIETNAM
Weighted Decision Value: $46,897.81
Net Weighted Savings: $46,897.81

Financial savings of $103,362 outweigh the expected loss risk of $56,465, 
resulting in a net benefit of $46,898.
```

## Technical Details

### Dependencies

- Python 3.7+
- Standard library only (no external dependencies)

### Key Functions

1. **`calculate_npv_delta()`**: Financial tradeoff calculation with TFRF and FVM adjustments
2. **`calculate_composite_risk()`**: Geopolitical risk score calculation
3. **`calculate_expected_loss()`**: Expected loss from potential sanctions
4. **`generate_recommendation()`**: Weighted decision and scenario generation
5. **`generate_report()`**: Main function that orchestrates all calculations

## Data Validation

The mock supplier data reflects realistic strategic positions:
- **China**: Higher control/fragmentation risk, state-subsidiary status, high CMDI
- **Vietnam**: Lower alignment issues, private company, moderate CMDI

## Next Steps / Future Enhancements

- Real-time API integration for geopolitical data
- Dynamic supplier data lookup
- Historical trend analysis
- Scenario modeling with Monte Carlo simulation
- Multi-supplier comparison
- Integration with procurement systems



