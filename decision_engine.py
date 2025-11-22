"""
PCB Sourcing Decision Engine V2
Advanced Geopolitical Risk and Financial Modeling for China vs Vietnam Supplier Analysis
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class SKUInputs:
    """SKU input parameters provided by user"""
    sku_id: str
    quantity_po_cycle: int
    current_price_unit: float  # China Price ($)
    proposed_price_unit: float  # Vietnam Price ($)
    current_lead_time_days: int
    proposed_lead_time_days: int
    importer_country: str = "USA"
    strategic_importance_score: int = 5  # Scale 1-10


@dataclass
class SupplierData:
    """Enhanced supplier data with geopolitical risk factors"""
    country: str
    base_freight_cost: float
    gas_score: float  # Geopolitical Alignment Score (0-1.0)
    tfrf_penalty: float  # Trade Fragmentation Risk Factor (0-1.0)
    fvm_multiplier: float  # Foreland Volatility Multiplier (1.0+)
    ssp_flag: str  # Strategic Shielding Potential: "State-Subsidiary" or "Private"
    cm_dependency: float  # Critical Mineral Dependency (0-1.0)
    historical_loss_pct: float  # Expected revenue loss % if targeted sanctions hit
    tariffs_percent: float = 0.0  # Import tariffs


def get_mock_supplier_data() -> Dict[str, SupplierData]:
    """Initialize mock supplier data reflecting strategic positions"""
    return {
        "china": SupplierData(
            country="China",
            base_freight_cost=0.05,
            gas_score=0.20,  # Lower alignment with US
            tfrf_penalty=0.31,  # Higher trade fragmentation risk
            fvm_multiplier=1.20,  # Higher maritime/port risk volatility
            ssp_flag="State-Subsidiary",
            cm_dependency=0.90,  # High critical mineral dependency
            historical_loss_pct=0.25,  # 25% revenue loss if sanctions hit
            tariffs_percent=25.0
        ),
        "vietnam": SupplierData(
            country="Vietnam",
            base_freight_cost=0.04,
            gas_score=0.65,  # Higher alignment with US
            tfrf_penalty=0.15,  # Lower trade fragmentation risk
            fvm_multiplier=1.10,  # Lower maritime risk
            ssp_flag="Private",
            cm_dependency=0.70,  # Moderate critical mineral dependency
            historical_loss_pct=0.10,  # 10% revenue loss if sanctions hit
            tariffs_percent=0.0
        )
    }


def calculate_npv_delta(sku: SKUInputs, china_supplier: SupplierData, 
                        vietnam_supplier: SupplierData) -> Dict[str, Any]:
    """
    Function 1: Financial Tradeoff Calculation
    
    Calculate Total Landed Cost (TLC) and NPV Delta
    - Adjusted Price (AP) = Price_unit × (1 + TFRF_penalty)
    - Adjusted Freight (AF) = Base Freight Cost × FVM_multiplier
    - Total Landed Cost (TLC) = AP + AF
    """
    quantity = sku.quantity_po_cycle
    
    # China (Current Supplier) Calculations
    ap_china = sku.current_price_unit * (1 + china_supplier.tfrf_penalty)
    af_china = china_supplier.base_freight_cost * china_supplier.fvm_multiplier
    tlc_china = ap_china + af_china
    tariffs_china = ap_china * (china_supplier.tariffs_percent / 100)
    total_cost_china = (tlc_china + tariffs_china) * quantity
    
    # Vietnam (Proposed Supplier) Calculations
    ap_vietnam = sku.proposed_price_unit * (1 + vietnam_supplier.tfrf_penalty)
    af_vietnam = vietnam_supplier.base_freight_cost * vietnam_supplier.fvm_multiplier
    tlc_vietnam = ap_vietnam + af_vietnam
    tariffs_vietnam = ap_vietnam * (vietnam_supplier.tariffs_percent / 100)
    total_cost_vietnam = (tlc_vietnam + tariffs_vietnam) * quantity
    
    # NPV Delta (savings/cost difference)
    npv_delta = total_cost_china - total_cost_vietnam  # Positive = savings from switching
    
    return {
        "npv_delta": npv_delta,
        "total_cost_china": total_cost_china,
        "total_cost_vietnam": total_cost_vietnam,
        "tlc_china_per_unit": tlc_china,
        "tlc_vietnam_per_unit": tlc_vietnam,
        "cost_breakdown": {
            "china": {
                "base_price": sku.current_price_unit,
                "adjusted_price_ap": ap_china,
                "tfrf_adjustment": china_supplier.tfrf_penalty,
                "base_freight": china_supplier.base_freight_cost,
                "adjusted_freight_af": af_china,
                "fvm_multiplier": china_supplier.fvm_multiplier,
                "tariffs": tariffs_china,
                "total_landed_cost_per_unit": tlc_china + tariffs_china,
                "total_cost_po_cycle": total_cost_china
            },
            "vietnam": {
                "base_price": sku.proposed_price_unit,
                "adjusted_price_ap": ap_vietnam,
                "tfrf_adjustment": vietnam_supplier.tfrf_penalty,
                "base_freight": vietnam_supplier.base_freight_cost,
                "adjusted_freight_af": af_vietnam,
                "fvm_multiplier": vietnam_supplier.fvm_multiplier,
                "tariffs": tariffs_vietnam,
                "total_landed_cost_per_unit": tlc_vietnam + tariffs_vietnam,
                "total_cost_po_cycle": total_cost_vietnam
            }
        }
    }


def calculate_composite_risk(supplier: SupplierData) -> Dict[str, Any]:
    """
    Function 2: Geopolitical Composite Risk Score
    
    Risk Score = (0.4 × GAS_Penalty + 0.3 × FVM_Score + 0.3 × CMDI_Score) × SSP_Multiplier
    
    Where:
    - GAS_Penalty = 1 - GAS_score (inverse of alignment)
    - FVM_Score = (FVM - 1) × 100
    - CMDI_Score = cm_dependency × 100
    - SSP_Multiplier = 1.2 if State-Subsidiary, else 1.0
    """
    # Calculate component scores (0-100 scale)
    gas_penalty = (1 - supplier.gas_score) * 100  # Higher penalty for lower alignment
    fvm_score = (supplier.fvm_multiplier - 1.0) * 100  # Score from FVM multiplier
    cmdi_score = supplier.cm_dependency * 100  # Direct use of dependency score
    
    # Apply weights
    weighted_base_score = (0.4 * gas_penalty + 0.3 * fvm_score + 0.3 * cmdi_score)
    
    # Apply SSP multiplier (amplify risk for State-Subsidiary)
    ssp_multiplier = 1.2 if supplier.ssp_flag == "State-Subsidiary" else 1.0
    composite_risk_score = weighted_base_score * ssp_multiplier
    
    # Cap at 100
    composite_risk_score = min(composite_risk_score, 100.0)
    
    return {
        "composite_risk_score": composite_risk_score,
        "gas_penalty": gas_penalty,
        "fvm_score": fvm_score,
        "cmdi_score": cmdi_score,
        "ssp_multiplier": ssp_multiplier,
        "components": {
            "gas_score": supplier.gas_score,
            "fvm_multiplier": supplier.fvm_multiplier,
            "cm_dependency": supplier.cm_dependency,
            "ssp_flag": supplier.ssp_flag
        }
    }


def calculate_expected_loss(npv_china: float, china_risk_score: float, 
                           historical_loss_pct: float) -> float:
    """
    Calculate Expected Loss if catastrophic sanction event occurs
    
    E_Loss = NPV_China × China_Risk_Score_normalized × Historical_Loss_Pct
    """
    # Normalize risk score to 0-1 range
    risk_score_normalized = china_risk_score / 100.0
    
    # Calculate expected loss
    expected_loss = npv_china * risk_score_normalized * historical_loss_pct
    
    return expected_loss


def generate_recommendation(sku: SKUInputs, npv_result: Dict[str, Any], 
                           china_risk: Dict[str, Any], vietnam_risk: Dict[str, Any],
                           china_supplier: SupplierData, 
                           vietnam_supplier: SupplierData) -> Dict[str, Any]:
    """
    Function 3: Weighted Decision and Scenario Output
    
    W_Decision = NPV_Δ - E_Loss
    
    Generate comprehensive recommendation with geopolitical insights
    """
    # Calculate Expected Loss based on China risk
    expected_loss = calculate_expected_loss(
        npv_china=npv_result["total_cost_china"],
        china_risk_score=china_risk["composite_risk_score"],
        historical_loss_pct=china_supplier.historical_loss_pct
    )
    
    # Calculate Weighted Decision
    w_decision = npv_result["npv_delta"] - expected_loss
    
    # Determine recommendation
    if w_decision > 0:
        recommendation = "SWITCH TO VIETNAM"
        recommendation_rationale = (
            f"Financial savings of ${npv_result['npv_delta']:,.0f} outweigh the expected loss "
            f"risk of ${expected_loss:,.0f}, resulting in a net benefit of ${w_decision:,.0f}."
        )
    else:
        recommendation = "STAY WITH CHINA (OR PURSUE ALTERNATIVE DIVERSIFICATION)"
        recommendation_rationale = (
            f"Expected loss risk of ${expected_loss:,.0f} exceeds the potential savings of "
            f"${npv_result['npv_delta']:,.0f}. Consider diversifying with additional suppliers "
            f"rather than a direct switch."
        )
    
    # Generate contingency warnings
    contingency_warnings = []
    
    # Targeted Sanctions Vulnerability Warning
    if china_supplier.cm_dependency > 0.75:
        contingency_warnings.append({
            "type": "Targeted Sanctions Vulnerability",
            "severity": "High",
            "message": (
                f"China supplier's Critical Mineral Dependency Index ({china_supplier.cm_dependency:.0%}) "
                f"indicates high vulnerability to supply-side elasticity targeting. Optimal sanctions "
                f"target goods supplied inelastically—PCBs with high CMDI scores represent prime targets "
                f"for strategic trade restrictions. This creates significant exposure risk even if "
                f"individual tariffs remain unchanged."
            )
        })
    
    # Strategic Shielding Risk
    if china_supplier.ssp_flag == "State-Subsidiary":
        contingency_warnings.append({
            "type": "Strategic Shielding Risk",
            "severity": "High",
            "message": (
                f"State-Subsidiary status increases the likelihood that targeted sanctions will "
                f"trigger government 'shielding' mechanisms. This shifts cost burden from the firm "
                f"to the target government, potentially distorting supply chain stability and "
                f"creating unpredictable regulatory disruptions."
            )
        })
    
    # Generate strategic scenarios for Vietnam alternative
    strategic_scenarios = [
        {
            "scenario": "Deterrence Scenario",
            "probability": "Moderate-High",
            "description": (
                "Geopolitical rivalry between global powers leads to pro-competition effects on "
                "trade infrastructure. Vietnam benefits from increased capacity, improved port "
                "facilities, and competitive pricing as alternative suppliers receive infrastructure "
                "investment. Expected outcome: Higher capacity, lower prices (15-20% additional "
                "savings potential), improved logistics reliability."
            ),
            "impact": "Positive"
        },
        {
            "scenario": "Accommodation Scenario",
            "probability": "Moderate",
            "description": (
                "Dual-power accommodation results in duopoly structures with managed competition. "
                "Vietnam capacity increases, but pricing remains more stable as global powers "
                "coordinate trade flows. Expected outcome: Increased capacity availability, "
                "moderate price improvements (5-10%), stable logistics environment."
            ),
            "impact": "Neutral-Positive"
        }
    ]
    
    # Generate legal/security questions
    legal_questions = []
    
    if china_supplier.ssp_flag == "State-Subsidiary":
        legal_questions.append({
            "category": "Legal/Regulatory",
            "question": (
                f"Given the {china_supplier.country} supplier's State-Subsidiary status (SSP), "
                f"what is our legal exposure and potential taxpayer burden if the supplier is "
                f"subjected to targeted sanctions? How does shielding risk affect our contractual "
                f"obligations and force majeure clauses?"
            )
        })
    
    if china_supplier.cm_dependency > 0.75:
        legal_questions.append({
            "category": "Supply Chain Security",
            "question": (
                f"With a Critical Mineral Dependency Index of {china_supplier.cm_dependency:.0%}, "
                f"what are our contingency options for component substitution or alternative sourcing "
                f"to reduce dependency on geopolitically sensitive materials? What is the timeline "
                f"and cost for qualifying alternative suppliers?"
            )
        })
    
    legal_questions.append({
        "category": "Strategic Planning",
        "question": (
            f"For SKU {sku.sku_id} with Strategic Importance Score {sku.strategic_importance_score}/10, "
            f"what is our acceptable risk threshold for supply disruption? Do we have adequate backup "
            f"inventory strategies and alternative supplier relationships to mitigate geopolitical shocks?"
        )
    })
    
    return {
        "recommendation": recommendation,
        "w_decision": w_decision,
        "recommendation_rationale": recommendation_rationale,
        "expected_loss": expected_loss,
        "contingency_warnings": contingency_warnings,
        "strategic_scenarios": strategic_scenarios,
        "legal_questions": legal_questions
    }


def generate_report(sku: SKUInputs, china_supplier: SupplierData, 
                   vietnam_supplier: SupplierData) -> Dict[str, Any]:
    """
    Main function to generate comprehensive decision report
    """
    # Calculate financial tradeoff
    npv_result = calculate_npv_delta(sku, china_supplier, vietnam_supplier)
    
    # Calculate risk scores
    china_risk = calculate_composite_risk(china_supplier)
    vietnam_risk = calculate_composite_risk(vietnam_supplier)
    
    # Generate recommendation
    recommendation_result = generate_recommendation(
        sku, npv_result, china_risk, vietnam_risk, 
        china_supplier, vietnam_supplier
    )
    
    # Compile comprehensive report
    report = {
        "sku_info": {
            "sku_id": sku.sku_id,
            "quantity_po_cycle": sku.quantity_po_cycle,
            "strategic_importance_score": sku.strategic_importance_score,
            "importer_country": sku.importer_country
        },
        "decision": {
            "recommendation": recommendation_result["recommendation"],
            "weighted_decision_value": recommendation_result["w_decision"],
            "recommendation_rationale": recommendation_result["recommendation_rationale"],
            "net_weighted_savings": recommendation_result["w_decision"] if recommendation_result["w_decision"] > 0 else 0
        },
        "cost_analysis": {
            "npv_delta": npv_result["npv_delta"],
            "total_cost_china": npv_result["total_cost_china"],
            "total_cost_vietnam": npv_result["total_cost_vietnam"],
            "cost_breakdown": npv_result["cost_breakdown"]
        },
        "risk_analysis": {
            "china_risk_score": china_risk["composite_risk_score"],
            "vietnam_risk_score": vietnam_risk["composite_risk_score"],
            "risk_delta": china_risk["composite_risk_score"] - vietnam_risk["composite_risk_score"],
            "china_risk_components": {
                "gas_penalty": china_risk["gas_penalty"],
                "fvm_score": china_risk["fvm_score"],
                "cmdi_score": china_risk["cmdi_score"],
                "ssp_multiplier": china_risk["ssp_multiplier"]
            },
            "vietnam_risk_components": {
                "gas_penalty": vietnam_risk["gas_penalty"],
                "fvm_score": vietnam_risk["fvm_score"],
                "cmdi_score": vietnam_risk["cmdi_score"],
                "ssp_multiplier": vietnam_risk["ssp_multiplier"]
            }
        },
        "expected_loss_analysis": {
            "expected_loss": recommendation_result["expected_loss"],
            "calculation_basis": (
                f"Based on China total cost of ${npv_result['total_cost_china']:,.0f}, "
                f"risk score of {china_risk['composite_risk_score']:.1f}/100, and "
                f"historical loss percentage of {china_supplier.historical_loss_pct:.0%}"
            )
        },
        "contingency_warnings": recommendation_result["contingency_warnings"],
        "strategic_scenarios": recommendation_result["strategic_scenarios"],
        "legal_security_questions": recommendation_result["legal_questions"]
    }
    
    return report


def print_report(report: Dict[str, Any]) -> None:
    """Pretty print the decision report"""
    print("=" * 80)
    print("PCB SOURCING DECISION ENGINE V2 - DECISION REPORT")
    print("=" * 80)
    print()
    
    # SKU Info
    print(f"SKU: {report['sku_info']['sku_id']}")
    print(f"PO Cycle Quantity: {report['sku_info']['quantity_po_cycle']:,} units")
    print(f"Strategic Importance: {report['sku_info']['strategic_importance_score']}/10")
    print()
    
    # Decision
    print("=" * 80)
    print("DECISION RECOMMENDATION")
    print("=" * 80)
    print(f"Recommendation: {report['decision']['recommendation']}")
    print(f"Weighted Decision Value: ${report['decision']['weighted_decision_value']:,.2f}")
    print(f"Net Weighted Savings: ${report['decision']['net_weighted_savings']:,.2f}")
    print()
    print(report['decision']['recommendation_rationale'])
    print()
    
    # Cost Analysis
    print("=" * 80)
    print("COST ANALYSIS")
    print("=" * 80)
    print(f"NPV Delta (Savings from Switch): ${report['cost_analysis']['npv_delta']:,.2f}")
    print(f"Total Cost (China): ${report['cost_analysis']['total_cost_china']:,.2f}")
    print(f"Total Cost (Vietnam): ${report['cost_analysis']['total_cost_vietnam']:,.2f}")
    print()
    print("Cost Breakdown per Unit:")
    print(f"  China TLC: ${report['cost_analysis']['cost_breakdown']['china']['total_landed_cost_per_unit']:.4f}")
    print(f"    - Base Price: ${report['cost_analysis']['cost_breakdown']['china']['base_price']:.2f}")
    print(f"    - TFRF Adjustment: {report['cost_analysis']['cost_breakdown']['china']['tfrf_adjustment']:.1%}")
    print(f"    - Adjusted Price (AP): ${report['cost_analysis']['cost_breakdown']['china']['adjusted_price_ap']:.2f}")
    print(f"    - Freight (FVM ×{report['cost_analysis']['cost_breakdown']['china']['fvm_multiplier']:.2f}): ${report['cost_analysis']['cost_breakdown']['china']['adjusted_freight_af']:.4f}")
    print(f"    - Tariffs: ${report['cost_analysis']['cost_breakdown']['china']['tariffs']:.4f}")
    print()
    print(f"  Vietnam TLC: ${report['cost_analysis']['cost_breakdown']['vietnam']['total_landed_cost_per_unit']:.4f}")
    print(f"    - Base Price: ${report['cost_analysis']['cost_breakdown']['vietnam']['base_price']:.2f}")
    print(f"    - TFRF Adjustment: {report['cost_analysis']['cost_breakdown']['vietnam']['tfrf_adjustment']:.1%}")
    print(f"    - Adjusted Price (AP): ${report['cost_analysis']['cost_breakdown']['vietnam']['adjusted_price_ap']:.2f}")
    print(f"    - Freight (FVM ×{report['cost_analysis']['cost_breakdown']['vietnam']['fvm_multiplier']:.2f}): ${report['cost_analysis']['cost_breakdown']['vietnam']['adjusted_freight_af']:.4f}")
    print(f"    - Tariffs: ${report['cost_analysis']['cost_breakdown']['vietnam']['tariffs']:.4f}")
    print()
    
    # Risk Analysis
    print("=" * 80)
    print("GEOPOLITICAL RISK ANALYSIS")
    print("=" * 80)
    print(f"China Risk Score: {report['risk_analysis']['china_risk_score']:.1f}/100")
    print(f"  - GAS Penalty: {report['risk_analysis']['china_risk_components']['gas_penalty']:.1f}")
    print(f"  - FVM Score: {report['risk_analysis']['china_risk_components']['fvm_score']:.1f}")
    print(f"  - CMDI Score: {report['risk_analysis']['china_risk_components']['cmdi_score']:.1f}")
    print(f"  - SSP Multiplier: ×{report['risk_analysis']['china_risk_components']['ssp_multiplier']:.1f}")
    print()
    print(f"Vietnam Risk Score: {report['risk_analysis']['vietnam_risk_score']:.1f}/100")
    print(f"  - GAS Penalty: {report['risk_analysis']['vietnam_risk_components']['gas_penalty']:.1f}")
    print(f"  - FVM Score: {report['risk_analysis']['vietnam_risk_components']['fvm_score']:.1f}")
    print(f"  - CMDI Score: {report['risk_analysis']['vietnam_risk_components']['cmdi_score']:.1f}")
    print(f"  - SSP Multiplier: ×{report['risk_analysis']['vietnam_risk_components']['ssp_multiplier']:.1f}")
    print()
    print(f"Risk Delta: {report['risk_analysis']['risk_delta']:.1f} points (lower is better for Vietnam)")
    print()
    
    # Expected Loss
    print("=" * 80)
    print("EXPECTED LOSS ANALYSIS")
    print("=" * 80)
    print(f"Expected Loss (if sanctions hit): ${report['expected_loss_analysis']['expected_loss']:,.2f}")
    print(report['expected_loss_analysis']['calculation_basis'])
    print()
    
    # Contingency Warnings
    if report['contingency_warnings']:
        print("=" * 80)
        print("CONTINGENCY WARNINGS")
        print("=" * 80)
        for warning in report['contingency_warnings']:
            print(f"[{warning['severity']}] {warning['type']}")
            print(f"  {warning['message']}")
            print()
    
    # Strategic Scenarios
    print("=" * 80)
    print("STRATEGIC SCENARIOS (Vietnam Alternative)")
    print("=" * 80)
    for scenario in report['strategic_scenarios']:
        print(f"Scenario: {scenario['scenario']} (Probability: {scenario['probability']}, Impact: {scenario['impact']})")
        print(f"  {scenario['description']}")
        print()
    
    # Legal/Security Questions
    if report['legal_security_questions']:
        print("=" * 80)
        print("LEGAL / SECURITY / REGULATORY QUESTIONS")
        print("=" * 80)
        for i, question in enumerate(report['legal_security_questions'], 1):
            print(f"{i}. [{question['category']}]")
            print(f"   {question['question']}")
            print()
    
    print("=" * 80)


def main():
    """Main execution function"""
    # Example SKU inputs
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
    
    # Also save as JSON
    report_json = json.dumps(report, indent=2, default=str)
    with open("decision_report.json", "w") as f:
        f.write(report_json)
    
    print("\nReport also saved to 'decision_report.json'")


if __name__ == "__main__":
    main()



