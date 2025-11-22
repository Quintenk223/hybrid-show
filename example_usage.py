"""
Example usage of the Decision Engine V2
Demonstrates how to use the engine with different SKU inputs
"""

from decision_engine import (
    SKUInputs,
    generate_report,
    print_report,
    get_mock_supplier_data,
    json
)


def example_1_basic_usage():
    """Example 1: Basic usage with standard inputs"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage")
    print("="*80 + "\n")
    
    sku = SKUInputs(
        sku_id="PCB-XYZ-101",
        quantity_po_cycle=50000,
        current_price_unit=3.50,
        proposed_price_unit=3.20,
        current_lead_time_days=45,
        proposed_lead_time_days=55,
        strategic_importance_score=8
    )
    
    suppliers = get_mock_supplier_data()
    report = generate_report(sku, suppliers["china"], suppliers["vietnam"])
    print_report(report)


def example_2_high_volume():
    """Example 2: High volume order with larger cost differences"""
    print("\n" + "="*80)
    print("EXAMPLE 2: High Volume Order")
    print("="*80 + "\n")
    
    sku = SKUInputs(
        sku_id="PCB-HIGH-VOL-500",
        quantity_po_cycle=200000,  # High volume
        current_price_unit=5.00,
        proposed_price_unit=4.50,  # Larger price difference
        current_lead_time_days=45,
        proposed_lead_time_days=55,
        strategic_importance_score=9
    )
    
    suppliers = get_mock_supplier_data()
    report = generate_report(sku, suppliers["china"], suppliers["vietnam"])
    
    # Just show decision summary
    print(f"SKU: {report['sku_info']['sku_id']}")
    print(f"Quantity: {report['sku_info']['quantity_po_cycle']:,} units")
    print(f"\nRecommendation: {report['decision']['recommendation']}")
    print(f"NPV Delta: ${report['cost_analysis']['npv_delta']:,.2f}")
    print(f"Net Weighted Savings: ${report['decision']['net_weighted_savings']:,.2f}")
    print(f"\nChina Risk Score: {report['risk_analysis']['china_risk_score']:.1f}/100")
    print(f"Vietnam Risk Score: {report['risk_analysis']['vietnam_risk_score']:.1f}/100")


def example_3_marginal_case():
    """Example 3: Marginal case where price difference is small"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Marginal Case (Small Price Difference)")
    print("="*80 + "\n")
    
    sku = SKUInputs(
        sku_id="PCB-MARGINAL-200",
        quantity_po_cycle=30000,
        current_price_unit=3.50,
        proposed_price_unit=3.48,  # Small price difference
        current_lead_time_days=45,
        proposed_lead_time_days=55,
        strategic_importance_score=6
    )
    
    suppliers = get_mock_supplier_data()
    report = generate_report(sku, suppliers["china"], suppliers["vietnam"])
    
    print(f"SKU: {report['sku_info']['sku_id']}")
    print(f"Recommendation: {report['decision']['recommendation']}")
    print(f"NPV Delta: ${report['cost_analysis']['npv_delta']:,.2f}")
    print(f"Expected Loss: ${report['expected_loss_analysis']['expected_loss']:,.2f}")
    print(f"Weighted Decision Value: ${report['decision']['weighted_decision_value']:,.2f}")
    print(f"\nRationale: {report['decision']['recommendation_rationale']}")


def example_4_json_export():
    """Example 4: Export to JSON for programmatic use"""
    print("\n" + "="*80)
    print("EXAMPLE 4: JSON Export for Programmatic Use")
    print("="*80 + "\n")
    
    sku = SKUInputs(
        sku_id="PCB-API-001",
        quantity_po_cycle=75000,
        current_price_unit=4.25,
        proposed_price_unit=3.95,
        current_lead_time_days=45,
        proposed_lead_time_days=55,
        strategic_importance_score=7
    )
    
    suppliers = get_mock_supplier_data()
    report = generate_report(sku, suppliers["china"], suppliers["vietnam"])
    
    # Export to JSON
    report_json = json.dumps(report, indent=2, default=str)
    
    output_file = "example_report.json"
    with open(output_file, "w") as f:
        f.write(report_json)
    
    print(f"Report generated and saved to: {output_file}")
    print(f"\nKey Metrics:")
    print(f"  Recommendation: {report['decision']['recommendation']}")
    print(f"  NPV Delta: ${report['cost_analysis']['npv_delta']:,.2f}")
    print(f"  Net Weighted Savings: ${report['decision']['net_weighted_savings']:,.2f}")
    print(f"  China Risk: {report['risk_analysis']['china_risk_score']:.1f}/100")
    print(f"  Vietnam Risk: {report['risk_analysis']['vietnam_risk_score']:.1f}/100")
    print(f"\nJSON structure available for integration with other systems.")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("DECISION ENGINE V2 - USAGE EXAMPLES")
    print("="*80)
    
    # Run examples
    example_1_basic_usage()
    example_2_high_volume()
    example_3_marginal_case()
    example_4_json_export()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")



