"""
AHP-Integrated Decision Engine
Combines AHP Technical Viability with Geopolitical Risk Modeling
Shifts from price arbitrage to productivity-driven strategic sourcing
"""

from decision_engine import (
    SKUInputs, SupplierData, generate_report, 
    calculate_npv_delta, calculate_composite_risk
)
from ahp_criteria import (
    AHPSupplierScores, calculate_technical_viability_score,
    adjust_strategic_importance_with_ahp, calculate_yield_risk_penalty,
    adjust_lfd_with_automation, calculate_long_term_cost_multiplier,
    AHP_GLOBAL_WEIGHTS, format_criterion_name, get_mock_ahp_scores
)
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict


def calculate_ahp_adjusted_npv_delta(
    sku: SKUInputs,
    current_supplier: SupplierData,
    proposed_supplier: SupplierData,
    current_ahp: Optional[AHPSupplierScores] = None,
    proposed_ahp: Optional[AHPSupplierScores] = None
) -> Dict[str, Any]:
    """
    Calculate NPV Delta with AHP adjustments
    
    Incorporates:
    - Yield risk penalty (low precision = high scrap risk)
    - Long-term cost multiplier (maintenance, durability, warranty)
    - Automation-adjusted LFD
    """
    # Base NPV calculation
    npv_result = calculate_npv_delta(sku, current_supplier, proposed_supplier)
    
    # Apply AHP adjustments if AHP scores provided
    if current_ahp and proposed_ahp:
        # Yield risk penalties (low precision = cost multiplier)
        current_yield_penalty = calculate_yield_risk_penalty(current_ahp)
        proposed_yield_penalty = calculate_yield_risk_penalty(proposed_ahp)
        
        # Long-term cost multipliers
        current_ltc = calculate_long_term_cost_multiplier(current_ahp)
        proposed_ltc = calculate_long_term_cost_multiplier(proposed_ahp)
        
        # Apply adjustments to costs
        current_cost_adjusted = npv_result['total_cost_china'] * current_yield_penalty * current_ltc
        proposed_cost_adjusted = npv_result['total_cost_vietnam'] * proposed_yield_penalty * proposed_ltc
        
        # Recalculate NPV delta with adjustments
        npv_delta_adjusted = current_cost_adjusted - proposed_cost_adjusted
        
        npv_result['npv_delta'] = npv_delta_adjusted
        npv_result['total_cost_china'] = current_cost_adjusted
        npv_result['total_cost_vietnam'] = proposed_cost_adjusted
        npv_result['ahp_adjustments'] = {
            'current_yield_penalty': current_yield_penalty,
            'proposed_yield_penalty': proposed_yield_penalty,
            'current_ltc_multiplier': current_ltc,
            'proposed_ltc_multiplier': proposed_ltc
        }
    
    return npv_result


def calculate_combined_risk_score(
    geopolitical_risk: Dict[str, Any],
    technical_viability: Dict[str, Any],
    technical_weight: float = 0.4,
    geopolitical_weight: float = 0.6
) -> Dict[str, Any]:
    """
    Calculate combined risk score integrating geopolitical and technical risk
    
    Technical Viability Score is inverted (high V = low risk)
    """
    # Extract risk score from composite risk structure
    if 'composite_risk_score' in geopolitical_risk:
        geo_risk_score = geopolitical_risk['composite_risk_score'] / 100.0
    else:
        geo_risk_score = geopolitical_risk.get('total_risk_score', 0) / 100.0
    
    # Technical viability: invert (high V = low technical risk)
    tech_v_score = technical_viability.get('technical_viability_score', 0.5)
    tech_risk_score = 1.0 - tech_v_score  # Invert: high capability = low risk
    
    # Combined risk
    combined_risk = (geopolitical_weight * geo_risk_score) + (technical_weight * tech_risk_score)
    
    return {
        'combined_risk_score': combined_risk * 100,
        'geopolitical_risk_score': geo_risk_score * 100,
        'technical_risk_score': tech_risk_score * 100,
        'technical_viability_score': tech_v_score,
        'weights': {
            'geopolitical': geopolitical_weight,
            'technical': technical_weight
        }
    }


def generate_ahp_integrated_recommendation(
    sku: SKUInputs,
    current_supplier: SupplierData,
    proposed_supplier: SupplierData,
    current_ahp: AHPSupplierScores,
    proposed_ahp: AHPSupplierScores
) -> Dict[str, Any]:
    """
    Generate recommendation with AHP-integrated decision logic
    
    Key Principle: Technical viability overrides price arbitrage
    """
    # Calculate technical viability scores
    current_v = calculate_technical_viability_score(current_ahp)
    proposed_v = calculate_technical_viability_score(proposed_ahp)
    
    # Calculate adjusted SIS based on critical technical criteria
    current_sis_adjusted = adjust_strategic_importance_with_ahp(sku.strategic_importance_score, current_ahp)
    proposed_sis_adjusted = adjust_strategic_importance_with_ahp(sku.strategic_importance_score, proposed_ahp)
    
    # Calculate AHP-adjusted NPV
    npv_result = calculate_ahp_adjusted_npv_delta(sku, current_supplier, proposed_supplier, current_ahp, proposed_ahp)
    
    # Calculate geopolitical risks
    from decision_engine import calculate_composite_risk
    current_geo_risk = calculate_composite_risk(current_supplier)
    proposed_geo_risk = calculate_composite_risk(proposed_supplier)
    
    # Calculate combined risks
    current_combined = calculate_combined_risk_score(current_geo_risk, current_v)
    proposed_combined = calculate_combined_risk_score(proposed_geo_risk, proposed_v)
    
    # Technical viability threshold (minimum acceptable score)
    MIN_TECHNICAL_VIABILITY = 0.50  # 50% threshold
    
    # Decision override logic: Technical risk outweighs price benefit
    technical_warning = None
    if proposed_v['technical_viability_score'] < MIN_TECHNICAL_VIABILITY:
        if npv_result['npv_delta'] > 0:  # Price is better but technical is poor
            technical_warning = {
                'severity': 'High',
                'type': 'Technical Viability Override',
                'message': (
                    f"WARNING: Proposed supplier's Technical Viability Score ({proposed_v['technical_viability_score']:.1%}) "
                    f"is below the minimum threshold ({MIN_TECHNICAL_VIABILITY:.0%}). Despite potential price savings "
                    f"of ${npv_result['npv_delta']:,.0f}, technical risk outweighs cost benefit. "
                    f"PCB industry prioritizes Manufacturing Requirements (0.545) and Equipment Specifications (0.279) "
                    f"over Purchasing Costs (0.032). Low scores in {format_criterion_name(proposed_v['top_detractor']['criterion'])} "
                    f"({proposed_v['top_detractor']['score']:.1%}) indicate insufficient technical capability."
                )
            }
    
    # Calculate expected loss with combined risk
    from decision_engine import calculate_expected_loss
    current_expected_loss = calculate_expected_loss(
        npv_result['total_cost_china'],
        current_combined['combined_risk_score'],
        current_supplier.historical_loss_pct
    )
    
    proposed_expected_loss = calculate_expected_loss(
        npv_result['total_cost_vietnam'],
        proposed_combined['combined_risk_score'],
        proposed_supplier.historical_loss_pct
    )
    
    # Weighted decision (considering both financial and technical)
    risk_adjustment = proposed_combined['combined_risk_score'] / 100.0 * proposed_expected_loss
    
    # Technical penalty for low viability
    tech_penalty = 0
    if proposed_v['technical_viability_score'] < MIN_TECHNICAL_VIABILITY:
        tech_penalty = (MIN_TECHNICAL_VIABILITY - proposed_v['technical_viability_score']) * npv_result['npv_delta'] * 2
    
    w_decision = npv_result['npv_delta'] - risk_adjustment - tech_penalty
    
    # Generate recommendation
    if technical_warning:
        recommendation = "NO SWITCH - TECHNICAL RISK OUTWEIGHS PRICE BENEFIT"
        recommendation_rationale = (
            f"Technical Viability Score ({proposed_v['technical_viability_score']:.1%}) below threshold. "
            f"Despite ${npv_result['npv_delta']:,.0f} potential savings, technical risk is unacceptable. "
            f"Stay with current supplier or find alternative with better technical capabilities."
        )
    elif w_decision > 0:
        recommendation = "SWITCH TO PROPOSED SUPPLIER"
        recommendation_rationale = (
            f"Technical Viability Score ({proposed_v['technical_viability_score']:.1%}) meets threshold. "
            f"Combined with financial savings of ${npv_result['npv_delta']:,.0f} and acceptable risk "
            f"profile, switching is recommended."
        )
    else:
        recommendation = "STAY WITH CURRENT SUPPLIER"
        recommendation_rationale = (
            f"Combined risk-adjusted costs and technical considerations favor staying with current supplier. "
            f"Technical Viability: Current ({current_v['technical_viability_score']:.1%}) vs "
            f"Proposed ({proposed_v['technical_viability_score']:.1%})."
        )
    
    # Generate technical analysis
    technical_analysis = {
        'current_viability': current_v,
        'proposed_viability': proposed_v,
        'viability_delta': proposed_v['technical_viability_score'] - current_v['technical_viability_score'],
        'top_driver_message': (
            f"Proposed supplier excels in {format_criterion_name(proposed_v['top_driver']['criterion'])} "
            f"(weight: {proposed_v['top_driver']['weight']:.1%}, score: {proposed_v['top_driver']['score']:.1%})"
        ),
        'top_detractor_message': (
            f"Proposed supplier struggles with {format_criterion_name(proposed_v['top_detractor']['criterion'])} "
            f"(weight: {proposed_v['top_detractor']['weight']:.1%}, score: {proposed_v['top_detractor']['score']:.1%})"
        ),
        'category_comparison': {
            'manufacturing_requirements': {
                'current': current_v['category_scores']['manufacturing_requirements'],
                'proposed': proposed_v['category_scores']['manufacturing_requirements'],
                'weight': 0.545
            },
            'equipment_specifications': {
                'current': current_v['category_scores']['equipment_specifications'],
                'proposed': proposed_v['category_scores']['equipment_specifications'],
                'weight': 0.279
            },
            'procurement_concerns': {
                'current': current_v['category_scores']['procurement_concerns'],
                'proposed': proposed_v['category_scores']['procurement_concerns'],
                'weight': 0.176
            }
        }
    }
    
    return {
        'recommendation': recommendation,
        'w_decision': w_decision,
        'recommendation_rationale': recommendation_rationale,
        'npv_analysis': npv_result,
        'technical_analysis': technical_analysis,
        'risk_analysis': {
            'current': {
                'combined_risk': current_combined,
                'geopolitical_risk': current_geo_risk
            },
            'proposed': {
                'combined_risk': proposed_combined,
                'geopolitical_risk': proposed_geo_risk
            }
        },
        'sis_adjustment': {
            'original': sku.strategic_importance_score,
            'current_adjusted': current_sis_adjusted,
            'proposed_adjusted': proposed_sis_adjusted
        },
        'technical_warning': technical_warning,
        'expected_loss': {
            'current': current_expected_loss,
            'proposed': proposed_expected_loss
        }
    }


def load_ahp_scores_from_database(supplier_id: str) -> Optional[AHPSupplierScores]:
    """Load AHP scores from database"""
    db_path = Path('data/ahp_scores.json')
    if db_path.exists():
        try:
            with open(db_path, 'r') as f:
                ahp_db = json.load(f)
            if supplier_id in ahp_db:
                data = ahp_db[supplier_id]
                return AHPSupplierScores(**{k: v for k, v in data.items() if k != 'notes' and k != 'supplier_id'})
        except Exception as e:
            print(f"Error loading AHP scores: {e}")
    return None


if __name__ == '__main__':
    # Example usage
    from decision_engine import get_mock_supplier_data
    
    sku = SKUInputs(
        sku_id="PCB-AHP-TEST-001",
        quantity_po_cycle=50000,
        current_price_unit=3.50,
        proposed_price_unit=3.20,
        current_lead_time_days=45,
        proposed_lead_time_days=55,
        strategic_importance_score=8
    )
    
    suppliers = get_mock_supplier_data()
    current_supplier = suppliers['china']
    proposed_supplier = suppliers['vietnam']
    
    # Get AHP scores
    current_ahp = get_mock_ahp_scores("CHINA_ALPHA")
    proposed_ahp = get_mock_ahp_scores("VIETNAM_GAMMA")
    
    # Generate AHP-integrated recommendation
    report = generate_ahp_integrated_recommendation(
        sku, current_supplier, proposed_supplier, current_ahp, proposed_ahp
    )
    
    print(json.dumps(report, indent=2, default=str))

