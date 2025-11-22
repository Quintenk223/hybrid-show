# AHP Integration Summary

## Overview

The AHP (Analytic Hierarchy Process) integration has been successfully implemented on the `feature/ahp-integration` branch. This enhancement fundamentally shifts the decision engine from price arbitrage to **productivity-driven strategic sourcing**, reflecting industry expert consensus that Purchasing Costs (0.032) are the least important factor in PCB equipment procurement.

## Key Implementations

### 1. AHP Criteria Framework (`ahp_criteria.py`)

**12 AHP Criteria with Global Weights:**
- **Line and Space** (0.182) - Highest weight - Manufacturing Requirements
- **Automatic Ops** (0.171) - Equipment Specifications
- **Mark Alignment Correction** (0.137) - Manufacturing Requirements
- **Process Speed** (0.112) - Manufacturing Requirements
- **Maintenance Cost** (0.062) - Procurement Concerns
- **Dual Stage** (0.057) - Equipment Specifications
- **Compatible Register** (0.057) - Equipment Specifications
- **Throughput** (0.054) - Manufacturing Requirements
- **DF and SR in One** (0.054) - Equipment Specifications
- **Part Durability** (0.046) - Procurement Concerns
- **Warranty** (0.036) - Procurement Concerns
- **Purchasing Costs** (0.032) - **Lowest weight** - Procurement Concerns

**Category Weights:**
- Manufacturing Requirements: **0.545** (Most important)
- Equipment Specifications: 0.279
- Procurement Concerns: 0.176

### 2. Technical Viability Score Calculation

**Formula:** `V = Σ(W_i × S_i)`

Where:
- `V` = Technical Viability Score (0-1 scale)
- `W_i` = Global Weight of criterion i
- `S_i` = Normalized score (0-1) for criterion i

The score is calculated for each supplier and integrated into risk assessment.

### 3. AHP-Integrated Decision Engine (`decision_engine_ahp_integrated.py`)

**Key Features:**

#### A. Strategic Importance Score Adjustment
- Dynamic adjustment based on critical technical criteria (Line and Space, Mark Alignment Correction)
- Suppliers failing on critical capabilities cannot receive high SIS
- High technical capability can increase SIS (up to 10)

#### B. Yield Risk Penalty
- Low scores on Line and Space and Mark Alignment Correction trigger financial penalty multipliers
- Represents cost of potential scrap and yield loss
- **Principle:** Cheap, low-precision machines are riskier

#### C. Long-Term Cost Modeling
- Incorporates Maintenance Cost (0.062), Part Durability (0.046), and Warranty (0.036)
- Feeds into multi-year NPV Delta calculation
- Provides comprehensive Total Ownership Cost assessment

#### D. Automation-Adjusted LFD
- Higher Automatic Ops score reduces Labor Friction Dispersion (LFD) risk
- Reflects goal to reduce reliance on labor-intensive manufacturing
- Max 30% reduction in LFD based on automation level

#### E. Decision Override Logic
- **Minimum Technical Viability Threshold:** 50%
- If proposed supplier scores below threshold, generates "NO SWITCH" recommendation
- Technical risk explicitly overrides price benefits
- Message: "Technical risk outweighs cost benefit. PCB industry prioritizes Manufacturing Requirements (0.545) and Equipment Specifications (0.279) over Purchasing Costs (0.032)."

#### F. Combined Risk Score
- Integrates geopolitical risk (40%) and technical risk (60%)
- Technical Viability Score inverted: high V = low technical risk
- Provides unified risk assessment

### 4. Data Integration

**AHP Data Source (`data_sources/ahp_data.py`):**
- Database-first approach: Reads from `data/ahp_scores.json`
- Automatic fallback to mock data
- Integrated into DataAdapter for unified data access

**Database Structure (`data/ahp_scores.json`):**
- Pre-populated scores for CHINA_ALPHA, CHINA_BETA, VIETNAM_GAMMA
- Each supplier has 12 AHP criterion scores (0-1 scale)
- Includes notes explaining supplier characteristics

**Example Scores:**
- **CHINA_ALPHA:** High precision (Line & Space: 0.75, Alignment: 0.80) but higher purchasing costs (0.30)
- **CHINA_BETA:** Lower price (0.75) but moderate technical capability (Line & Space: 0.55, Alignment: 0.50) - **yield risk**
- **VIETNAM_GAMMA:** Strong automation (0.75), good technical capabilities, competitive pricing

### 5. Integration with Existing Models

**AHP adjustments are applied to:**
- NPV Delta calculations (yield penalties, long-term cost multipliers)
- Labor Friction Dispersion (automation-adjusted)
- Strategic Importance Score (dynamic adjustment)
- Combined Risk Score (geopolitical + technical)
- Decision Recommendation (technical override logic)

## Technical Architecture

```
User Input (SKU Parameters)
    ↓
AHP Scores (from database)
    ↓
Technical Viability Score Calculation
    ↓
AHP Adjustments Applied:
  - Yield Risk Penalty
  - Long-Term Cost Multiplier
  - Automation-Adjusted LFD
  - Strategic Importance Score Adjustment
    ↓
Geopolitical Risk Assessment
    ↓
Combined Risk Score (40% geo + 60% technical)
    ↓
Decision Override Logic (Technical Threshold Check)
    ↓
Final Recommendation
```

## Example Output

**Technical Viability Report includes:**
- Overall V Score (0-1)
- Top Driver/Detractor criteria
- Category scores (Manufacturing Requirements, Equipment Specifications, Procurement Concerns)
- Warning message about industry priorities

**Example Warning:**
```
WARNING: Proposed supplier's Technical Viability Score (45%) is below 
the minimum threshold (50%). Despite potential price savings of $101,374, 
technical risk outweighs cost benefit. PCB industry prioritizes 
Manufacturing Requirements (0.545) and Equipment Specifications (0.279) 
over Purchasing Costs (0.032). Low scores in Mark Alignment Correction 
(0.50) indicate insufficient technical capability.
```

## Key Principles Implemented

1. **Technical Capability > Price**: Manufacturing Requirements (0.545) and Equipment Specifications (0.279) prioritized over Purchasing Costs (0.032)

2. **Yield Risk Penalty**: Low precision = high scrap risk = cost multiplier in TLC

3. **Long-Term Thinking**: Maintenance, durability, and warranty feed into total ownership cost

4. **Automation Reduces Labor Risk**: Higher automation reduces LFD (Labor Friction Dispersion)

5. **Critical Criteria Enforcement**: Line and Space (0.182) and Mark Alignment Correction (0.137) are mandatory for high-precision manufacturing

## Files Created/Modified

### New Files:
- `ahp_criteria.py` - AHP criteria, weights, and calculation functions
- `decision_engine_ahp_integrated.py` - AHP-integrated decision engine
- `data_sources/ahp_data.py` - AHP data source for loading scores
- `data/ahp_scores.json` - Database of AHP scores for suppliers

### Modified Files:
- `data_sources/adapter.py` - Added AHP data source integration

## Next Steps (Future Enhancements)

1. **UI Integration**: Create AHP-enabled web interface showing technical viability scores
2. **Supplier Scoring Interface**: Allow users to input/edit AHP scores for suppliers
3. **Scenario Modeling**: Enable "what-if" analysis for AHP criteria
4. **Visualization**: Charts showing AHP category scores and criterion comparisons
5. **Historical Tracking**: Track technical viability scores over time

## Branch Status

- **Branch**: `feature/ahp-integration`
- **Status**: Core implementation complete and committed
- **Ready for**: UI integration and testing

