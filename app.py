from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

# Load mock data
def load_mock_data():
    """Load mock geopolitical and supplier data"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Load supplier records
    suppliers_file = os.path.join(data_dir, 'suppliers.json')
    if os.path.exists(suppliers_file):
        with open(suppliers_file, 'r') as f:
            suppliers_data = json.load(f)
    else:
        suppliers_data = get_default_suppliers()
    
    return suppliers_data

def get_default_suppliers():
    """Default mock supplier data"""
    return {
        "china": {
            "country": "China",
            "company_type": "State Enterprise",
            "gas": 0.35,  # Geopolitical Alignment Score (lower = less aligned with US)
            "cmdi": 0.85,  # Critical Mineral Dependency Index (high for China due to REEs)
            "ssp": 0.75,  # Strategic Shielding Potential (high for state enterprises)
            "fvm": 1.45,  # Foreland Volatility Multiplier (China Sea tensions)
            "freight_cost_per_unit": 2.50,
            "tariffs_percent": 25.0,  # Higher tariffs on Chinese imports
            "tfrf": 0.31  # Trade Fragmentation Risk Factor (31% reduction)
        },
        "vietnam": {
            "country": "Vietnam",
            "company_type": "Private",
            "gas": 0.72,  # Higher alignment with US
            "cmdi": 0.45,  # Lower dependency on critical minerals
            "ssp": 0.25,  # Lower shielding risk (private company)
            "fvm": 1.15,  # Lower maritime risk
            "freight_cost_per_unit": 2.30,
            "tariffs_percent": 0.0,  # No tariffs (normal trade relations)
            "tfrf": 0.15  # Lower trade fragmentation risk
        }
    }

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Get available supplier data"""
    suppliers = load_mock_data()
    return jsonify(suppliers)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.json
        
        # Extract SKU parameters
        sku_params = {
            'sku': data.get('sku', ''),
            'quantity': float(data.get('quantity', 0)),
            'price_current': float(data.get('price_current', 0)),
            'price_proposed': float(data.get('price_proposed', 0)),
            'moq_current': int(data.get('moq_current', 0)),
            'moq_proposed': int(data.get('moq_proposed', 0)),
            'lead_time_current': int(data.get('lead_time_current', 0)),
            'lead_time_proposed': int(data.get('lead_time_proposed', 0)),
            'reorder_quantity': float(data.get('reorder_quantity', 0)),
            'sis': int(data.get('sis', 5))  # Strategic Importance Score
        }
        
        # Load supplier data
        suppliers = load_mock_data()
        current_supplier = suppliers['china']
        proposed_supplier = suppliers['vietnam']
        
        # Perform calculations
        result = calculate_decision(sku_params, current_supplier, proposed_supplier)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def calculate_npv_delta(sku_params: Dict, current_supplier: Dict, proposed_supplier: Dict) -> float:
    """
    Calculate NPV Delta (financial tradeoff)
    NPV_Δ = Σ[(Cash Flow_Proposed,t - Cash Flow_Current,t) / (1 + r)^t]
    """
    quantity = sku_params['quantity']
    r = 0.05  # Discount rate (5%)
    t = max(sku_params['lead_time_current'], sku_params['lead_time_proposed']) / 365  # Convert days to years
    
    # Calculate cash flows (costs are negative)
    # Cash Flow = -((Price * Quantity) + Freight Cost + Duties)
    
    # Current supplier costs
    price_cost_current = sku_params['price_current'] * quantity
    freight_cost_current = current_supplier['freight_cost_per_unit'] * quantity * current_supplier['fvm']
    duties_current = price_cost_current * (current_supplier['tariffs_percent'] / 100)
    total_cost_current = -(price_cost_current + freight_cost_current + duties_current)
    
    # Proposed supplier costs
    price_cost_proposed = sku_params['price_proposed'] * quantity
    freight_cost_proposed = proposed_supplier['freight_cost_per_unit'] * quantity * proposed_supplier['fvm']
    duties_proposed = price_cost_proposed * (proposed_supplier['tariffs_percent'] / 100)
    total_cost_proposed = -(price_cost_proposed + freight_cost_proposed + duties_proposed)
    
    # Calculate NPV delta
    cash_flow_delta = total_cost_proposed - total_cost_current
    npv_delta = cash_flow_delta / (1 + r) ** t
    
    return {
        'npv_delta': npv_delta,
        'cost_current': abs(total_cost_current),
        'cost_proposed': abs(total_cost_proposed),
        'cash_flow_delta': cash_flow_delta,
        'details': {
            'price_cost_current': price_cost_current,
            'freight_cost_current': freight_cost_current,
            'duties_current': duties_current,
            'price_cost_proposed': price_cost_proposed,
            'freight_cost_proposed': freight_cost_proposed,
            'duties_proposed': duties_proposed
        }
    }

def calculate_risk_score(supplier: Dict) -> Dict[str, float]:
    """
    Calculate Geopolitical Risk Score
    Risk Score = 0.4 × GTS_Penalty + 0.3 × GSV + 0.3 × GLV_Score
    """
    # GTS_Penalty: Inversely related to GAS (Geopolitical Alignment Score)
    # Lower GAS = Higher risk (penalty)
    gts_penalty = 1.0 - supplier['gas']
    
    # GSV (Geopolitical Supply Vulnerability): Combines CMDI and SSP
    gsv = (supplier['cmdi'] * 0.6 + supplier['ssp'] * 0.4)
    
    # GLV_Score (Geopolitical Logistics Volatility): Based on FVM
    # Normalize FVM to 0-1 scale (assuming FVM ranges from 1.0 to 2.0)
    glv_score = (supplier['fvm'] - 1.0) / 1.0
    glv_score = min(glv_score, 1.0)  # Cap at 1.0
    
    # Weighted risk score
    risk_score = 0.4 * gts_penalty + 0.3 * gsv + 0.3 * glv_score
    
    return {
        'total_risk_score': risk_score,
        'gts_penalty': gts_penalty,
        'gsv': gsv,
        'glv_score': glv_score,
        'components': {
            'gas': supplier['gas'],
            'cmdi': supplier['cmdi'],
            'ssp': supplier['ssp'],
            'fvm': supplier['fvm']
        }
    }

def calculate_decision(sku_params: Dict, current_supplier: Dict, proposed_supplier: Dict) -> Dict[str, Any]:
    """
    Main decision calculation
    W_Decision = NPV_Δ - (Risk Score × E_Loss)
    """
    # Calculate NPV Delta
    npv_result = calculate_npv_delta(sku_params, current_supplier, proposed_supplier)
    
    # Calculate Risk Scores
    current_risk = calculate_risk_score(current_supplier)
    proposed_risk = calculate_risk_score(proposed_supplier)
    
    # Calculate Expected Loss for proposed supplier
    # E_Loss = Annual SKU Revenue × Probability_Disruption × Impact_Magnitude
    annual_sku_revenue = sku_params['price_current'] * sku_params['reorder_quantity'] * 12  # Approximate annual
    
    # Probability of disruption based on proposed supplier's risk score
    # Higher risk score = higher probability of disruption
    probability_disruption = proposed_risk['total_risk_score'] * 0.5  # Scale down to reasonable probability
    impact_magnitude = 0.25  # 25% impact based on Russian firm data reference
    
    e_loss = annual_sku_revenue * probability_disruption * impact_magnitude
    
    # Calculate weighted decision
    # W_Decision = NPV_Δ - (Risk Score × E_Loss)
    # Use proposed supplier's risk score to weight the expected loss
    risk_adjustment = proposed_risk['total_risk_score'] * e_loss
    w_decision = npv_result['npv_delta'] - risk_adjustment
    
    # Calculate risk delta for display
    risk_delta = abs(proposed_risk['total_risk_score'] - current_risk['total_risk_score'])
    
    # Generate recommendation
    recommendation = "SWITCH TO VIETNAM" if w_decision > 0 else "STAY WITH CHINA"
    
    # Generate contingency recommendations
    contingency = generate_contingency_recommendations(proposed_risk if w_decision > 0 else current_risk)
    
    # Generate questions for legal/engineering team
    questions = generate_legal_questions(sku_params, proposed_supplier if w_decision > 0 else current_supplier, 
                                        proposed_risk if w_decision > 0 else current_risk)
    
    return {
        'recommendation': recommendation,
        'w_decision': w_decision,
        'npv_delta': npv_result['npv_delta'],
        'cost_savings': abs(npv_result['npv_delta']) if npv_result['npv_delta'] > 0 else 0,
        'current_cost': npv_result['cost_current'],
        'proposed_cost': npv_result['cost_proposed'],
        'risk_analysis': {
            'current_risk': current_risk,
            'proposed_risk': proposed_risk,
            'risk_delta': risk_delta
        },
        'expected_loss': e_loss,
        'risk_adjustment': risk_adjustment,
        'supplier_metrics': {
            'current': {
                'gas': current_supplier['gas'],
                'fvm': current_supplier['fvm'],
                'tfrf': current_supplier['tfrf'],
                'tariffs_percent': current_supplier['tariffs_percent']
            },
            'proposed': {
                'gas': proposed_supplier['gas'],
                'fvm': proposed_supplier['fvm'],
                'tfrf': proposed_supplier['tfrf'],
                'tariffs_percent': proposed_supplier['tariffs_percent']
            }
        },
        'cost_breakdown': npv_result['details'],
        'contingency_recommendations': contingency,
        'legal_questions': questions,
        'email_generator_prompt': f"Generate monthly email update based on changes to TFRF/FVM metrics. Current TFRF: China {current_supplier['tfrf']:.1%}, Vietnam {proposed_supplier['tfrf']:.1%}. Current FVM: China {current_supplier['fvm']:.2f}x, Vietnam {proposed_supplier['fvm']:.2f}x."
    }

def generate_contingency_recommendations(risk_data: Dict) -> list:
    """Generate contingency planning recommendations based on highest risk factor"""
    recommendations = []
    
    if risk_data['glv_score'] > 0.4:
        recommendations.append({
            'priority': 'High',
            'category': 'Logistics',
            'recommendation': f"Given high Geopolitical Logistics Volatility (GLV: {risk_data['glv_score']:.2f}), review alternative freight providers and shipping routes. Consider diversifying between air and sea freight options to mitigate maritime disruption risks."
        })
    
    if risk_data['gsv'] > 0.5:
        recommendations.append({
            'priority': 'High',
            'category': 'Supply Chain',
            'recommendation': f"High Geopolitical Supply Vulnerability (GSV: {risk_data['gsv']:.2f}) detected. Increase safety stock by 30-60 days to mitigate potential targeted sanction exposure or resource nationalism disruptions."
        })
    
    if risk_data['gts_penalty'] > 0.5:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Trade Relations',
            'recommendation': f"Elevated trade stability risk (GTS Penalty: {risk_data['gts_penalty']:.2f}). Monitor trade policy changes and maintain relationships with alternative suppliers in different regions."
        })
    
    if not recommendations:
        recommendations.append({
            'priority': 'Low',
            'category': 'General',
            'recommendation': "Risk factors are within acceptable ranges. Continue standard monitoring protocols."
        })
    
    return recommendations

def generate_legal_questions(sku_params: Dict, supplier: Dict, risk_data: Dict) -> list:
    """Generate critical questions for legal/engineering/security teams"""
    questions = []
    
    if supplier['ssp'] > 0.5:
        questions.append({
            'category': 'Legal',
            'question': f"Given the high Strategic Shielding Potential (SSP: {supplier['ssp']:.2f}) of the {supplier['country']} supplier, what is our legal exposure if the supplier is subjected to targeted sanctions, potentially leading to asset freezing or supply chain disruption?"
        })
    
    if risk_data['gsv'] > 0.5:
        questions.append({
            'category': 'Engineering/Security',
            'question': f"With Critical Mineral Dependency Index (CMDI: {risk_data['components']['cmdi']:.2f}) at elevated levels, what are our options for component substitution or alternative sourcing to reduce dependency on geopolitically sensitive materials?"
        })
    
    if supplier['tfrf'] > 0.2:
        questions.append({
            'category': 'Supply Chain',
            'question': f"Trade Fragmentation Risk Factor (TFRF: {supplier['tfrf']:.1%}) indicates potential {supplier['tfrf']*100:.0f}% cost increase from trade restrictions. What is our contingency plan if trade flows between blocs are disrupted?"
        })
    
    questions.append({
        'category': 'General',
        'question': f"For SKU {sku_params['sku']} with Strategic Importance Score {sku_params['sis']}/10, what is the acceptable risk threshold for supply disruption, and do we have backup inventory strategies in place?"
    })
    
    return questions

if __name__ == '__main__':
    app.run(debug=True, port=5000)

