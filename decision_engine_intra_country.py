"""
Intra-Country Supplier Comparison Tool
Compares two suppliers within the same country (e.g., China Supplier A vs China Supplier B)
Focuses on firm-level stability, localized operational risk, and micro-level frictions
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass
from decision_engine import SKUInputs


@dataclass
class IntraCountrySupplierData:
    """Enhanced supplier data for intra-country comparison"""
    supplier_id: str
    supplier_name: str
    company_type: str  # "State Enterprise", "Subsidiary", "Private"
    is_strategic_jewel: bool  # Recognized "jewel" of the country
    location_prefecture: str  # Prefecture or commuting zone
    location_type: str  # "Coastal" or "Inland"
    port_cluster: str  # "Bohai Rim", "PRD", "YRD", etc.
    
    # Supplier Identity Metrics
    pcb_revenue_percent: float  # PCB as % of total revenue
    export_share_western: float  # Export share to Western-aligned countries (0-1)
    
    # Operational Metrics
    base_price_unit: float
    base_freight_cost: float
    labor_friction_dispersion: float  # LFD Score (higher = more volatility)
    wealth_efficiency_multiplier: float  # Coastal vs Inland efficiency (lower = better)
    migration_vulnerability: float  # Migration risk (0-1)
    
    # Logistics Metrics
    port_foreland_vulnerability_score: float  # FVS (0-100)
    capacity_deterrence_benefit: float  # Benefit from infrastructure rivalry (0-1)
    roundabout_trade_exposure: float  # Risk from complex trade patterns (0-1)
    
    # Historical/Operational
    historical_loss_pct: float  # Expected revenue loss % if sanctions hit
    tariffs_percent: float = 0.0


def calculate_ssp_score(supplier: IntraCountrySupplierData) -> float:
    """
    Calculate Strategic Shielding Potential (SSP) Score
    Higher SSP = more stable but potentially politically sensitive
    """
    base_ssp = 0.0
    
    # Company type base score
    if supplier.company_type == "State Enterprise":
        base_ssp = 0.7
    elif supplier.company_type == "Subsidiary":
        base_ssp = 0.5
    else:  # Private
        base_ssp = 0.2
    
    # Strategic jewel bonus
    if supplier.is_strategic_jewel:
        base_ssp += 0.2
    
    # Cap at 1.0
    return min(base_ssp, 1.0)


def calculate_core_product_vulnerability(supplier: IntraCountrySupplierData) -> float:
    """
    Core Product Vulnerability Index
    Higher PCB revenue % = higher vulnerability during downturns
    Firms reduce exports of core products to uncertain markets first
    """
    # Higher PCB % of revenue = higher penalty
    # Scale: 0-1, where 1 = 100% PCB revenue
    return supplier.pcb_revenue_percent / 100.0


def calculate_embargo_exposure(supplier: IntraCountrySupplierData) -> float:
    """
    Embargo Exposure and Adaptation Score
    Higher Western export reliance = higher vulnerability
    More diverse market portfolio = more resilient
    """
    # Invert so higher Western reliance = higher exposure (risk)
    return supplier.export_share_western


def calculate_labor_friction_penalty(supplier: IntraCountrySupplierData) -> float:
    """
    Labor Friction Dispersion (LFD) Penalty
    Higher LFD = greater payroll volatility and less stable labor costs
    LFD dispersion is substantially higher (1.18x) than output frictions
    """
    # Scale LFD to 0-1 penalty (assuming LFD range 0-2, with 1.18 as high)
    normalized_lfd = min(supplier.labor_friction_dispersion / 2.0, 1.0)
    return normalized_lfd


def calculate_wealth_efficiency_adjustment(supplier: IntraCountrySupplierData) -> float:
    """
    Wealth-Adjusted Efficiency Multiplier
    Frictions are less dispersed in richer (coastal) prefectures
    Documented difference: 0.085 (coastal) vs 0.108 (inland)
    """
    # Coastal = lower friction = better efficiency
    if supplier.location_type == "Coastal":
        return 0.085  # Lower friction
    else:  # Inland
        return 0.108  # Higher friction


def calculate_migration_vulnerability_penalty(supplier: IntraCountrySupplierData) -> float:
    """
    Migration Vulnerability Analysis
    Inland suppliers vulnerable to labor outflow during policy shifts
    """
    return supplier.migration_vulnerability


def calculate_port_foreland_risk(supplier: IntraCountrySupplierData) -> float:
    """
    Port Cluster Foreland Vulnerability Score (FVS)
    Higher FVS = port cluster exposed to geopolitical tension
    """
    # Already a 0-100 score, normalize to 0-1
    return supplier.port_foreland_vulnerability_score / 100.0


def calculate_operational_stability_score(supplier: IntraCountrySupplierData) -> Dict[str, float]:
    """
    Calculate comprehensive operational stability score
    Combines all micro-level friction metrics
    """
    lfd_penalty = calculate_labor_friction_penalty(supplier)
    wealth_efficiency = calculate_wealth_efficiency_adjustment(supplier)
    migration_penalty = calculate_migration_vulnerability_penalty(supplier)
    
    # Weighted operational risk (higher = worse)
    operational_risk = (
        0.4 * lfd_penalty +  # Labor friction volatility
        0.3 * (wealth_efficiency / 0.108) +  # Inefficiency (normalized to max)
        0.3 * migration_penalty  # Migration vulnerability
    )
    
    return {
        "operational_risk_score": operational_risk * 100,  # Scale to 0-100
        "labor_friction_dispersion": lfd_penalty * 100,
        "wealth_efficiency_penalty": (wealth_efficiency / 0.108) * 100,
        "migration_vulnerability": migration_penalty * 100
    }


def calculate_supplier_identity_risk(supplier: IntraCountrySupplierData) -> Dict[str, float]:
    """
    Calculate Supplier Identity and Political Exposure Risk
    Combines SSP, Core Product Vulnerability, and Embargo Exposure
    """
    ssp_score = calculate_ssp_score(supplier)
    core_vulnerability = calculate_core_product_vulnerability(supplier)
    embargo_exposure = calculate_embargo_exposure(supplier)
    
    # SSP paradox: High SSP = stable but politically sensitive
    # For risk assessment: Low SSP suppliers are more vulnerable to disruption
    # High SSP suppliers may be shielded but are more likely targets
    ssp_vulnerability = 1.0 - ssp_score  # Invert: high SSP = lower vulnerability to disruption
    
    # Weighted identity risk
    identity_risk = (
        0.3 * (1.0 - ssp_vulnerability) +  # SSP vulnerability (inverted)
        0.4 * core_vulnerability +  # Core product concentration
        0.3 * embargo_exposure  # Western market reliance
    )
    
    return {
        "identity_risk_score": identity_risk * 100,
        "ssp_score": ssp_score * 100,
        "core_product_vulnerability": core_vulnerability * 100,
        "embargo_exposure": embargo_exposure * 100,
        "is_shielded": ssp_score > 0.6
    }


def calculate_logistics_risk(supplier: IntraCountrySupplierData) -> Dict[str, float]:
    """
    Calculate Localized Logistics and Infrastructure Risk
    """
    port_risk = calculate_port_foreland_risk(supplier)
    
    # Invert capacity deterrence (higher benefit = lower risk)
    capacity_benefit = supplier.capacity_deterrence_benefit
    capacity_risk = 1.0 - capacity_benefit
    
    # Roundabout trade exposure (direct risk)
    roundabout_risk = supplier.roundabout_trade_exposure
    
    # Weighted logistics risk
    logistics_risk = (
        0.4 * port_risk +
        0.3 * capacity_risk +
        0.3 * roundabout_risk
    )
    
    return {
        "logistics_risk_score": logistics_risk * 100,
        "port_foreland_vulnerability": port_risk * 100,
        "capacity_risk": capacity_risk * 100,
        "roundabout_trade_risk": roundabout_risk * 100
    }


def calculate_adjusted_costs(sku: SKUInputs, supplier: IntraCountrySupplierData) -> Dict[str, float]:
    """
    Calculate adjusted costs with all friction and efficiency adjustments
    """
    quantity = sku.quantity_po_cycle
    
    # Base costs
    base_price_cost = supplier.base_price_unit * quantity
    base_freight_cost = supplier.base_freight_cost * quantity
    tariffs = base_price_cost * (supplier.tariffs_percent / 100)
    
    # Apply wealth-adjusted efficiency multiplier
    wealth_efficiency = calculate_wealth_efficiency_adjustment(supplier)
    efficiency_adjustment = 1.0 + wealth_efficiency
    
    # Apply labor friction volatility (adds uncertainty premium)
    lfd_penalty = calculate_labor_friction_penalty(supplier)
    labor_volatility_premium = 1.0 + (lfd_penalty * 0.1)  # 10% max premium for high LFD
    
    # Adjusted price cost
    adjusted_price_cost = base_price_cost * efficiency_adjustment * labor_volatility_premium
    
    # Port vulnerability affects freight
    port_risk_multiplier = 1.0 + (calculate_port_foreland_risk(supplier) * 0.15)  # 15% max for high port risk
    adjusted_freight_cost = base_freight_cost * port_risk_multiplier
    
    total_cost = adjusted_price_cost + adjusted_freight_cost + tariffs
    
    return {
        "base_price_cost": base_price_cost,
        "adjusted_price_cost": adjusted_price_cost,
        "base_freight_cost": base_freight_cost,
        "adjusted_freight_cost": adjusted_freight_cost,
        "tariffs": tariffs,
        "total_cost": total_cost,
        "total_cost_per_unit": total_cost / quantity,
        "efficiency_adjustment": efficiency_adjustment,
        "labor_volatility_premium": labor_volatility_premium,
        "port_risk_multiplier": port_risk_multiplier
    }


def generate_intra_country_recommendation(
    sku: SKUInputs,
    supplier_a: IntraCountrySupplierData,
    supplier_b: IntraCountrySupplierData
) -> Dict[str, Any]:
    """
    Main function to generate intra-country supplier comparison recommendation
    """
    # Calculate costs for both suppliers
    costs_a = calculate_adjusted_costs(sku, supplier_a)
    costs_b = calculate_adjusted_costs(sku, supplier_b)
    
    # Calculate NPV delta (savings from switching to Supplier B)
    npv_delta = costs_a["total_cost"] - costs_b["total_cost"]
    
    # Calculate risk scores
    identity_risk_a = calculate_supplier_identity_risk(supplier_a)
    identity_risk_b = calculate_supplier_identity_risk(supplier_b)
    
    operational_stability_a = calculate_operational_stability_score(supplier_a)
    operational_stability_b = calculate_operational_stability_score(supplier_b)
    
    logistics_risk_a = calculate_logistics_risk(supplier_a)
    logistics_risk_b = calculate_logistics_risk(supplier_b)
    
    # Composite risk scores (weighted)
    composite_risk_a = (
        0.4 * identity_risk_a["identity_risk_score"] +
        0.3 * operational_stability_a["operational_risk_score"] +
        0.3 * logistics_risk_a["logistics_risk_score"]
    )
    
    composite_risk_b = (
        0.4 * identity_risk_b["identity_risk_score"] +
        0.3 * operational_stability_b["operational_risk_score"] +
        0.3 * logistics_risk_b["logistics_risk_score"]
    )
    
    # Calculate expected loss for Supplier A (higher risk)
    higher_risk_score = max(composite_risk_a, composite_risk_b)
    higher_risk_supplier = supplier_a if composite_risk_a > composite_risk_b else supplier_b
    higher_risk_cost = costs_a["total_cost"] if composite_risk_a > composite_risk_b else costs_b["total_cost"]
    
    expected_loss = higher_risk_cost * (higher_risk_score / 100.0) * higher_risk_supplier.historical_loss_pct
    
    # Weighted decision
    risk_adjustment = abs(composite_risk_a - composite_risk_b) / 100.0 * expected_loss
    w_decision = npv_delta - risk_adjustment
    
    # Generate recommendation
    if w_decision > 0:
        recommendation = f"SWITCH TO {supplier_b.supplier_name.upper()}"
        rationale = (
            f"Financial savings of ${npv_delta:,.0f} outweigh the risk-adjusted expected loss "
            f"of ${risk_adjustment:,.0f}, resulting in a net benefit of ${w_decision:,.0f}. "
            f"{supplier_b.supplier_name} demonstrates better operational stability and lower "
            f"exposure to localized risks."
        )
    else:
        recommendation = f"STAY WITH {supplier_a.supplier_name.upper()}"
        rationale = (
            f"Risk-adjusted expected loss of ${risk_adjustment:,.0f} exceeds the potential "
            f"savings of ${npv_delta:,.0f}. {supplier_a.supplier_name} offers better stability "
            f"despite potentially higher costs. Consider renegotiating terms rather than switching."
        )
    
    # Generate contingency warnings
    contingency_warnings = []
    
    if identity_risk_a["is_shielded"] or identity_risk_b["is_shielded"]:
        shielded_supplier = supplier_a if identity_risk_a["is_shielded"] else supplier_b
        contingency_warnings.append({
            "type": "Strategic Shielding Risk",
            "severity": "Medium-High",
            "message": (
                f"{shielded_supplier.supplier_name} has high Strategic Shielding Potential (SSP: "
                f"{identity_risk_a['ssp_score']:.0f}% if A, {identity_risk_b['ssp_score']:.0f}% if B). "
                f"High SSP suppliers may be protected by government intervention during crises, but this "
                f"can lead to unpredictable pricing shifts, capacity prioritization changes, or taxpayer-funded "
                f"bailouts that distort future market dynamics. Incorporate risk of government-mandated "
                f"interventions in capacity planning."
            )
        })
    
    if operational_stability_a["labor_friction_dispersion"] > 70 or operational_stability_b["labor_friction_dispersion"] > 70:
        high_lfd_supplier = supplier_a if operational_stability_a["labor_friction_dispersion"] > 70 else supplier_b
        contingency_warnings.append({
            "type": "Labor Friction Volatility",
            "severity": "High",
            "message": (
                f"{high_lfd_supplier.supplier_name} operates in a region with high Labor Friction "
                f"Dispersion (LFD: {operational_stability_a['labor_friction_dispersion']:.0f}% vs "
                f"{operational_stability_b['labor_friction_dispersion']:.0f}%). Input markets are "
                f"significantly more distorted than output markets. This indicates high payroll volatility "
                f"and unstable labor costs. Increase recommended safety stock by 20-30 days to mitigate "
                f"production disruptions from labor market shocks."
            )
        })
    
    # Generate legal/security questions
    legal_questions = []
    
    low_ssp_supplier = supplier_a if identity_risk_a["ssp_score"] < identity_risk_b["ssp_score"] else supplier_b
    legal_questions.append({
        "category": "Trade Finance",
        "question": (
            f"Does {low_ssp_supplier.supplier_name} (low SSP: {identity_risk_a['ssp_score']:.0f}% vs "
            f"{identity_risk_b['ssp_score']:.0f}%) rely heavily on trade finance instruments for US export? "
            f"Reduced availability of trade finance due to political uncertainty is a known channel for "
            f"'friendly fire' effects that can disrupt operations even without direct sanctions."
        )
    })
    
    if supplier_a.export_share_western > 0.5 or supplier_b.export_share_western > 0.5:
        high_export_supplier = supplier_a if supplier_a.export_share_western > 0.5 else supplier_b
        legal_questions.append({
            "category": "Market Diversification",
            "question": (
                f"{high_export_supplier.supplier_name} has high Western market reliance "
                f"({high_export_supplier.export_share_western:.0%}). Firms with concentrated export portfolios "
                f"are more vulnerable to embargo effects. What is the timeline for diversifying export markets, "
                f"and how does this affect their capacity allocation for our orders?"
            )
        })
    
    legal_questions.append({
        "category": "Operational Stability",
        "question": (
            f"Given the location difference between {supplier_a.supplier_name} ({supplier_a.location_type}) "
            f"and {supplier_b.supplier_name} ({supplier_b.location_type}), what are the implications of "
            f"potential migration policy changes? Suppliers in less-developed regions face higher vulnerability "
            f"to labor outflow during policy shifts."
        )
    })
    
    # Generate friction heatmap data
    friction_heatmap = {
        "supplier_a": {
            "name": supplier_a.supplier_name,
            "labor_friction_dispersion": operational_stability_a["labor_friction_dispersion"],
            "location": supplier_a.location_prefecture,
            "location_type": supplier_a.location_type,
            "operational_risk": operational_stability_a["operational_risk_score"]
        },
        "supplier_b": {
            "name": supplier_b.supplier_name,
            "labor_friction_dispersion": operational_stability_b["labor_friction_dispersion"],
            "location": supplier_b.location_prefecture,
            "location_type": supplier_b.location_type,
            "operational_risk": operational_stability_b["operational_risk_score"]
        },
        "key_insight": (
            "Input markets (labor) are significantly more distorted than output markets. "
            "High LFD indicates greater payroll volatility and operational instability."
        )
    }
    
    return {
        "sku_info": {
            "sku_id": sku.sku_id,
            "quantity_po_cycle": sku.quantity_po_cycle,
            "strategic_importance_score": sku.strategic_importance_score
        },
        "decision": {
            "recommendation": recommendation,
            "weighted_decision_value": w_decision,
            "recommendation_rationale": rationale,
            "net_weighted_savings": w_decision if w_decision > 0 else 0
        },
        "cost_analysis": {
            "npv_delta": npv_delta,
            "supplier_a_cost": costs_a["total_cost"],
            "supplier_b_cost": costs_b["total_cost"],
            "cost_breakdown": {
                "supplier_a": costs_a,
                "supplier_b": costs_b
            }
        },
        "risk_analysis": {
            "supplier_a": {
                "composite_risk_score": composite_risk_a,
                "identity_risk": identity_risk_a,
                "operational_stability": operational_stability_a,
                "logistics_risk": logistics_risk_a
            },
            "supplier_b": {
                "composite_risk_score": composite_risk_b,
                "identity_risk": identity_risk_b,
                "operational_stability": operational_stability_b,
                "logistics_risk": logistics_risk_b
            },
            "risk_delta": composite_risk_a - composite_risk_b
        },
        "friction_heatmap": friction_heatmap,
        "contingency_warnings": contingency_warnings,
        "legal_questions": legal_questions,
        "expected_loss": expected_loss,
        "risk_adjustment": risk_adjustment
    }


def get_mock_supplier_a() -> IntraCountrySupplierData:
    """Mock data for China Supplier A (State Enterprise, Coastal)"""
    return IntraCountrySupplierData(
        supplier_id="CHINA_SUPPLIER_A",
        supplier_name="ChinaTech State Manufacturing",
        company_type="State Enterprise",
        is_strategic_jewel=True,
        location_prefecture="Shanghai (YRD)",
        location_type="Coastal",
        port_cluster="YRD",
        pcb_revenue_percent=45.0,  # PCB is core product
        export_share_western=0.65,  # 65% to Western markets
        base_price_unit=3.50,
        base_freight_cost=0.05,
        labor_friction_dispersion=1.10,  # Moderate LFD
        wealth_efficiency_multiplier=0.085,  # Coastal efficiency
        migration_vulnerability=0.20,  # Low migration risk (coastal)
        port_foreland_vulnerability_score=75.0,  # High port risk (YRD exposed)
        capacity_deterrence_benefit=0.40,  # Moderate benefit
        roundabout_trade_exposure=0.30,  # Some complex trade patterns
        historical_loss_pct=0.25,
        tariffs_percent=25.0
    )


def get_mock_supplier_b() -> IntraCountrySupplierData:
    """Mock data for China Supplier B (Private, Inland)"""
    return IntraCountrySupplierData(
        supplier_id="CHINA_SUPPLIER_B",
        supplier_name="Shenzhen Precision Circuits",
        company_type="Private",
        is_strategic_jewel=False,
        location_prefecture="Shenzhen (PRD)",
        location_type="Coastal",
        port_cluster="PRD",
        pcb_revenue_percent=25.0,  # More diversified
        export_share_western=0.45,  # 45% to Western markets (more diversified)
        base_price_unit=3.25,
        base_freight_cost=0.04,
        labor_friction_dispersion=0.85,  # Lower LFD (better stability)
        wealth_efficiency_multiplier=0.085,  # Coastal efficiency
        migration_vulnerability=0.15,  # Low migration risk
        port_foreland_vulnerability_score=60.0,  # Lower port risk
        capacity_deterrence_benefit=0.60,  # Higher benefit from competition
        roundabout_trade_exposure=0.15,  # Less complex trade patterns
        historical_loss_pct=0.15,
        tariffs_percent=25.0
    )


if __name__ == "__main__":
    # Example usage
    sku = SKUInputs(
        sku_id="PCB-INTRA-COMP-001",
        quantity_po_cycle=50000,
        current_price_unit=3.50,
        proposed_price_unit=3.25,
        current_lead_time_days=45,
        proposed_lead_time_days=50,
        strategic_importance_score=8
    )
    
    supplier_a = get_mock_supplier_a()
    supplier_b = get_mock_supplier_b()
    
    report = generate_intra_country_recommendation(sku, supplier_a, supplier_b)
    
    print(json.dumps(report, indent=2, default=str))

