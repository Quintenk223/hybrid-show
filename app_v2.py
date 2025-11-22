"""
Flask Web Application for Decision Engine V2
Provides a web interface to interact with the decision engine
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from decision_engine import (
    SKUInputs,
    SupplierData,
    generate_report,
    get_mock_supplier_data
)
import json

app = Flask(__name__)
CORS(app)

# Load supplier data
suppliers = get_mock_supplier_data()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PCB Sourcing Decision Engine V2</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .input-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }

        .input-section h2 {
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
            font-size: 0.9em;
        }

        .form-group input {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 5px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .results-section {
            display: none;
        }

        .recommendation-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
        }

        .recommendation-box.switch {
            border-left: 5px solid #10b981;
        }

        .recommendation-box.stay {
            border-left: 5px solid #ef4444;
        }

        .recommendation-box h2 {
            font-size: 2em;
            margin-bottom: 15px;
        }

        .switch h2 {
            color: #10b981;
        }

        .stay h2 {
            color: #ef4444;
        }

        .savings-display {
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 10px;
        }

        .positive {
            color: #10b981;
        }

        .negative {
            color: #ef4444;
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }

        .result-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .result-card h3 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .metric-label {
            font-weight: 600;
            color: #666;
        }

        .metric-value {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }

        .risk-score {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            padding: 15px;
            background: #f9fafb;
            border-radius: 5px;
            margin: 10px 0;
        }

        .risk-score.low {
            color: #10b981;
        }

        .risk-score.medium {
            color: #f59e0b;
        }

        .risk-score.high {
            color: #ef4444;
        }

        .warning-box {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            border-left: 4px solid #ef4444;
            background: #fef2f2;
        }

        .warning-box.high {
            border-left-color: #ef4444;
            background: #fef2f2;
        }

        .warning-box h4 {
            color: #991b1b;
            margin-bottom: 8px;
        }

        .scenario-box {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            background: #f0f9ff;
        }

        .scenario-box h4 {
            color: #1e40af;
            margin-bottom: 8px;
        }

        .question-box {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            border-left: 4px solid #7c3aed;
            background: #f5f3ff;
        }

        .question-box h4 {
            color: #5b21b6;
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .cost-breakdown {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }

        .cost-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 0.9em;
            color: #666;
        }

        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            .results-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>PCB Sourcing Decision Engine V2</h1>
            <p class="subtitle">Advanced Geopolitical Risk & Financial Modeling</p>
        </header>

        <div class="input-section">
            <h2>SKU Parameters</h2>
            <form id="analysisForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="sku_id">SKU/Component Number *</label>
                        <input type="text" id="sku_id" name="sku_id" required placeholder="PCB-XYZ-101">
                    </div>

                    <div class="form-group">
                        <label for="quantity_po_cycle">Quantity (per PO cycle) *</label>
                        <input type="number" id="quantity_po_cycle" name="quantity_po_cycle" required min="1" value="50000">
                    </div>

                    <div class="form-group">
                        <label for="current_price_unit">Current Price (China) $/unit *</label>
                        <input type="number" id="current_price_unit" name="current_price_unit" required step="0.01" min="0" value="3.50">
                    </div>

                    <div class="form-group">
                        <label for="proposed_price_unit">Proposed Price (Vietnam) $/unit *</label>
                        <input type="number" id="proposed_price_unit" name="proposed_price_unit" required step="0.01" min="0" value="3.20">
                    </div>

                    <div class="form-group">
                        <label for="current_lead_time_days">Lead Time - Current (Days) *</label>
                        <input type="number" id="current_lead_time_days" name="current_lead_time_days" required min="1" value="45">
                    </div>

                    <div class="form-group">
                        <label for="proposed_lead_time_days">Lead Time - Proposed (Days) *</label>
                        <input type="number" id="proposed_lead_time_days" name="proposed_lead_time_days" required min="1" value="55">
                    </div>

                    <div class="form-group">
                        <label for="strategic_importance_score">Strategic Importance Score (1-10) *</label>
                        <input type="number" id="strategic_importance_score" name="strategic_importance_score" required min="1" max="10" value="8">
                    </div>
                </div>

                <button type="submit" class="btn-primary">Analyze Decision</button>
            </form>
        </div>

        <div class="results-section" id="resultsSection">
            <div class="recommendation-box" id="recommendationBox">
                <h2 id="recommendationTitle"></h2>
                <div class="savings-display" id="savingsDisplay"></div>
                <div style="margin-top: 15px; font-size: 0.9em; color: #666;" id="recommendationRationale"></div>
            </div>

            <div class="results-grid" id="resultsGrid"></div>
        </div>
    </div>

    <script>
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                sku_id: document.getElementById('sku_id').value,
                quantity_po_cycle: parseInt(document.getElementById('quantity_po_cycle').value),
                current_price_unit: parseFloat(document.getElementById('current_price_unit').value),
                proposed_price_unit: parseFloat(document.getElementById('proposed_price_unit').value),
                current_lead_time_days: parseInt(document.getElementById('current_lead_time_days').value),
                proposed_lead_time_days: parseInt(document.getElementById('proposed_lead_time_days').value),
                strategic_importance_score: parseInt(document.getElementById('strategic_importance_score').value)
            };

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error('Analysis failed');
                }

                const data = await response.json();
                displayResults(data);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });

        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(value);
        }

        function getRiskClass(score) {
            if (score < 40) return 'low';
            if (score < 70) return 'medium';
            return 'high';
        }

        function displayResults(data) {
            const resultsSection = document.getElementById('resultsSection');
            const recommendationBox = document.getElementById('recommendationBox');
            const recommendationTitle = document.getElementById('recommendationTitle');
            const savingsDisplay = document.getElementById('savingsDisplay');
            const recommendationRationale = document.getElementById('recommendationRationale');
            const resultsGrid = document.getElementById('resultsGrid');

            // Recommendation
            const isSwitch = data.decision.recommendation === 'SWITCH TO VIETNAM';
            recommendationBox.className = `recommendation-box ${isSwitch ? 'switch' : 'stay'}`;
            recommendationTitle.textContent = `Recommended: ${data.decision.recommendation}`;
            
            if (data.decision.net_weighted_savings > 0) {
                savingsDisplay.textContent = `${formatCurrency(data.decision.net_weighted_savings)} Net Weighted Savings`;
                savingsDisplay.className = 'savings-display positive';
            } else {
                savingsDisplay.textContent = `Risk-Adjusted Cost: ${formatCurrency(Math.abs(data.decision.weighted_decision_value))}`;
                savingsDisplay.className = 'savings-display negative';
            }
            recommendationRationale.textContent = data.decision.recommendation_rationale;

            // Build results grid HTML
            const costBreakdown = data.cost_analysis.cost_breakdown;
            const chinaCost = costBreakdown.china;
            const vietnamCost = costBreakdown.vietnam;
            const riskAnalysis = data.risk_analysis;
            
            let html = '<div class="result-card"><h3>Cost Analysis</h3>';
            html += '<div class="metric"><span class="metric-label">NPV Delta:</span><span class="metric-value ' + (data.cost_analysis.npv_delta > 0 ? 'positive' : 'negative') + '">' + formatCurrency(data.cost_analysis.npv_delta) + '</span></div>';
            html += '<div class="metric"><span class="metric-label">Total Cost (China):</span><span class="metric-value">' + formatCurrency(data.cost_analysis.total_cost_china) + '</span></div>';
            html += '<div class="metric"><span class="metric-label">Total Cost (Vietnam):</span><span class="metric-value">' + formatCurrency(data.cost_analysis.total_cost_vietnam) + '</span></div>';
            html += '<div class="cost-breakdown"><h4>China TLC per Unit: ' + formatCurrency(chinaCost.total_landed_cost_per_unit) + '</h4>';
            html += '<div class="cost-item"><span>Base Price:</span> <span>' + formatCurrency(chinaCost.base_price) + '</span></div>';
            html += '<div class="cost-item"><span>TFRF Adjustment (' + (chinaCost.tfrf_adjustment * 100).toFixed(0) + '%):</span> <span>' + formatCurrency(chinaCost.adjusted_price_ap - chinaCost.base_price) + '</span></div>';
            html += '<div class="cost-item"><span>Freight (FVM ×' + chinaCost.fvm_multiplier + '):</span> <span>' + formatCurrency(chinaCost.adjusted_freight_af) + '</span></div>';
            html += '<div class="cost-item"><span>Tariffs:</span> <span>' + formatCurrency(chinaCost.tariffs) + '</span></div>';
            html += '<h4 style="margin-top: 15px;">Vietnam TLC per Unit: ' + formatCurrency(vietnamCost.total_landed_cost_per_unit) + '</h4>';
            html += '<div class="cost-item"><span>Base Price:</span> <span>' + formatCurrency(vietnamCost.base_price) + '</span></div>';
            html += '<div class="cost-item"><span>TFRF Adjustment (' + (vietnamCost.tfrf_adjustment * 100).toFixed(0) + '%):</span> <span>' + formatCurrency(vietnamCost.adjusted_price_ap - vietnamCost.base_price) + '</span></div>';
            html += '<div class="cost-item"><span>Freight (FVM ×' + vietnamCost.fvm_multiplier + '):</span> <span>' + formatCurrency(vietnamCost.adjusted_freight_af) + '</span></div>';
            html += '<div class="cost-item"><span>Tariffs:</span> <span>' + formatCurrency(vietnamCost.tariffs) + '</span></div></div></div>';
            
            html += '<div class="result-card"><h3>Geopolitical Risk Scores</h3>';
            html += '<div style="margin-bottom: 20px;"><h4>China (Current)</h4>';
            html += '<div class="risk-score ' + getRiskClass(riskAnalysis.china_risk_score) + '">' + riskAnalysis.china_risk_score.toFixed(1) + '/100</div>';
            html += '<div style="font-size: 0.9em; color: #666;">';
            html += '<div>GAS Penalty: ' + riskAnalysis.china_risk_components.gas_penalty.toFixed(1) + '</div>';
            html += '<div>FVM Score: ' + riskAnalysis.china_risk_components.fvm_score.toFixed(1) + '</div>';
            html += '<div>CMDI Score: ' + riskAnalysis.china_risk_components.cmdi_score.toFixed(1) + '</div>';
            html += '<div>SSP Multiplier: ×' + riskAnalysis.china_risk_components.ssp_multiplier.toFixed(1) + '</div></div></div>';
            html += '<div><h4>Vietnam (Proposed)</h4>';
            html += '<div class="risk-score ' + getRiskClass(riskAnalysis.vietnam_risk_score) + '">' + riskAnalysis.vietnam_risk_score.toFixed(1) + '/100</div>';
            html += '<div style="font-size: 0.9em; color: #666;">';
            html += '<div>GAS Penalty: ' + riskAnalysis.vietnam_risk_components.gas_penalty.toFixed(1) + '</div>';
            html += '<div>FVM Score: ' + riskAnalysis.vietnam_risk_components.fvm_score.toFixed(1) + '</div>';
            html += '<div>CMDI Score: ' + riskAnalysis.vietnam_risk_components.cmdi_score.toFixed(1) + '</div>';
            html += '<div>SSP Multiplier: ×' + riskAnalysis.vietnam_risk_components.ssp_multiplier.toFixed(1) + '</div></div></div>';
            html += '<div style="margin-top: 20px; padding: 10px; background: #f0f9ff; border-radius: 5px; font-size: 0.9em;"><strong>Risk Delta:</strong> ' + riskAnalysis.risk_delta.toFixed(1) + ' points (lower is better for Vietnam)</div></div>';
            
            html += '<div class="result-card"><h3>Expected Loss Analysis</h3>';
            html += '<div class="metric"><span class="metric-label">Expected Loss (if sanctions hit):</span><span class="metric-value negative">' + formatCurrency(data.expected_loss_analysis.expected_loss) + '</span></div>';
            html += '<div style="margin-top: 15px; font-size: 0.9em; color: #666; padding: 10px; background: #f9fafb; border-radius: 5px;">' + data.expected_loss_analysis.calculation_basis + '</div></div>';
            
            if (data.contingency_warnings && data.contingency_warnings.length > 0) {
                html += '<div class="result-card"><h3>Contingency Warnings</h3>';
                data.contingency_warnings.forEach(function(w) {
                    html += '<div class="warning-box ' + w.severity.toLowerCase() + '"><h4>[' + w.severity + '] ' + w.type + '</h4><p>' + w.message + '</p></div>';
                });
                html += '</div>';
            }
            
            if (data.strategic_scenarios && data.strategic_scenarios.length > 0) {
                html += '<div class="result-card"><h3>Strategic Scenarios (Vietnam)</h3>';
                data.strategic_scenarios.forEach(function(s) {
                    html += '<div class="scenario-box"><h4>' + s.scenario + ' (' + s.probability + ', ' + s.impact + ')</h4><p>' + s.description + '</p></div>';
                });
                html += '</div>';
            }
            
            if (data.legal_security_questions && data.legal_security_questions.length > 0) {
                html += '<div class="result-card"><h3>Legal / Security / Regulatory Questions</h3>';
                data.legal_security_questions.forEach(function(q, i) {
                    html += '<div class="question-box"><h4>' + (i + 1) + '. [' + q.category + ']</h4><p>' + q.question + '</p></div>';
                });
                html += '</div>';
            }
            
            resultsGrid.innerHTML = html;

            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """Serve the main interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.json
        
        # Create SKU inputs
        sku_inputs = SKUInputs(
            sku_id=data.get('sku_id', ''),
            quantity_po_cycle=int(data.get('quantity_po_cycle', 0)),
            current_price_unit=float(data.get('current_price_unit', 0)),
            proposed_price_unit=float(data.get('proposed_price_unit', 0)),
            current_lead_time_days=int(data.get('current_lead_time_days', 0)),
            proposed_lead_time_days=int(data.get('proposed_lead_time_days', 0)),
            strategic_importance_score=int(data.get('strategic_importance_score', 5))
        )
        
        # Generate report
        report = generate_report(sku_inputs, suppliers['china'], suppliers['vietnam'])
        
        # Convert to JSON-serializable format
        return jsonify(report)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("Starting Decision Engine V2 Web Interface...")
    print("Open your browser and navigate to: http://localhost:5001")
    app.run(debug=True, port=5001)

