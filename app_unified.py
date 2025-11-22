"""
Unified Decision Engine Web Application
Supports both Country-to-Country and Intra-Country supplier comparisons
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from decision_engine import SKUInputs, SupplierData, generate_report, get_mock_supplier_data
from decision_engine_intra_country import (
    IntraCountrySupplierData,
    generate_intra_country_recommendation,
    get_mock_supplier_a,
    get_mock_supplier_b
)
import json

app = Flask(__name__)
CORS(app)

# HTML Template with mode selection
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decision Engine - Unified</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        header h1 { font-size: 2.5em; margin-bottom: 5px; }
        .subtitle { font-size: 1.1em; opacity: 0.9; }
        .mode-selector {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .mode-selector label {
            display: inline-block;
            margin-right: 20px;
            font-weight: 600;
            color: #555;
        }
        .mode-selector input[type="radio"] {
            margin-right: 5px;
        }
        .mode-description {
            margin-top: 10px;
            padding: 10px;
            background: #f0f9ff;
            border-radius: 5px;
            font-size: 0.9em;
            color: #666;
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
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .results-section { display: none; }
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
        .switch h2 { color: #10b981; }
        .stay h2 { color: #ef4444; }
        .savings-display {
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 10px;
        }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
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
        .metric-label { font-weight: 600; color: #666; }
        .metric-value { font-weight: bold; color: #333; font-size: 1.1em; }
        .risk-score {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            padding: 15px;
            background: #f9fafb;
            border-radius: 5px;
            margin: 10px 0;
        }
        .risk-score.low { color: #10b981; }
        .risk-score.medium { color: #f59e0b; }
        .risk-score.high { color: #ef4444; }
        .warning-box, .scenario-box, .question-box {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        .warning-box {
            border-left: 4px solid #ef4444;
            background: #fef2f2;
        }
        .scenario-box {
            border-left: 4px solid #667eea;
            background: #f0f9ff;
        }
        .question-box {
            border-left: 4px solid #7c3aed;
            background: #f5f3ff;
        }
        .friction-heatmap {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }
        .friction-item {
            padding: 15px;
            background: #f9fafb;
            border-radius: 5px;
        }
        .friction-item h4 { margin-bottom: 10px; }
        .friction-bar {
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        .friction-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444);
            transition: width 0.3s;
        }
        .scenario-section {
            margin-top: 30px;
            border-top: 2px solid #e0e0e0;
            padding-top: 20px;
        }
        .scenario-toggle {
            background: #f0f9ff;
            border: 2px solid #667eea;
            color: #667eea;
            padding: 12px 20px;
            border-radius: 5px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            text-align: left;
            font-size: 1em;
        }
        .scenario-toggle:hover {
            background: #e0e7ff;
        }
        .scenario-controls {
            margin-top: 20px;
            padding: 20px;
            background: #f9fafb;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
        .scenario-controls h3 {
            margin-bottom: 20px;
        }
        .scenario-input {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 1em;
            width: 100%;
        }
        .scenario-input:focus {
            outline: none;
            border-color: #667eea;
        }
        .scenario-slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #e0e0e0;
            outline: none;
            margin: 10px 0;
        }
        .scenario-slider::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        .slider-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }
        .slider-labels span:nth-child(2) {
            font-weight: bold;
            color: #667eea;
        }
        .scenario-controls small {
            display: block;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>PCB Sourcing Decision Engine</h1>
            <p class="subtitle">Country-to-Country & Intra-Country Supplier Analysis</p>
        </header>

        <div class="mode-selector">
            <label>
                <input type="radio" name="comparisonMode" value="country" checked onchange="toggleMode()">
                Country-to-Country (China → Vietnam)
            </label>
            <label>
                <input type="radio" name="comparisonMode" value="intra" onchange="toggleMode()">
                Intra-Country (China Supplier A ↔ China Supplier B)
            </label>
            <div class="mode-description" id="modeDescription">
                Compare suppliers from different countries with geopolitical alignment analysis.
            </div>
        </div>

        <div class="input-section">
            <h2>SKU Parameters</h2>
            <form id="analysisForm">
                <div class="form-grid" id="formGrid">
                    <!-- Country-to-Country fields -->
                    <div class="form-group mode-country">
                        <label for="sku_id">SKU/Component Number *</label>
                        <input type="text" id="sku_id" name="sku_id" required placeholder="PCB-XYZ-101">
                    </div>
                    <div class="form-group mode-country">
                        <label for="quantity_po_cycle">Quantity (per PO cycle) *</label>
                        <input type="number" id="quantity_po_cycle" name="quantity_po_cycle" required min="1" value="50000">
                    </div>
                    <div class="form-group mode-country">
                        <label for="current_price_unit">Current Price (China) $/unit *</label>
                        <input type="number" id="current_price_unit" name="current_price_unit" required step="0.01" min="0" value="3.50">
                    </div>
                    <div class="form-group mode-country">
                        <label for="proposed_price_unit">Proposed Price (Vietnam) $/unit *</label>
                        <input type="number" id="proposed_price_unit" name="proposed_price_unit" required step="0.01" min="0" value="3.20">
                    </div>
                    <div class="form-group mode-country">
                        <label for="current_lead_time_days">Lead Time - Current (Days) *</label>
                        <input type="number" id="current_lead_time_days" name="current_lead_time_days" required min="1" value="45">
                    </div>
                    <div class="form-group mode-country">
                        <label for="proposed_lead_time_days">Lead Time - Proposed (Days) *</label>
                        <input type="number" id="proposed_lead_time_days" name="proposed_lead_time_days" required min="1" value="55">
                    </div>
                    <div class="form-group mode-country">
                        <label for="strategic_importance_score">Strategic Importance Score (1-10) *</label>
                        <input type="number" id="strategic_importance_score" name="strategic_importance_score" required min="1" max="10" value="8">
                    </div>
                </div>
                
                <!-- Scenario Controls Section -->
                <div class="scenario-section" id="scenarioSection">
                    <button type="button" class="scenario-toggle" onclick="toggleScenarioSection()">
                        <span id="scenarioToggleIcon">▼</span> Geopolitical & Risk Scenario Inputs (Optional Overrides)
                    </button>
                    <div class="scenario-controls" id="scenarioControls" style="display: none;">
                        <div id="countryScenarioControls" class="mode-country">
                            <h3 style="margin-bottom: 15px; color: #667eea;">Country-to-Country Geopolitical Metrics</h3>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label for="china_gas">China GAS (Geopolitical Alignment Score)</label>
                                    <select id="china_gas" name="china_gas" class="scenario-input">
                                        <option value="">Use Database Default (0.20)</option>
                                        <option value="0.10">Discordant/Rival (0.10 - High Risk)</option>
                                        <option value="0.20" selected>Neutral/Ambivalent (0.20 - Moderate Risk)</option>
                                        <option value="0.30">Slightly Aligned (0.30)</option>
                                        <option value="0.50">Moderately Aligned (0.50)</option>
                                    </select>
                                    <small style="color: #666; font-size: 0.85em;">UNGA voting similarity impact on trade flows</small>
                                </div>
                                <div class="form-group">
                                    <label for="vietnam_gas">Vietnam GAS (Geopolitical Alignment Score)</label>
                                    <select id="vietnam_gas" name="vietnam_gas" class="scenario-input">
                                        <option value="">Use Database Default (0.60)</option>
                                        <option value="0.40">Neutral (0.40)</option>
                                        <option value="0.60" selected>Moderately Aligned (0.60)</option>
                                        <option value="0.75">Highly Aligned (0.75 - Low Risk)</option>
                                        <option value="0.85">Very Highly Aligned (0.85 - Very Low Risk)</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="china_tfrf">China TFRF (%) - Trade Fragmentation Risk</label>
                                    <input type="range" id="china_tfrf" name="china_tfrf" min="0" max="100" value="31" step="1" class="scenario-slider">
                                    <div class="slider-labels">
                                        <span>0% (Minimal)</span>
                                        <span id="china_tfrf_display">31%</span>
                                        <span>100% (Severe)</span>
                                    </div>
                                    <small style="color: #666;">Trade flow reduction: 22-57% across bloc boundaries</small>
                                </div>
                                <div class="form-group">
                                    <label for="vietnam_tfrf">Vietnam TFRF (%) - Trade Fragmentation Risk</label>
                                    <input type="range" id="vietnam_tfrf" name="vietnam_tfrf" min="0" max="100" value="15" step="1" class="scenario-slider">
                                    <div class="slider-labels">
                                        <span>0% (Minimal)</span>
                                        <span id="vietnam_tfrf_display">15%</span>
                                        <span>100% (Severe)</span>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="china_cmdi">China CMDI - Critical Mineral Dependency</label>
                                    <select id="china_cmdi" name="china_cmdi" class="scenario-input">
                                        <option value="">Use Database Default (0.90)</option>
                                        <option value="0.50">Low Dependency (0.50)</option>
                                        <option value="0.70">Moderate Vulnerability (0.70)</option>
                                        <option value="0.90" selected>High Criticality/Fragile Supply (0.90)</option>
                                        <option value="0.95">Very High Criticality (0.95)</option>
                                    </select>
                                    <small style="color: #666;">Inelastic supply chain vulnerability</small>
                                </div>
                                <div class="form-group">
                                    <label for="vietnam_cmdi">Vietnam CMDI - Critical Mineral Dependency</label>
                                    <select id="vietnam_cmdi" name="vietnam_cmdi" class="scenario-input">
                                        <option value="">Use Database Default (0.50)</option>
                                        <option value="0.30">Low Dependency (0.30)</option>
                                        <option value="0.50" selected>Moderate Vulnerability (0.50)</option>
                                        <option value="0.70">High Criticality (0.70)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div id="intraScenarioControls" class="mode-intra" style="display: none;">
                            <h3 style="margin-bottom: 15px; color: #667eea;">Intra-Country Firm-Level Metrics</h3>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label for="supplier_a_ssp">Supplier A SSP (Strategic Shielding Potential)</label>
                                    <select id="supplier_a_ssp" name="supplier_a_ssp" class="scenario-input">
                                        <option value="">Use Database Default</option>
                                        <option value="0.20">Non-Strategic Firm (0.20 - No Shielding)</option>
                                        <option value="0.50">Semi-Strategic (0.50)</option>
                                        <option value="0.75">Strategic Firm (0.75 - Likely Shielding)</option>
                                        <option value="0.90">Strategic Jewel (0.90 - High Shielding)</option>
                                    </select>
                                    <small style="color: #666;">Government protection from sanctions</small>
                                </div>
                                <div class="form-group">
                                    <label for="supplier_b_ssp">Supplier B SSP (Strategic Shielding Potential)</label>
                                    <select id="supplier_b_ssp" name="supplier_b_ssp" class="scenario-input">
                                        <option value="">Use Database Default</option>
                                        <option value="0.20">Non-Strategic Firm (0.20 - No Shielding)</option>
                                        <option value="0.50">Semi-Strategic (0.50)</option>
                                        <option value="0.75">Strategic Firm (0.75 - Likely Shielding)</option>
                                        <option value="0.90">Strategic Jewel (0.90 - High Shielding)</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="supplier_a_lfd">Supplier A LFD - Labor Friction Dispersion (0.0-2.0)</label>
                                    <input type="number" id="supplier_a_lfd" name="supplier_a_lfd" min="0" max="2.0" step="0.01" class="scenario-input" placeholder="e.g., 0.85 (coastal) or 1.18 (inland)">
                                    <small style="color: #666;">Average: 1.18. Coastal regions typically lower (0.85)</small>
                                </div>
                                <div class="form-group">
                                    <label for="supplier_b_lfd">Supplier B LFD - Labor Friction Dispersion (0.0-2.0)</label>
                                    <input type="number" id="supplier_b_lfd" name="supplier_b_lfd" min="0" max="2.0" step="0.01" class="scenario-input" placeholder="e.g., 0.85 (coastal) or 1.18 (inland)">
                                </div>
                                <div class="form-group">
                                    <label for="supplier_a_pvs">Supplier A PVS - Port Foreland Vulnerability</label>
                                    <select id="supplier_a_pvs" name="supplier_a_pvs" class="scenario-input">
                                        <option value="">Use Database Default</option>
                                        <option value="30">Stable Route/Low Risk (30)</option>
                                        <option value="50">Moderate Exposure (50)</option>
                                        <option value="70">High Vulnerability (70)</option>
                                        <option value="90">Critical Chokepoint/Conflict Zone (90)</option>
                                    </select>
                                    <small style="color: #666;">Geopolitical risk of shipping route</small>
                                </div>
                                <div class="form-group">
                                    <label for="supplier_b_pvs">Supplier B PVS - Port Foreland Vulnerability</label>
                                    <select id="supplier_b_pvs" name="supplier_b_pvs" class="scenario-input">
                                        <option value="">Use Database Default</option>
                                        <option value="30">Stable Route/Low Risk (30)</option>
                                        <option value="50">Moderate Exposure (50)</option>
                                        <option value="70">High Vulnerability (70)</option>
                                        <option value="90">Critical Chokepoint/Conflict Zone (90)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn-primary">Analyze Decision</button>
            </form>
        </div>

        <div class="results-section" id="resultsSection"></div>
    </div>

    <script>
        function toggleMode() {
            const mode = document.querySelector('input[name="comparisonMode"]:checked').value;
            const description = document.getElementById('modeDescription');
            
            if (mode === 'country') {
                description.textContent = 'Compare suppliers from different countries with geopolitical alignment analysis.';
                document.querySelectorAll('.mode-country').forEach(el => el.style.display = '');
                document.querySelectorAll('.mode-intra').forEach(el => el.style.display = 'none');
                document.getElementById('current_price_unit').parentElement.querySelector('label').textContent = 'Current Price (China) $/unit *';
                document.getElementById('proposed_price_unit').parentElement.querySelector('label').textContent = 'Proposed Price (Vietnam) $/unit *';
                document.getElementById('countryScenarioControls').style.display = 'block';
                document.getElementById('intraScenarioControls').style.display = 'none';
            } else {
                description.textContent = 'Compare two suppliers within the same country, analyzing firm-level stability and localized operational risks.';
                document.querySelectorAll('.mode-country').forEach(el => el.style.display = '');
                document.querySelectorAll('.mode-intra').forEach(el => el.style.display = 'none');
                document.getElementById('current_price_unit').parentElement.querySelector('label').textContent = 'Supplier A Price $/unit *';
                document.getElementById('proposed_price_unit').parentElement.querySelector('label').textContent = 'Supplier B Price $/unit *';
                document.getElementById('countryScenarioControls').style.display = 'none';
                document.getElementById('intraScenarioControls').style.display = 'block';
            }
        }
        
        function toggleScenarioSection() {
            const controls = document.getElementById('scenarioControls');
            const icon = document.getElementById('scenarioToggleIcon');
            if (controls.style.display === 'none') {
                controls.style.display = 'block';
                icon.textContent = '▲';
            } else {
                controls.style.display = 'none';
                icon.textContent = '▼';
            }
        }
        
        // Slider value displays
        document.addEventListener('DOMContentLoaded', function() {
            const chinaTfrf = document.getElementById('china_tfrf');
            const vietnamTfrf = document.getElementById('vietnam_tfrf');
            const chinaTfrfDisplay = document.getElementById('china_tfrf_display');
            const vietnamTfrfDisplay = document.getElementById('vietnam_tfrf_display');
            
            if (chinaTfrf) {
                chinaTfrf.addEventListener('input', function() {
                    chinaTfrfDisplay.textContent = this.value + '%';
                });
            }
            if (vietnamTfrf) {
                vietnamTfrf.addEventListener('input', function() {
                    vietnamTfrfDisplay.textContent = this.value + '%';
                });
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

        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const mode = document.querySelector('input[name="comparisonMode"]:checked').value;
            
            const formData = {
                mode: mode,
                sku_id: document.getElementById('sku_id').value,
                quantity_po_cycle: parseInt(document.getElementById('quantity_po_cycle').value),
                current_price_unit: parseFloat(document.getElementById('current_price_unit').value),
                proposed_price_unit: parseFloat(document.getElementById('proposed_price_unit').value),
                current_lead_time_days: parseInt(document.getElementById('current_lead_time_days').value),
                proposed_lead_time_days: parseInt(document.getElementById('proposed_lead_time_days').value),
                strategic_importance_score: parseInt(document.getElementById('strategic_importance_score').value)
            };
            
            // Add scenario overrides if provided
            if (mode === 'country') {
                const chinaGas = document.getElementById('china_gas').value;
                const vietnamGas = document.getElementById('vietnam_gas').value;
                const chinaTfrf = document.getElementById('china_tfrf').value;
                const vietnamTfrf = document.getElementById('vietnam_tfrf').value;
                const chinaCmdi = document.getElementById('china_cmdi').value;
                const vietnamCmdi = document.getElementById('vietnam_cmdi').value;
                
                if (chinaGas) formData.china_gas_override = parseFloat(chinaGas);
                if (vietnamGas) formData.vietnam_gas_override = parseFloat(vietnamGas);
                if (chinaTfrf) formData.china_tfrf_override = parseFloat(chinaTfrf) / 100;
                if (vietnamTfrf) formData.vietnam_tfrf_override = parseFloat(vietnamTfrf) / 100;
                if (chinaCmdi) formData.china_cmdi_override = parseFloat(chinaCmdi);
                if (vietnamCmdi) formData.vietnam_cmdi_override = parseFloat(vietnamCmdi);
            } else {
                const supplierASSP = document.getElementById('supplier_a_ssp').value;
                const supplierBSSP = document.getElementById('supplier_b_ssp').value;
                const supplierALFD = document.getElementById('supplier_a_lfd').value;
                const supplierBLFD = document.getElementById('supplier_b_lfd').value;
                const supplierAPVS = document.getElementById('supplier_a_pvs').value;
                const supplierBPVS = document.getElementById('supplier_b_pvs').value;
                
                if (supplierASSP) formData.supplier_a_ssp_override = parseFloat(supplierASSP);
                if (supplierBSSP) formData.supplier_b_ssp_override = parseFloat(supplierBSSP);
                if (supplierALFD) formData.supplier_a_lfd_override = parseFloat(supplierALFD);
                if (supplierBLFD) formData.supplier_b_lfd_override = parseFloat(supplierBLFD);
                if (supplierAPVS) formData.supplier_a_pvs_override = parseFloat(supplierAPVS);
                if (supplierBPVS) formData.supplier_b_pvs_override = parseFloat(supplierBPVS);
            }

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) throw new Error('Analysis failed');
                const data = await response.json();
                displayResults(data, mode);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });

        function displayResults(data, mode) {
            const resultsSection = document.getElementById('resultsSection');
            let html = '';
            
            if (mode === 'country') {
                html = displayCountryResults(data);
            } else {
                html = displayIntraCountryResults(data);
            }
            
            resultsSection.innerHTML = html;
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }

        function displayCountryResults(data) {
            const isSwitch = data.decision.recommendation === 'SWITCH TO VIETNAM';
            let html = '<div class="recommendation-box ' + (isSwitch ? 'switch' : 'stay') + '">';
            html += '<h2>Recommended: ' + data.decision.recommendation + '</h2>';
            html += '<div class="savings-display ' + (data.decision.net_weighted_savings > 0 ? 'positive' : 'negative') + '">';
            html += formatCurrency(data.decision.net_weighted_savings) + ' Net Weighted Savings</div>';
            html += '<div style="margin-top: 15px; font-size: 0.9em; color: #666;">' + data.decision.recommendation_rationale + '</div></div>';
            
            html += '<div class="results-grid">';
            html += '<div class="result-card"><h3>Cost Analysis</h3>';
            html += '<div class="metric"><span class="metric-label">NPV Delta:</span><span class="metric-value ' + (data.cost_analysis.npv_delta > 0 ? 'positive' : 'negative') + '">' + formatCurrency(data.cost_analysis.npv_delta) + '</span></div>';
            html += '<div class="metric"><span class="metric-label">Total Cost (China):</span><span class="metric-value">' + formatCurrency(data.cost_analysis.total_cost_china) + '</span></div>';
            html += '<div class="metric"><span class="metric-label">Total Cost (Vietnam):</span><span class="metric-value">' + formatCurrency(data.cost_analysis.total_cost_vietnam) + '</span></div></div>';
            
            html += '<div class="result-card"><h3>Risk Scores</h3>';
            html += '<div>China: <span class="risk-score ' + getRiskClass(data.risk_analysis.china_risk_score) + '">' + data.risk_analysis.china_risk_score.toFixed(1) + '/100</span></div>';
            html += '<div style="margin-top: 15px;">Vietnam: <span class="risk-score ' + getRiskClass(data.risk_analysis.vietnam_risk_score) + '">' + data.risk_analysis.vietnam_risk_score.toFixed(1) + '/100</span></div></div>';
            html += '</div>';
            
            return html;
        }

        function displayIntraCountryResults(data) {
            const isSwitch = data.decision.recommendation.includes('SWITCH TO');
            let html = '<div class="recommendation-box ' + (isSwitch ? 'switch' : 'stay') + '">';
            html += '<h2>' + data.decision.recommendation + '</h2>';
            html += '<div class="savings-display ' + (data.decision.net_weighted_savings > 0 ? 'positive' : 'negative') + '">';
            html += formatCurrency(data.decision.net_weighted_savings) + ' Net Weighted Savings</div>';
            html += '<div style="margin-top: 15px; font-size: 0.9em; color: #666;">' + data.decision.recommendation_rationale + '</div></div>';
            
            html += '<div class="results-grid">';
            html += '<div class="result-card"><h3>Cost Analysis</h3>';
            html += '<div class="metric"><span class="metric-label">NPV Delta:</span><span class="metric-value ' + (data.cost_analysis.npv_delta > 0 ? 'positive' : 'negative') + '">' + formatCurrency(data.cost_analysis.npv_delta) + '</span></div>';
            html += '<div class="metric"><span class="metric-label">Supplier A Cost:</span><span class="metric-value">' + formatCurrency(data.cost_analysis.supplier_a_cost) + '</span></div>';
            html += '<div class="metric"><span class="metric-label">Supplier B Cost:</span><span class="metric-value">' + formatCurrency(data.cost_analysis.supplier_b_cost) + '</span></div></div>';
            
            const friction = data.friction_heatmap;
            html += '<div class="result-card"><h3>Friction Heatmap</h3>';
            html += '<div class="friction-heatmap">';
            html += '<div class="friction-item"><h4>' + friction.supplier_a.name + '</h4>';
            html += '<div>Location: ' + friction.supplier_a.location + ' (' + friction.supplier_a.location_type + ')</div>';
            html += '<div style="margin-top: 10px;">LFD: ' + friction.supplier_a.labor_friction_dispersion.toFixed(1) + '%</div>';
            html += '<div class="friction-bar"><div class="friction-bar-fill" style="width: ' + friction.supplier_a.labor_friction_dispersion + '%"></div></div>';
            html += '</div>';
            html += '<div class="friction-item"><h4>' + friction.supplier_b.name + '</h4>';
            html += '<div>Location: ' + friction.supplier_b.location + ' (' + friction.supplier_b.location_type + ')</div>';
            html += '<div style="margin-top: 10px;">LFD: ' + friction.supplier_b.labor_friction_dispersion.toFixed(1) + '%</div>';
            html += '<div class="friction-bar"><div class="friction-bar-fill" style="width: ' + friction.supplier_b.labor_friction_dispersion + '%"></div></div>';
            html += '</div></div>';
            html += '<div style="margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 5px; font-size: 0.9em;">' + friction.key_insight + '</div></div>';
            
            html += '<div class="result-card"><h3>Risk Scores</h3>';
            html += '<div>Supplier A: <span class="risk-score ' + getRiskClass(data.risk_analysis.supplier_a.composite_risk_score) + '">' + data.risk_analysis.supplier_a.composite_risk_score.toFixed(1) + '/100</span></div>';
            html += '<div style="margin-top: 15px;">Supplier B: <span class="risk-score ' + getRiskClass(data.risk_analysis.supplier_b.composite_risk_score) + '">' + data.risk_analysis.supplier_b.composite_risk_score.toFixed(1) + '/100</span></div></div>';
            
            if (data.contingency_warnings && data.contingency_warnings.length > 0) {
                html += '<div class="result-card"><h3>Contingency Warnings</h3>';
                data.contingency_warnings.forEach(function(w) {
                    html += '<div class="warning-box"><h4>[' + w.severity + '] ' + w.type + '</h4><p>' + w.message + '</p></div>';
                });
                html += '</div>';
            }
            
            if (data.legal_questions && data.legal_questions.length > 0) {
                html += '<div class="result-card"><h3>Questions for Vetting Team</h3>';
                data.legal_questions.forEach(function(q, i) {
                    html += '<div class="question-box"><h4>' + (i + 1) + '. [' + q.category + ']</h4><p>' + q.question + '</p></div>';
                });
                html += '</div>';
            }
            
            html += '</div>';
            return html;
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        mode = data.get('mode', 'country')
        
        sku_inputs = SKUInputs(
            sku_id=data.get('sku_id', ''),
            quantity_po_cycle=int(data.get('quantity_po_cycle', 0)),
            current_price_unit=float(data.get('current_price_unit', 0)),
            proposed_price_unit=float(data.get('proposed_price_unit', 0)),
            current_lead_time_days=int(data.get('current_lead_time_days', 0)),
            proposed_lead_time_days=int(data.get('proposed_lead_time_days', 0)),
            strategic_importance_score=int(data.get('strategic_importance_score', 5))
        )
        
        if mode == 'country':
            from data_sources import DataAdapter
            adapter = DataAdapter()
            
            # Get base supplier data
            china_dict = adapter.get_country_level_supplier_data("China", "USA")
            vietnam_dict = adapter.get_country_level_supplier_data("Vietnam", "USA")
            
            # Apply overrides if provided
            if 'china_gas_override' in data:
                china_dict['gas_score'] = data['china_gas_override']
            if 'vietnam_gas_override' in data:
                vietnam_dict['gas_score'] = data['vietnam_gas_override']
            if 'china_tfrf_override' in data:
                china_dict['tfrf_penalty'] = data['china_tfrf_override']
            if 'vietnam_tfrf_override' in data:
                vietnam_dict['tfrf_penalty'] = data['vietnam_tfrf_override']
            if 'china_cmdi_override' in data:
                china_dict['cm_dependency'] = data['china_cmdi_override']
            if 'vietnam_cmdi_override' in data:
                vietnam_dict['cm_dependency'] = data['vietnam_cmdi_override']
            
            china_supplier = SupplierData(**china_dict)
            vietnam_supplier = SupplierData(**vietnam_dict)
            report = generate_report(sku_inputs, china_supplier, vietnam_supplier)
        else:
            from data_sources import DataAdapter
            adapter = DataAdapter()
            
            supplier_a_dict = adapter.get_intra_country_supplier_data("CHINA_ALPHA")
            supplier_b_dict = adapter.get_intra_country_supplier_data("CHINA_BETA")
            
            # Apply overrides if provided
            if 'supplier_a_ssp_override' in data:
                supplier_a_dict['ssp_score'] = data['supplier_a_ssp_override']
            if 'supplier_b_ssp_override' in data:
                supplier_b_dict['ssp_score'] = data['supplier_b_ssp_override']
            if 'supplier_a_lfd_override' in data:
                supplier_a_dict['labor_friction_dispersion'] = data['supplier_a_lfd_override']
            if 'supplier_b_lfd_override' in data:
                supplier_b_dict['labor_friction_dispersion'] = data['supplier_b_lfd_override']
            if 'supplier_a_pvs_override' in data:
                supplier_a_dict['port_foreland_vulnerability_score'] = data['supplier_a_pvs_override']
            if 'supplier_b_pvs_override' in data:
                supplier_b_dict['port_foreland_vulnerability_score'] = data['supplier_b_pvs_override']
            
            supplier_a = IntraCountrySupplierData(**supplier_a_dict)
            supplier_b = IntraCountrySupplierData(**supplier_b_dict)
            report = generate_intra_country_recommendation(sku_inputs, supplier_a, supplier_b)
        
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("Starting Unified Decision Engine...")
    print("Open your browser: http://localhost:5002")
    app.run(debug=True, port=5002)



