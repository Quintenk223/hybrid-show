"""Test decision engine with real database data"""
from data_sources import DataAdapter
from decision_engine import SKUInputs, SupplierData, generate_report, print_report

print("=" * 80)
print("Testing Decision Engine with Real Database Data")
print("=" * 80)
print()

# Initialize adapter
adapter = DataAdapter()

# Create test SKU
sku = SKUInputs(
    sku_id="PCB-TEST-001",
    quantity_po_cycle=50000,
    current_price_unit=3.50,
    proposed_price_unit=3.20,
    current_lead_time_days=45,
    proposed_lead_time_days=55,
    strategic_importance_score=8
)

print("1. Fetching Country-Level Supplier Data from Database:")
print("-" * 80)

# Get data from database
china_dict = adapter.get_country_level_supplier_data("China", "USA")
vietnam_dict = adapter.get_country_level_supplier_data("Vietnam", "USA")

print(f"China Data:")
print(f"  GAS Score: {china_dict.get('gas_score', 'N/A')}")
print(f"  TFRF Penalty: {china_dict.get('tfrf_penalty', 'N/A')}")
print(f"  CMDI: {china_dict.get('cm_dependency', 'N/A')}")
print(f"  FVM Multiplier: {china_dict.get('fvm_multiplier', 'N/A')}")

print(f"\nVietnam Data:")
print(f"  GAS Score: {vietnam_dict.get('gas_score', 'N/A')}")
print(f"  TFRF Penalty: {vietnam_dict.get('tfrf_penalty', 'N/A')}")
print(f"  CMDI: {vietnam_dict.get('cm_dependency', 'N/A')}")
print(f"  FVM Multiplier: {vietnam_dict.get('fvm_multiplier', 'N/A')}")

print("\n2. Converting to SupplierData Objects:")
print("-" * 80)
china = SupplierData(**china_dict)
vietnam = SupplierData(**vietnam_dict)
print("[OK] SupplierData objects created successfully")

print("\n3. Running Decision Engine Analysis:")
print("-" * 80)
report = generate_report(sku, china, vietnam)

print(f"\n[SUCCESS] Analysis Complete!")
print(f"\nRecommendation: {report['decision']['recommendation']}")
print(f"Net Weighted Savings: ${report['decision']['net_weighted_savings']:,.2f}")
print(f"NPV Delta: ${report['cost_analysis']['npv_delta']:,.2f}")
print(f"China Risk Score: {report['risk_analysis']['china_risk_score']:.1f}/100")
print(f"Vietnam Risk Score: {report['risk_analysis']['vietnam_risk_score']:.1f}/100")

print("\n" + "=" * 80)
print("Full Report:")
print("=" * 80)
print_report(report)

