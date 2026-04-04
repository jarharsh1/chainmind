import json
import random
from collections import Counter

random.seed(42)

# ============ SUPPLIERS ============
suppliers = [
    {"id": "SUP-001", "name": "ShenZhen MicroTech", "country": "China", "on_time_delivery_pct": 92, "lead_time_days": 14},
    {"id": "SUP-002", "name": "Taiwan Semiconductor Co", "country": "Taiwan", "on_time_delivery_pct": 97, "lead_time_days": 21},
    {"id": "SUP-003", "name": "Seoul ChipWorks", "country": "South Korea", "on_time_delivery_pct": 95, "lead_time_days": 18},
    {"id": "SUP-004", "name": "Mumbai Electronics Ltd", "country": "India", "on_time_delivery_pct": 85, "lead_time_days": 12},
    {"id": "SUP-005", "name": "Stuttgart Precision GmbH", "country": "Germany", "on_time_delivery_pct": 98, "lead_time_days": 25},
    {"id": "SUP-006", "name": "Osaka Display Corp", "country": "Japan", "on_time_delivery_pct": 96, "lead_time_days": 20},
    {"id": "SUP-007", "name": "Bangkok Components", "country": "Thailand", "on_time_delivery_pct": 88, "lead_time_days": 15},
    {"id": "SUP-008", "name": "Hanoi Battery Systems", "country": "Vietnam", "on_time_delivery_pct": 84, "lead_time_days": 10},
    {"id": "SUP-009", "name": "Guadalajara Assemblies", "country": "Mexico", "on_time_delivery_pct": 87, "lead_time_days": 8},
    {"id": "SUP-010", "name": "Penang Silicon Works", "country": "Malaysia", "on_time_delivery_pct": 91, "lead_time_days": 16},
    {"id": "SUP-011", "name": "Helsinki Sensor Tech", "country": "Finland", "on_time_delivery_pct": 99, "lead_time_days": 28},
    {"id": "SUP-012", "name": "Dongguan Power Systems", "country": "China", "on_time_delivery_pct": 86, "lead_time_days": 11},
]

# ============ COMPONENTS ============
components = [
    {"id": "CMP-001", "name": "A14 Processor", "category": "Chipset", "unit_cost": 45.00, "criticality": "high"},
    {"id": "CMP-002", "name": "M2 SoC", "category": "Chipset", "unit_cost": 72.00, "criticality": "high"},
    {"id": "CMP-003", "name": "Snapdragon 8 Gen 3", "category": "Chipset", "unit_cost": 55.00, "criticality": "high"},
    {"id": "CMP-004", "name": "6.7 inch AMOLED Panel", "category": "Display", "unit_cost": 38.00, "criticality": "high"},
    {"id": "CMP-005", "name": "15.6 inch IPS LCD", "category": "Display", "unit_cost": 52.00, "criticality": "medium"},
    {"id": "CMP-006", "name": "10.9 inch Retina Display", "category": "Display", "unit_cost": 48.00, "criticality": "high"},
    {"id": "CMP-007", "name": "5000mAh Li-Po Cell", "category": "Battery", "unit_cost": 8.50, "criticality": "medium"},
    {"id": "CMP-008", "name": "8000mAh Li-Po Cell", "category": "Battery", "unit_cost": 12.00, "criticality": "medium"},
    {"id": "CMP-009", "name": "100Wh Laptop Battery", "category": "Battery", "unit_cost": 22.00, "criticality": "medium"},
    {"id": "CMP-010", "name": "8GB LPDDR5 RAM", "category": "Memory", "unit_cost": 18.00, "criticality": "high"},
    {"id": "CMP-011", "name": "16GB LPDDR5 RAM", "category": "Memory", "unit_cost": 32.00, "criticality": "high"},
    {"id": "CMP-012", "name": "256GB NVMe SSD", "category": "Storage", "unit_cost": 15.00, "criticality": "medium"},
    {"id": "CMP-013", "name": "512GB NVMe SSD", "category": "Storage", "unit_cost": 25.00, "criticality": "medium"},
    {"id": "CMP-014", "name": "50MP Camera Module", "category": "Sensor", "unit_cost": 14.00, "criticality": "medium"},
    {"id": "CMP-015", "name": "WiFi 7 Module", "category": "Connectivity", "unit_cost": 9.00, "criticality": "high"},
    {"id": "CMP-016", "name": "5G Modem Chip", "category": "Connectivity", "unit_cost": 28.00, "criticality": "high"},
    {"id": "CMP-017", "name": "USB-C Port Assembly", "category": "Connector", "unit_cost": 2.50, "criticality": "low"},
    {"id": "CMP-018", "name": "Haptic Feedback Motor", "category": "Sensor", "unit_cost": 3.20, "criticality": "low"},
    {"id": "CMP-019", "name": "Gorilla Glass 7 Panel", "category": "Display", "unit_cost": 11.00, "criticality": "medium"},
    {"id": "CMP-020", "name": "1TB NVMe SSD", "category": "Storage", "unit_cost": 42.00, "criticality": "low"},
]

# ============ PRODUCTS ============
products = [
    {"id": "PRD-001", "name": "Galaxy Ultra X", "category": "Smartphone", "price": 1199.99},
    {"id": "PRD-002", "name": "iPhone 16 Pro", "category": "Smartphone", "price": 1099.00},
    {"id": "PRD-003", "name": "Pixel 9", "category": "Smartphone", "price": 799.00},
    {"id": "PRD-004", "name": "ProBook Laptop 15", "category": "Laptop", "price": 1349.00},
    {"id": "PRD-005", "name": "AirSlim Ultrabook", "category": "Laptop", "price": 1599.00},
    {"id": "PRD-006", "name": "Tab Pro 11", "category": "Tablet", "price": 649.00},
    {"id": "PRD-007", "name": "StudyPad Basic", "category": "Tablet", "price": 329.00},
    {"id": "PRD-008", "name": "BudsPro Max", "category": "Wearable", "price": 249.00},
    {"id": "PRD-009", "name": "SmartWatch Ultra", "category": "Wearable", "price": 449.00},
    {"id": "PRD-010", "name": "HomeHub Display", "category": "Smart Home", "price": 199.00},
]

# ============ WAREHOUSES ============
warehouses = [
    {"id": "WH-001", "name": "ShenZhen Hub", "city": "Shenzhen", "country": "China", "capacity": 50000},
    {"id": "WH-002", "name": "Dubai Logistics Center", "city": "Dubai", "country": "UAE", "capacity": 30000},
    {"id": "WH-003", "name": "Rotterdam Port Warehouse", "city": "Rotterdam", "country": "Netherlands", "capacity": 40000},
    {"id": "WH-004", "name": "LA Distribution Center", "city": "Los Angeles", "country": "USA", "capacity": 45000},
    {"id": "WH-005", "name": "Singapore Free Trade Zone", "city": "Singapore", "country": "Singapore", "capacity": 25000},
    {"id": "WH-006", "name": "Mumbai Central Depot", "city": "Mumbai", "country": "India", "capacity": 20000},
]

# ============ RETAILERS ============
retailers = [
    {"id": "RET-001", "name": "TechMart Online", "city": "Global", "country": "Global", "type": "E-commerce"},
    {"id": "RET-002", "name": "ElectroCity Dubai Mall", "city": "Dubai", "country": "UAE", "type": "Physical Store"},
    {"id": "RET-003", "name": "Berlin Electronics Hub", "city": "Berlin", "country": "Germany", "type": "Physical Store"},
    {"id": "RET-004", "name": "BestBuy US", "city": "Multiple", "country": "USA", "type": "Chain Store"},
    {"id": "RET-005", "name": "Flipkart India", "city": "Bangalore", "country": "India", "type": "E-commerce"},
    {"id": "RET-006", "name": "JD.com", "city": "Beijing", "country": "China", "type": "E-commerce"},
    {"id": "RET-007", "name": "Currys UK", "city": "London", "country": "UK", "type": "Chain Store"},
    {"id": "RET-008", "name": "Croma India", "city": "Mumbai", "country": "India", "type": "Chain Store"},
]

# ============ RELATIONSHIPS ============

# Supplier → Component (SUPPLIES)
supplies = [
    {"supplier_id": "SUP-001", "component_id": "CMP-001", "volume_per_month": 5000},
    {"supplier_id": "SUP-002", "component_id": "CMP-001", "volume_per_month": 8000},
    {"supplier_id": "SUP-002", "component_id": "CMP-002", "volume_per_month": 10000},
    {"supplier_id": "SUP-003", "component_id": "CMP-003", "volume_per_month": 7000},
    {"supplier_id": "SUP-010", "component_id": "CMP-003", "volume_per_month": 3000},
    {"supplier_id": "SUP-006", "component_id": "CMP-004", "volume_per_month": 6000},
    {"supplier_id": "SUP-001", "component_id": "CMP-004", "volume_per_month": 4000},
    {"supplier_id": "SUP-006", "component_id": "CMP-005", "volume_per_month": 5000},
    {"supplier_id": "SUP-006", "component_id": "CMP-006", "volume_per_month": 7000},
    {"supplier_id": "SUP-005", "component_id": "CMP-006", "volume_per_month": 3000},
    {"supplier_id": "SUP-008", "component_id": "CMP-007", "volume_per_month": 15000},
    {"supplier_id": "SUP-012", "component_id": "CMP-007", "volume_per_month": 10000},
    {"supplier_id": "SUP-008", "component_id": "CMP-008", "volume_per_month": 8000},
    {"supplier_id": "SUP-012", "component_id": "CMP-009", "volume_per_month": 6000},
    {"supplier_id": "SUP-009", "component_id": "CMP-009", "volume_per_month": 4000},
    {"supplier_id": "SUP-003", "component_id": "CMP-010", "volume_per_month": 12000},
    {"supplier_id": "SUP-010", "component_id": "CMP-010", "volume_per_month": 8000},
    {"supplier_id": "SUP-003", "component_id": "CMP-011", "volume_per_month": 9000},
    {"supplier_id": "SUP-002", "component_id": "CMP-011", "volume_per_month": 5000},
    {"supplier_id": "SUP-010", "component_id": "CMP-012", "volume_per_month": 20000},
    {"supplier_id": "SUP-001", "component_id": "CMP-012", "volume_per_month": 15000},
    {"supplier_id": "SUP-010", "component_id": "CMP-013", "volume_per_month": 10000},
    {"supplier_id": "SUP-011", "component_id": "CMP-014", "volume_per_month": 9000},
    {"supplier_id": "SUP-007", "component_id": "CMP-015", "volume_per_month": 11000},
    {"supplier_id": "SUP-004", "component_id": "CMP-015", "volume_per_month": 7000},
    {"supplier_id": "SUP-002", "component_id": "CMP-016", "volume_per_month": 6000},
    {"supplier_id": "SUP-009", "component_id": "CMP-017", "volume_per_month": 25000},
    {"supplier_id": "SUP-004", "component_id": "CMP-017", "volume_per_month": 20000},
    {"supplier_id": "SUP-011", "component_id": "CMP-018", "volume_per_month": 8000},
    {"supplier_id": "SUP-007", "component_id": "CMP-018", "volume_per_month": 6000},
    {"supplier_id": "SUP-005", "component_id": "CMP-019", "volume_per_month": 12000},
    {"supplier_id": "SUP-001", "component_id": "CMP-020", "volume_per_month": 5000},
    {"supplier_id": "SUP-010", "component_id": "CMP-020", "volume_per_month": 4000},
]

# Component → Product (USED_IN)
used_in = [
    {"component_id": "CMP-003", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-004", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-007", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-011", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-013", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-014", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-016", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-019", "product_id": "PRD-001", "quantity": 1},
    {"component_id": "CMP-001", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-004", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-007", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-010", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-012", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-014", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-016", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-019", "product_id": "PRD-002", "quantity": 1},
    {"component_id": "CMP-001", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-004", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-007", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-010", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-012", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-015", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-017", "product_id": "PRD-003", "quantity": 1},
    {"component_id": "CMP-003", "product_id": "PRD-004", "quantity": 1},
    {"component_id": "CMP-005", "product_id": "PRD-004", "quantity": 1},
    {"component_id": "CMP-009", "product_id": "PRD-004", "quantity": 1},
    {"component_id": "CMP-011", "product_id": "PRD-004", "quantity": 1},
    {"component_id": "CMP-013", "product_id": "PRD-004", "quantity": 1},
    {"component_id": "CMP-015", "product_id": "PRD-004", "quantity": 1},
    {"component_id": "CMP-017", "product_id": "PRD-004", "quantity": 2},
    {"component_id": "CMP-002", "product_id": "PRD-005", "quantity": 1},
    {"component_id": "CMP-005", "product_id": "PRD-005", "quantity": 1},
    {"component_id": "CMP-009", "product_id": "PRD-005", "quantity": 1},
    {"component_id": "CMP-011", "product_id": "PRD-005", "quantity": 1},
    {"component_id": "CMP-020", "product_id": "PRD-005", "quantity": 1},
    {"component_id": "CMP-015", "product_id": "PRD-005", "quantity": 1},
    {"component_id": "CMP-017", "product_id": "PRD-005", "quantity": 2},
    {"component_id": "CMP-001", "product_id": "PRD-006", "quantity": 1},
    {"component_id": "CMP-006", "product_id": "PRD-006", "quantity": 1},
    {"component_id": "CMP-008", "product_id": "PRD-006", "quantity": 1},
    {"component_id": "CMP-010", "product_id": "PRD-006", "quantity": 1},
    {"component_id": "CMP-012", "product_id": "PRD-006", "quantity": 1},
    {"component_id": "CMP-015", "product_id": "PRD-006", "quantity": 1},
    {"component_id": "CMP-003", "product_id": "PRD-007", "quantity": 1},
    {"component_id": "CMP-006", "product_id": "PRD-007", "quantity": 1},
    {"component_id": "CMP-008", "product_id": "PRD-007", "quantity": 1},
    {"component_id": "CMP-010", "product_id": "PRD-007", "quantity": 1},
    {"component_id": "CMP-012", "product_id": "PRD-007", "quantity": 1},
    {"component_id": "CMP-018", "product_id": "PRD-008", "quantity": 2},
    {"component_id": "CMP-015", "product_id": "PRD-008", "quantity": 1},
    {"component_id": "CMP-001", "product_id": "PRD-009", "quantity": 1},
    {"component_id": "CMP-018", "product_id": "PRD-009", "quantity": 1},
    {"component_id": "CMP-015", "product_id": "PRD-009", "quantity": 1},
    {"component_id": "CMP-014", "product_id": "PRD-009", "quantity": 1},
    {"component_id": "CMP-006", "product_id": "PRD-010", "quantity": 1},
    {"component_id": "CMP-015", "product_id": "PRD-010", "quantity": 1},
    {"component_id": "CMP-017", "product_id": "PRD-010", "quantity": 1},
]

# Product → Warehouse (STORED_AT)
stored_at = [
    {"product_id": "PRD-001", "warehouse_id": "WH-001", "stock_quantity": 3500},
    {"product_id": "PRD-001", "warehouse_id": "WH-002", "stock_quantity": 1200},
    {"product_id": "PRD-001", "warehouse_id": "WH-005", "stock_quantity": 800},
    {"product_id": "PRD-002", "warehouse_id": "WH-001", "stock_quantity": 5000},
    {"product_id": "PRD-002", "warehouse_id": "WH-004", "stock_quantity": 3000},
    {"product_id": "PRD-002", "warehouse_id": "WH-003", "stock_quantity": 2000},
    {"product_id": "PRD-003", "warehouse_id": "WH-004", "stock_quantity": 4000},
    {"product_id": "PRD-003", "warehouse_id": "WH-001", "stock_quantity": 2500},
    {"product_id": "PRD-004", "warehouse_id": "WH-003", "stock_quantity": 1800},
    {"product_id": "PRD-004", "warehouse_id": "WH-004", "stock_quantity": 2200},
    {"product_id": "PRD-005", "warehouse_id": "WH-001", "stock_quantity": 1500},
    {"product_id": "PRD-005", "warehouse_id": "WH-003", "stock_quantity": 1000},
    {"product_id": "PRD-006", "warehouse_id": "WH-002", "stock_quantity": 2000},
    {"product_id": "PRD-006", "warehouse_id": "WH-005", "stock_quantity": 1500},
    {"product_id": "PRD-006", "warehouse_id": "WH-006", "stock_quantity": 1800},
    {"product_id": "PRD-007", "warehouse_id": "WH-006", "stock_quantity": 3000},
    {"product_id": "PRD-007", "warehouse_id": "WH-002", "stock_quantity": 2500},
    {"product_id": "PRD-008", "warehouse_id": "WH-001", "stock_quantity": 8000},
    {"product_id": "PRD-008", "warehouse_id": "WH-004", "stock_quantity": 5000},
    {"product_id": "PRD-008", "warehouse_id": "WH-005", "stock_quantity": 3000},
    {"product_id": "PRD-009", "warehouse_id": "WH-003", "stock_quantity": 2000},
    {"product_id": "PRD-009", "warehouse_id": "WH-002", "stock_quantity": 1500},
    {"product_id": "PRD-010", "warehouse_id": "WH-004", "stock_quantity": 4000},
    {"product_id": "PRD-010", "warehouse_id": "WH-006", "stock_quantity": 2500},
]

# Warehouse → Retailer (SHIPS_TO)
ships_to = [
    {"warehouse_id": "WH-001", "retailer_id": "RET-006", "mode": "truck", "cost_per_unit": 1.20, "transit_days": 2},
    {"warehouse_id": "WH-001", "retailer_id": "RET-001", "mode": "sea", "cost_per_unit": 3.50, "transit_days": 18},
    {"warehouse_id": "WH-001", "retailer_id": "RET-005", "mode": "sea", "cost_per_unit": 4.00, "transit_days": 12},
    {"warehouse_id": "WH-002", "retailer_id": "RET-002", "mode": "truck", "cost_per_unit": 0.80, "transit_days": 1},
    {"warehouse_id": "WH-002", "retailer_id": "RET-005", "mode": "sea", "cost_per_unit": 3.00, "transit_days": 7},
    {"warehouse_id": "WH-002", "retailer_id": "RET-008", "mode": "sea", "cost_per_unit": 2.50, "transit_days": 5},
    {"warehouse_id": "WH-003", "retailer_id": "RET-003", "mode": "truck", "cost_per_unit": 1.50, "transit_days": 1},
    {"warehouse_id": "WH-003", "retailer_id": "RET-007", "mode": "truck", "cost_per_unit": 2.00, "transit_days": 2},
    {"warehouse_id": "WH-003", "retailer_id": "RET-001", "mode": "air", "cost_per_unit": 8.00, "transit_days": 3},
    {"warehouse_id": "WH-004", "retailer_id": "RET-004", "mode": "truck", "cost_per_unit": 1.00, "transit_days": 2},
    {"warehouse_id": "WH-004", "retailer_id": "RET-001", "mode": "air", "cost_per_unit": 7.50, "transit_days": 2},
    {"warehouse_id": "WH-005", "retailer_id": "RET-006", "mode": "sea", "cost_per_unit": 2.80, "transit_days": 5},
    {"warehouse_id": "WH-005", "retailer_id": "RET-001", "mode": "air", "cost_per_unit": 6.00, "transit_days": 3},
    {"warehouse_id": "WH-005", "retailer_id": "RET-002", "mode": "sea", "cost_per_unit": 3.20, "transit_days": 6},
    {"warehouse_id": "WH-006", "retailer_id": "RET-005", "mode": "truck", "cost_per_unit": 0.90, "transit_days": 2},
    {"warehouse_id": "WH-006", "retailer_id": "RET-008", "mode": "truck", "cost_per_unit": 0.70, "transit_days": 1},
]

# ============ SAVE TO JSON ============
data = {
    "suppliers": suppliers,
    "components": components,
    "products": products,
    "warehouses": warehouses,
    "retailers": retailers,
    "supplies": supplies,
    "used_in": used_in,
    "stored_at": stored_at,
    "ships_to": ships_to,
}

with open("data/supply_chain_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Data generated successfully!")
print(f"  Suppliers:      {len(suppliers)}")
print(f"  Components:     {len(components)}")
print(f"  Products:       {len(products)}")
print(f"  Warehouses:     {len(warehouses)}")
print(f"  Retailers:      {len(retailers)}")
print(f"  SUPPLIES rels:  {len(supplies)}")
print(f"  USED_IN rels:   {len(used_in)}")
print(f"  STORED_AT rels: {len(stored_at)}")
print(f"  SHIPS_TO rels:  {len(ships_to)}")

# Single-source risk analysis
supplier_count = Counter(s["component_id"] for s in supplies)
single_source = [cid for cid, count in supplier_count.items() if count == 1]
print(f"\n  Single-source components: {len(single_source)}")
for cid in single_source:
    comp = next(c for c in components if c["id"] == cid)
    sup = next(s for s in supplies if s["component_id"] == cid)
    supplier = next(s for s in suppliers if s["id"] == sup["supplier_id"])
    print(f"     {comp['name']} <-- only from {supplier['name']}")