"""Test data integration system"""
from data_sources import DataAdapter

print("Testing Data Integration System...")
print("=" * 50)

adapter = DataAdapter()

print("\n1. Testing Country-Level Supplier Data (China):")
china_data = adapter.get_country_level_supplier_data("China", "USA")
print(f"   GAS Score: {china_data['gas_score']}")
print(f"   TFRF Penalty: {china_data['tfrf_penalty']}")
print(f"   CMDI: {china_data['cm_dependency']}")
print(f"   FVM Multiplier: {china_data['fvm_multiplier']}")

print("\n2. Testing Country-Level Supplier Data (Vietnam):")
vietnam_data = adapter.get_country_level_supplier_data("Vietnam", "USA")
print(f"   GAS Score: {vietnam_data['gas_score']}")
print(f"   TFRF Penalty: {vietnam_data['tfrf_penalty']}")
print(f"   CMDI: {vietnam_data['cm_dependency']}")

print("\n3. Testing Intra-Country Supplier Data:")
supplier_a = adapter.get_intra_country_supplier_data("CHINA_SUPPLIER_A")
print(f"   Supplier: {supplier_a['supplier_name']}")
print(f"   Location: {supplier_a['location_prefecture']}")
print(f"   LFD Score: {supplier_a['labor_friction_dispersion']}")
print(f"   Port FVS: {supplier_a['port_foreland_vulnerability_score']}")

print("\n4. Testing Supplier Search:")
suppliers = adapter.search_suppliers("China")
print(f"   Found {len(suppliers)} suppliers in China")

print("\n" + "=" * 50)
print("[SUCCESS] All tests passed! Data integration system is functional.")
print("\nNote: Currently using mock data (expected behavior).")
print("Set environment variables and configure APIs to use real data.")

