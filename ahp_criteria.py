"""
AHP (Analytic Hierarchy Process) Criteria and Weights for PCB Equipment Procurement
Based on FPCB industry expert consensus
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

# AHP Global Weights (from expert consensus)
AHP_GLOBAL_WEIGHTS = {
    "line_and_space": 0.182,  # Manufacturing Requirements
    "automatic_ops": 0.171,    # Equipment Specifications
    "mark_alignment_correction": 0.137,  # Manufacturing Requirements
    "process_speed": 0.112,    # Manufacturing Requirements
    "maintenance_cost": 0.062,  # Procurement Concerns
    "dual_stage": 0.057,       # Equipment Specifications
    "compatible_register": 0.057,  # Equipment Specifications
    "throughput": 0.054,       # Manufacturing Requirements
    "df_and_sr_in_one": 0.054,  # Equipment Specifications
    "part_durability": 0.046,  # Procurement Concerns
    "warranty": 0.036,         # Procurement Concerns
    "purchasing_costs": 0.032  # Procurement Concerns (Lowest - least important!)
}

# AHP Category Local Weights
AHP_CATEGORY_WEIGHTS = {
    "manufacturing_requirements": 0.545,  # Most important category
    "equipment_specifications": 0.279,
    "procurement_concerns": 0.176
}

# Criteria to Category mapping
CRITERIA_CATEGORY_MAP = {
    "line_and_space": "manufacturing_requirements",
    "automatic_ops": "equipment_specifications",
    "mark_alignment_correction": "manufacturing_requirements",
    "process_speed": "manufacturing_requirements",
    "maintenance_cost": "procurement_concerns",
    "dual_stage": "equipment_specifications",
    "compatible_register": "equipment_specifications",
    "throughput": "manufacturing_requirements",
    "df_and_sr_in_one": "equipment_specifications",
    "part_durability": "procurement_concerns",
    "warranty": "procurement_concerns",
    "purchasing_costs": "procurement_concerns"
}

# Top criteria that influence Strategic Importance Score
TOP_TECHNICAL_CRITERIA = [
    "line_and_space",  # 0.182
    "mark_alignment_correction"  # 0.137
]

@dataclass
class AHPSupplierScores:
    """AHP criteria scores for a supplier (0-1 scale, higher = better)"""
    supplier_id: str
    
    # Manufacturing Requirements (0.545 weight)
    line_and_space: float = 0.5  # Minimum feature size capability (0-1: 1 = excellent precision)
    mark_alignment_correction: float = 0.5  # Alignment precision (0-1: 1 = excellent)
    process_speed: float = 0.5  # Throughput/smooth process (0-1: 1 = fast/reliable)
    throughput: float = 0.5  # Overall throughput score
    
    # Equipment Specifications (0.279 weight)
    automatic_ops: float = 0.5  # Automation level (0-1: 1 = highly automated)
    dual_stage: float = 0.5  # Dual stage capability
    compatible_register: float = 0.5  # Compatibility score
    df_and_sr_in_one: float = 0.5  # Combined DF/SR capability
    
    # Procurement Concerns (0.176 weight)
    maintenance_cost: float = 0.5  # Maintenance cost efficiency (0-1: 1 = low cost/maintenance)
    part_durability: float = 0.5  # Durability score (0-1: 1 = highly durable)
    warranty: float = 0.5  # Warranty coverage (0-1: 1 = excellent warranty)
    purchasing_costs: float = 0.5  # Price competitiveness (0-1: 1 = low price) - LEAST IMPORTANT


def calculate_technical_viability_score(ahp_scores: AHPSupplierScores) -> Dict[str, Any]:
    """
    Calculate Technical Viability Score using AHP model
    
    V = Σ(W_i × S_i)
    
    Where:
    - V = Technical Viability Score
    - W_i = Global Weight of criterion i
    - S_i = Normalized score (0-1) for criterion i
    """
    score_dict = {
        'line_and_space': ahp_scores.line_and_space,
        'automatic_ops': ahp_scores.automatic_ops,
        'mark_alignment_correction': ahp_scores.mark_alignment_correction,
        'process_speed': ahp_scores.process_speed,
        'maintenance_cost': ahp_scores.maintenance_cost,
        'dual_stage': ahp_scores.dual_stage,
        'compatible_register': ahp_scores.compatible_register,
        'throughput': ahp_scores.throughput,
        'df_and_sr_in_one': ahp_scores.df_and_sr_in_one,
        'part_durability': ahp_scores.part_durability,
        'warranty': ahp_scores.warranty,
        'purchasing_costs': ahp_scores.purchasing_costs
    }
    
    # Calculate weighted sum
    v_score = sum(
        AHP_GLOBAL_WEIGHTS[criterion] * score_dict[criterion]
        for criterion in AHP_GLOBAL_WEIGHTS.keys()
    )
    
    # Calculate category scores
    category_scores = {
        'manufacturing_requirements': sum(
            AHP_GLOBAL_WEIGHTS[c] * score_dict[c]
            for c in AHP_GLOBAL_WEIGHTS.keys()
            if CRITERIA_CATEGORY_MAP[c] == 'manufacturing_requirements'
        ) / AHP_CATEGORY_WEIGHTS['manufacturing_requirements'],
        'equipment_specifications': sum(
            AHP_GLOBAL_WEIGHTS[c] * score_dict[c]
            for c in AHP_GLOBAL_WEIGHTS.keys()
            if CRITERIA_CATEGORY_MAP[c] == 'equipment_specifications'
        ) / AHP_CATEGORY_WEIGHTS['equipment_specifications'],
        'procurement_concerns': sum(
            AHP_GLOBAL_WEIGHTS[c] * score_dict[c]
            for c in AHP_GLOBAL_WEIGHTS.keys()
            if CRITERIA_CATEGORY_MAP[c] == 'procurement_concerns'
        ) / AHP_CATEGORY_WEIGHTS['procurement_concerns']
    }
    
    # Find top driver and detractor
    weighted_scores = {
        criterion: AHP_GLOBAL_WEIGHTS[criterion] * score_dict[criterion]
        for criterion in AHP_GLOBAL_WEIGHTS.keys()
    }
    
    top_driver = max(weighted_scores, key=weighted_scores.get)
    top_detractor = min(weighted_scores, key=weighted_scores.get)
    
    return {
        'technical_viability_score': v_score,
        'v_score_normalized': v_score,  # Already 0-1 range
        'category_scores': category_scores,
        'criterion_scores': score_dict,
        'weighted_contributions': weighted_scores,
        'top_driver': {
            'criterion': top_driver,
            'weight': AHP_GLOBAL_WEIGHTS[top_driver],
            'score': score_dict[top_driver],
            'contribution': weighted_scores[top_driver]
        },
        'top_detractor': {
            'criterion': top_detractor,
            'weight': AHP_GLOBAL_WEIGHTS[top_detractor],
            'score': score_dict[top_detractor],
            'contribution': weighted_scores[top_detractor]
        },
        'critical_technical_scores': {
            'line_and_space': score_dict['line_and_space'],
            'mark_alignment_correction': score_dict['mark_alignment_correction']
        }
    }


def adjust_strategic_importance_with_ahp(base_sis: int, ahp_scores: AHPSupplierScores) -> int:
    """
    Adjust Strategic Importance Score based on critical AHP criteria
    
    Line and Space (0.182) and Mark Alignment Correction (0.137) are mandatory
    for high-precision manufacturing. Low scores on these reduce SIS.
    """
    # Critical technical criteria
    line_space_score = ahp_scores.line_and_space
    alignment_score = ahp_scores.mark_alignment_correction
    
    # If critical capabilities are low, reduce SIS
    if line_space_score < 0.5 or alignment_score < 0.5:
        # Technical failure on critical criteria reduces importance
        reduction = int((1.0 - max(line_space_score, alignment_score)) * 3)
        adjusted_sis = max(1, base_sis - reduction)
        return adjusted_sis
    
    # High technical capability can increase SIS (up to 10)
    if line_space_score > 0.8 and alignment_score > 0.8:
        bonus = int((min(line_space_score, alignment_score) - 0.8) * 2)
        adjusted_sis = min(10, base_sis + bonus)
        return adjusted_sis
    
    return base_sis


def calculate_yield_risk_penalty(ahp_scores: AHPSupplierScores) -> float:
    """
    Calculate yield risk penalty multiplier for TLC
    
    Low scores on Line and Space and Mark Alignment Correction
    indicate potential scrap and yield loss
    """
    line_space_score = ahp_scores.line_and_space
    alignment_score = ahp_scores.mark_alignment_correction
    
    # Average of critical technical scores
    avg_critical_score = (line_space_score + alignment_score) / 2.0
    
    # Penalty: 1.0 (no penalty) to 1.2 (20% penalty for low precision)
    # Low precision = high scrap risk = cost multiplier
    yield_risk_multiplier = 1.0 + (1.0 - avg_critical_score) * 0.2
    
    return yield_risk_multiplier


def adjust_lfd_with_automation(base_lfd: float, automatic_ops_score: float) -> float:
    """
    Adjust Labor Friction Dispersion based on automation level
    
    Higher automation (Automatic Ops) reduces LFD risk
    """
    # Automation reduces labor dependency
    # Scale: 0.0 (manual) to 1.0 (fully automated)
    automation_reduction = automatic_ops_score * 0.3  # Max 30% reduction
    
    adjusted_lfd = max(0.1, base_lfd - (base_lfd * automation_reduction))
    
    return adjusted_lfd


def calculate_long_term_cost_multiplier(ahp_scores: AHPSupplierScores) -> float:
    """
    Calculate long-term cost multiplier based on maintenance, durability, warranty
    
    Incorporates Maintenance Cost (0.062), Part Durability (0.046), Warranty (0.036)
    """
    # Invert scores (higher score = lower cost/risk)
    maintenance_factor = 1.0 - (ahp_scores.maintenance_cost * 0.1)  # 10% max impact
    durability_factor = 1.0 - (ahp_scores.part_durability * 0.08)   # 8% max impact
    warranty_factor = 1.0 - (ahp_scores.warranty * 0.05)            # 5% max impact
    
    # Combined long-term cost multiplier
    ltc_multiplier = (maintenance_factor + durability_factor + warranty_factor) / 3.0
    
    return ltc_multiplier


def get_mock_ahp_scores(supplier_id: str) -> AHPSupplierScores:
    """Get mock AHP scores for a supplier"""
    # Default: average scores
    if "CHINA_ALPHA" in supplier_id or "ALPHA" in supplier_id:
        # State enterprise - better equipment but higher costs
        return AHPSupplierScores(
            supplier_id=supplier_id,
            line_and_space=0.75,  # Good precision
            automatic_ops=0.70,
            mark_alignment_correction=0.80,  # High precision
            process_speed=0.65,
            maintenance_cost=0.40,  # Higher maintenance cost
            dual_stage=0.70,
            compatible_register=0.65,
            throughput=0.70,
            df_and_sr_in_one=0.60,
            part_durability=0.75,
            warranty=0.70,
            purchasing_costs=0.30  # Higher price
        )
    elif "CHINA_BETA" in supplier_id or "BETA" in supplier_id:
        # Private - lower price, moderate technical capability
        return AHPSupplierScores(
            supplier_id=supplier_id,
            line_and_space=0.55,  # Moderate precision
            automatic_ops=0.50,
            mark_alignment_correction=0.50,  # Moderate precision
            process_speed=0.55,
            maintenance_cost=0.65,  # Lower maintenance cost
            dual_stage=0.50,
            compatible_register=0.55,
            throughput=0.60,
            df_and_sr_in_one=0.50,
            part_durability=0.60,
            warranty=0.55,
            purchasing_costs=0.75  # Lower price (advantage)
        )
    elif "VIETNAM" in supplier_id or "GAMMA" in supplier_id:
        # Vietnam - emerging, good automation, competitive
        return AHPSupplierScores(
            supplier_id=supplier_id,
            line_and_space=0.70,  # Good precision
            automatic_ops=0.75,  # High automation
            mark_alignment_correction=0.70,
            process_speed=0.75,
            maintenance_cost=0.60,
            dual_stage=0.65,
            compatible_register=0.70,
            throughput=0.75,
            df_and_sr_in_one=0.65,
            part_durability=0.70,
            warranty=0.65,
            purchasing_costs=0.70  # Competitive price
        )
    else:
        # Default average scores
        return AHPSupplierScores(supplier_id=supplier_id)


def format_criterion_name(criterion: str) -> str:
    """Format criterion name for display"""
    name_map = {
        "line_and_space": "Line and Space",
        "automatic_ops": "Automatic Operations",
        "mark_alignment_correction": "Mark Alignment Correction",
        "process_speed": "Process Speed",
        "maintenance_cost": "Maintenance Cost",
        "dual_stage": "Dual Stage",
        "compatible_register": "Compatible Register",
        "throughput": "Throughput",
        "df_and_sr_in_one": "DF and SR in One",
        "part_durability": "Part Durability",
        "warranty": "Warranty",
        "purchasing_costs": "Purchasing Costs"
    }
    return name_map.get(criterion, criterion.replace("_", " ").title())

