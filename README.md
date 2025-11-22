# PCB Sourcing Decision Engine MVP

A plug-and-play decision engine for electronics importers to analyze the financial and geopolitical tradeoffs of switching PCB suppliers from China to Vietnam.

## Features

- **Financial Analysis**: Calculate NPV Delta with comprehensive cost modeling including freight, duties, and lead time adjustments
- **Geopolitical Risk Scoring**: Quantified risk analysis using multiple factors:
  - Geopolitical Trade Stability (GTS) Penalty
  - Geopolitical Supply Vulnerability (GSV)
  - Geopolitical Logistics Volatility (GLV)
- **Decision Recommendation**: Weighted decision model combining financial incentives with risk-adjusted expected losses
- **Contingency Planning**: Automated recommendations based on identified risk factors
- **Legal/Engineering Questions**: Dynamic generation of critical questions for cross-functional teams

## Technology Stack

- **Pure HTML/CSS/JavaScript**: Standalone single-file application
- **No Server Required**: Runs entirely in the browser
- **Mock Data**: Embedded supplier data for China and Vietnam

## Setup Instructions

**Simply open `index.html` in your web browser!**

1. **Open the file**:
   - Double-click `index.html`, or
   - Right-click → "Open with" → Your web browser, or
   - Drag and drop the file into your browser window

2. **That's it!** The application is ready to use.

No installation, no dependencies, no server setup required. Everything runs locally in your browser.

## Usage

1. Enter SKU parameters in the input form:
   - SKU/Component Number
   - Quantity per PO cycle
   - Current and proposed prices
   - MOQ (Minimum Order Quantity) for both suppliers
   - Lead times for both suppliers
   - Expected re-ordering quantity
   - Strategic Importance Score (1-10)

2. Click "Analyze Decision" to generate the recommendation

3. Review the results:
   - **Recommendation**: Switch to Vietnam or Stay with China
   - **Cash Flow Delta**: Projected savings/costs per cycle
   - **Risk Analysis**: Detailed geopolitical risk scores for both suppliers
   - **Contingency Recommendations**: Actionable mitigation strategies
   - **Legal Questions**: Critical questions for your cross-functional teams

## Data Structure

The application uses mock data stored in `data/suppliers.json` for:
- Geopolitical Alignment Score (GAS)
- Critical Mineral Dependency Index (CMDI)
- Strategic Shielding Potential (SSP)
- Foreland Volatility Multiplier (FVM)
- Trade Fragmentation Risk Factor (TFRF)
- Freight costs and tariff rates

## MVP Constraints

- Focus: PCB component category only
- Origin/Destination: China → Vietnam supplier comparison
- Importer Country: U.S. (fixed)
- Mock data used for geopolitical metrics (no real-time API integrations)

## Future Enhancements

- Real-time API integrations for geopolitical data
- Multi-component category support
- Additional origin/destination pairs
- Email update generator for metric changes
- Historical trend analysis
- Advanced scenario modeling

## License

This is a prototype/MVP for demonstration purposes.

