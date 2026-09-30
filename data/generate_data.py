"""
Synthetic supply-chain data generator for ChainMind.

Deterministic (fixed seed) so the graph is identical on every run and demo
questions always return the same answers. Emits a richer graph than the original
hand-written one, with:

  - deliberate SINGLE-SOURCE risks on critical components (great "risk" queries)
  - multi-sourcing with differing price / lead time / volume per supplier
  - richer attributes (supplier region + tier, component alt_supplier_count,
    warehouse utilization, per-edge unit price)
  - a couple of intentional bottlenecks (a near-full warehouse; a retailer
    served by a single warehouse)

Recognizable "hero" entities (Taiwan Semiconductor Co, Galaxy Ultra X,
Flipkart India, ...) are kept so the README sample questions resolve.

Emitted counts (see the summary printed at the end):
  ~48 suppliers · ~70 components · ~24 products · 10 warehouses · 12 retailers
"""

import json
import os
import random
from collections import Counter, defaultdict

random.seed(42)

# --------------------------------------------------------------------------- #
# Reference pools
# --------------------------------------------------------------------------- #
COUNTRY_REGION = {
    "China": "APAC", "Taiwan": "APAC", "South Korea": "APAC", "Japan": "APAC",
    "India": "APAC", "Thailand": "APAC", "Vietnam": "APAC", "Malaysia": "APAC",
    "Singapore": "APAC", "Germany": "EMEA", "Finland": "EMEA", "Ireland": "EMEA",
    "Israel": "EMEA", "USA": "AMER", "Mexico": "AMER", "Brazil": "AMER",
}
CITY_BY_COUNTRY = {
    "China": ["Shenzhen", "Dongguan", "Suzhou"], "Taiwan": ["Hsinchu", "Taipei"],
    "South Korea": ["Seoul", "Incheon"], "Japan": ["Osaka", "Tokyo"],
    "India": ["Mumbai", "Bengaluru", "Chennai"], "Thailand": ["Bangkok"],
    "Vietnam": ["Hanoi", "Da Nang"], "Malaysia": ["Penang"], "Singapore": ["Singapore"],
    "Germany": ["Stuttgart", "Dresden"], "Finland": ["Helsinki"], "Ireland": ["Dublin"],
    "Israel": ["Haifa"], "USA": ["Austin", "Phoenix"], "Mexico": ["Guadalajara"],
    "Brazil": ["Manaus"],
}
SUPPLIER_SUFFIX = [
    "MicroTech", "Semiconductor Co", "ChipWorks", "Electronics Ltd", "Precision GmbH",
    "Display Corp", "Components", "Battery Systems", "Assemblies", "Silicon Works",
    "Sensor Tech", "Power Systems", "Optics", "Fabrication", "Circuits", "Modules Inc",
]
COMPONENT_CATEGORIES = [
    "Chipset", "Display", "Battery", "Memory", "Storage", "Sensor",
    "Connectivity", "Connector", "Camera", "Audio", "Power", "Cooling",
]
COMPONENT_NAMES = {
    "Chipset": ["A{n} Processor", "M{n} SoC", "Snapdragon {n} Gen", "Tensor G{n}", "Exynos {n}"],
    "Display": ["{s}in AMOLED Panel", "{s}in IPS LCD", "{s}in Retina Display", "{s}in OLED Panel"],
    "Battery": ["{n}mAh Li-Po Cell", "{n}Wh Laptop Battery", "{n}mAh Graphene Cell"],
    "Memory": ["{n}GB LPDDR5 RAM", "{n}GB DDR5 RAM", "{n}GB LPDDR5X RAM"],
    "Storage": ["{n}GB NVMe SSD", "{n}TB NVMe SSD", "{n}GB UFS Storage"],
    "Sensor": ["Haptic Feedback Motor", "Gyroscope Module", "Accelerometer", "LiDAR Scanner"],
    "Connectivity": ["WiFi {n} Module", "5G Modem Chip", "Bluetooth {n} Chip", "UWB Chip"],
    "Connector": ["USB-C Port Assembly", "Lightning Port", "HDMI Port", "Audio Jack"],
    "Camera": ["{n}MP Camera Module", "{n}MP Ultrawide Cam", "ToF Camera", "{n}MP Selfie Cam"],
    "Audio": ["Stereo Speaker Unit", "Noise-Cancel Mic Array", "Piezo Buzzer"],
    "Power": ["{n}W Charging IC", "Power Management IC", "Wireless Charge Coil"],
    "Cooling": ["Vapor Chamber", "Graphite Heat Spreader", "Cooling Fan Module"],
}
CRITICAL_CATEGORIES = {"Chipset", "Display", "Memory", "Connectivity"}

PRODUCT_TEMPLATES = {
    "Smartphone": ["Chipset", "Display", "Battery", "Memory", "Storage", "Camera",
                   "Connectivity", "Connector", "Sensor"],
    "Laptop": ["Chipset", "Display", "Battery", "Memory", "Storage", "Connectivity",
               "Connector", "Cooling", "Audio"],
    "Tablet": ["Chipset", "Display", "Battery", "Memory", "Storage", "Connectivity", "Connector"],
    "Wearable": ["Chipset", "Battery", "Sensor", "Connectivity", "Display"],
    "Earbuds": ["Battery", "Audio", "Connectivity", "Sensor"],
    "Smart Home": ["Chipset", "Display", "Connectivity", "Connector", "Audio", "Power"],
    "Monitor": ["Display", "Connector", "Power", "Cooling"],
    "Console": ["Chipset", "Memory", "Storage", "Cooling", "Connectivity", "Power"],
}


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def build_suppliers(n_extra: int) -> list[dict]:
    curated = [
        ("ShenZhen MicroTech", "China"), ("Taiwan Semiconductor Co", "Taiwan"),
        ("Seoul ChipWorks", "South Korea"), ("Mumbai Electronics Ltd", "India"),
        ("Stuttgart Precision GmbH", "Germany"), ("Osaka Display Corp", "Japan"),
        ("Bangkok Components", "Thailand"), ("Hanoi Battery Systems", "Vietnam"),
        ("Guadalajara Assemblies", "Mexico"), ("Penang Silicon Works", "Malaysia"),
        ("Helsinki Sensor Tech", "Finland"), ("Dongguan Power Systems", "China"),
    ]
    suppliers = []
    seen = set()
    for i, (name, country) in enumerate(curated, start=1):
        suppliers.append(_make_supplier(i, name, country))
        seen.add(name)

    countries = list(COUNTRY_REGION)
    idx = len(curated)
    while len(suppliers) < len(curated) + n_extra:
        country = random.choice(countries)
        city = random.choice(CITY_BY_COUNTRY[country])
        name = f"{city} {random.choice(SUPPLIER_SUFFIX)}"
        if name in seen:
            continue
        seen.add(name)
        idx += 1
        suppliers.append(_make_supplier(idx, name, country))
    return suppliers


def _make_supplier(i: int, name: str, country: str) -> dict:
    on_time = random.randint(80, 99)
    tier = 1 if on_time >= 95 else (2 if on_time >= 88 else 3)
    return {
        "id": f"SUP-{i:03d}", "name": name, "country": country,
        "region": COUNTRY_REGION[country], "tier": tier,
        "on_time_delivery_pct": on_time,
        "lead_time_days": random.randint(7, 30),
        "lead_time_variance": random.randint(1, 8),
    }


def build_components(target: int) -> list[dict]:
    components = []
    seen = set()
    i = 0
    while len(components) < target:
        category = COMPONENT_CATEGORIES[i % len(COMPONENT_CATEGORIES)]
        template = random.choice(COMPONENT_NAMES[category])
        name = template.format(
            n=random.choice([8, 12, 16, 18, 24, 50, 64, 100, 200, 256, 512]),
            s=random.choice([6.1, 6.7, 10.9, 13.3, 15.6, 27.0]),
        )
        i += 1
        if name in seen:
            continue
        seen.add(name)
        components.append({
            "id": f"CMP-{len(components) + 1:03d}", "name": name, "category": category,
            "unit_cost": round(random.uniform(2.0, 90.0), 2),
            "criticality": "high" if category in CRITICAL_CATEGORIES
            else random.choice(["medium", "low"]),
            "alt_supplier_count": 0,  # backfilled after SUPPLIES is built
        })
    return components


def build_products(n_extra: int) -> list[dict]:
    curated = [
        ("Galaxy Ultra X", "Smartphone", 1199.99), ("iPhone 16 Pro", "Smartphone", 1099.00),
        ("Pixel 9", "Smartphone", 799.00), ("ProBook Laptop 15", "Laptop", 1349.00),
        ("AirSlim Ultrabook", "Laptop", 1599.00), ("Tab Pro 11", "Tablet", 649.00),
        ("StudyPad Basic", "Tablet", 329.00), ("BudsPro Max", "Earbuds", 249.00),
        ("SmartWatch Ultra", "Wearable", 449.00), ("HomeHub Display", "Smart Home", 199.00),
    ]
    products = [
        {"id": f"PRD-{i:03d}", "name": name, "category": cat, "price": price}
        for i, (name, cat, price) in enumerate(curated, start=1)
    ]
    extra_names = [
        ("Galaxy A55", "Smartphone"), ("iPhone 16", "Smartphone"), ("Pixel 9 Pro", "Smartphone"),
        ("Nova Edge", "Smartphone"), ("ProBook Laptop 17", "Laptop"), ("GamerBook X", "Laptop"),
        ("AirSlim Mini", "Laptop"), ("Tab Lite 10", "Tablet"), ("Tab Ultra 14", "Tablet"),
        ("BudsLite", "Earbuds"), ("SmartWatch SE", "Wearable"), ("FitBand 7", "Wearable"),
        ("HomeHub Mini", "Smart Home"), ("Vision Monitor 27", "Monitor"),
        ("Vision Monitor 32", "Monitor"), ("PlayConsole 5", "Console"),
    ]
    for j, (name, cat) in enumerate(extra_names[:n_extra], start=len(products) + 1):
        base = {"Smartphone": 699, "Laptop": 1199, "Tablet": 399, "Wearable": 199,
                "Earbuds": 129, "Smart Home": 149, "Monitor": 349, "Console": 499}[cat]
        products.append({"id": f"PRD-{j:03d}", "name": name, "category": cat,
                         "price": round(base + random.uniform(-50, 250), 2)})
    return products


def build_warehouses() -> list[dict]:
    base = [
        ("ShenZhen Hub", "Shenzhen", "China", 50000), ("Dubai Logistics Center", "Dubai", "UAE", 30000),
        ("Rotterdam Port Warehouse", "Rotterdam", "Netherlands", 40000),
        ("LA Distribution Center", "Los Angeles", "USA", 45000),
        ("Singapore Free Trade Zone", "Singapore", "Singapore", 25000),
        ("Mumbai Central Depot", "Mumbai", "India", 20000),
        ("Frankfurt Air Cargo Hub", "Frankfurt", "Germany", 35000),
        ("Sao Paulo Depot", "Sao Paulo", "Brazil", 18000),
        ("Tokyo Bay Warehouse", "Tokyo", "Japan", 28000),
        ("Memphis Freight Center", "Memphis", "USA", 42000),
    ]
    warehouses = []
    for i, (name, city, country, cap) in enumerate(base, start=1):
        # WH-007 is an intentional bottleneck: near capacity.
        util = 96 if i == 7 else random.randint(45, 88)
        warehouses.append({"id": f"WH-{i:03d}", "name": name, "city": city,
                           "country": country, "capacity": cap, "utilization_pct": util})
    return warehouses


def build_retailers() -> list[dict]:
    base = [
        ("TechMart Online", "Global", "Global", "E-commerce"),
        ("ElectroCity Dubai Mall", "Dubai", "UAE", "Physical Store"),
        ("Berlin Electronics Hub", "Berlin", "Germany", "Physical Store"),
        ("BestBuy US", "Multiple", "USA", "Chain Store"),
        ("Flipkart India", "Bengaluru", "India", "E-commerce"),
        ("JD.com", "Beijing", "China", "E-commerce"),
        ("Currys UK", "London", "UK", "Chain Store"),
        ("Croma India", "Mumbai", "India", "Chain Store"),
        ("Amazon Japan", "Tokyo", "Japan", "E-commerce"),
        ("MediaMarkt EU", "Amsterdam", "Netherlands", "Chain Store"),
        ("Magazine Luiza", "Sao Paulo", "Brazil", "Chain Store"),
        ("Newegg US", "Los Angeles", "USA", "E-commerce"),
    ]
    return [{"id": f"RET-{i:03d}", "name": name, "city": city, "country": country, "type": rtype}
            for i, (name, city, country, rtype) in enumerate(base, start=1)]


# --------------------------------------------------------------------------- #
# Relationships
# --------------------------------------------------------------------------- #
def build_supplies(suppliers: list[dict], components: list[dict]) -> list[dict]:
    # Give each supplier 1-3 specialty categories.
    specialties = {
        s["id"]: set(random.sample(COMPONENT_CATEGORIES, k=random.randint(1, 3)))
        for s in suppliers
    }
    by_category = defaultdict(list)
    for s in suppliers:
        for cat in specialties[s["id"]]:
            by_category[cat].append(s["id"])

    # A handful of critical components are deliberately single-sourced.
    high = [c for c in components if c["criticality"] == "high"]
    single_source = set(random.sample([c["id"] for c in high], k=min(6, len(high))))
    # Guarantee a hero single-source: a Chipset supplied ONLY by Taiwan Semiconductor.
    taiwan = next(s for s in suppliers if s["name"] == "Taiwan Semiconductor Co")
    hero = next(c for c in components if c["category"] == "Chipset")
    single_source.add(hero["id"])

    supplies = []
    for c in components:
        candidates = by_category.get(c["category"]) or [s["id"] for s in suppliers]
        if c["id"] == hero["id"]:
            chosen = [taiwan["id"]]
        elif c["id"] in single_source:
            chosen = [random.choice(candidates)]
        else:
            k = min(len(candidates), random.randint(2, 4))
            chosen = random.sample(candidates, k=k)
        sup_by_id = {s["id"]: s for s in suppliers}
        for sup_id in chosen:
            sup = sup_by_id[sup_id]
            supplies.append({
                "supplier_id": sup_id, "component_id": c["id"],
                "volume_per_month": random.randint(2000, 25000),
                # Per-supplier price varies around the component's base cost.
                "unit_price": round(c["unit_cost"] * random.uniform(0.9, 1.2), 2),
                "lead_time_days": max(3, sup["lead_time_days"] + random.randint(-3, 5)),
            })
    return supplies, hero


def build_used_in(products: list[dict], components: list[dict]) -> list[dict]:
    by_category = defaultdict(list)
    for c in components:
        by_category[c["category"]].append(c["id"])

    used_in = []
    for p in products:
        template = PRODUCT_TEMPLATES[p["category"]]
        for cat in template:
            pool = by_category.get(cat)
            if not pool:
                continue
            for cid in random.sample(pool, k=min(len(pool), random.randint(1, 2))):
                used_in.append({"component_id": cid, "product_id": p["id"],
                                "quantity": random.randint(1, 2)})
    return used_in


def wire_hero_into_flagships(used_in: list[dict], hero: dict, products: list[dict]) -> None:
    """Force the single-source hero chipset into several flagship products."""
    flagships = [p for p in products if p["category"] in ("Smartphone", "Tablet")][:5]
    existing = {(u["component_id"], u["product_id"]) for u in used_in}
    for p in flagships:
        if (hero["id"], p["id"]) not in existing:
            used_in.append({"component_id": hero["id"], "product_id": p["id"], "quantity": 1})


def build_stored_at(products: list[dict], warehouses: list[dict]) -> list[dict]:
    stored_at = []
    for p in products:
        for w in random.sample(warehouses, k=random.randint(2, 5)):
            stored_at.append({"product_id": p["id"], "warehouse_id": w["id"],
                              "stock_quantity": random.randint(200, 8000)})
    return stored_at


def build_ships_to(warehouses: list[dict], retailers: list[dict]) -> list[dict]:
    modes = [("truck", (0.7, 2.0), (1, 3)), ("sea", (2.5, 4.5), (5, 20)),
             ("air", (6.0, 9.0), (2, 4))]
    ships_to = []
    seen = set()
    for w in warehouses:
        for r in random.sample(retailers, k=random.randint(2, 4)):
            if (w["id"], r["id"]) in seen:
                continue
            seen.add((w["id"], r["id"]))
            mode, (clo, chi), (tlo, thi) = random.choice(modes)
            ships_to.append({"warehouse_id": w["id"], "retailer_id": r["id"], "mode": mode,
                             "cost_per_unit": round(random.uniform(clo, chi), 2),
                             "transit_days": random.randint(tlo, thi)})
    # Intentional bottleneck: RET-005 (Flipkart India) served by exactly one warehouse.
    ships_to = [s for s in ships_to if s["retailer_id"] != "RET-005"]
    ships_to.append({"warehouse_id": "WH-006", "retailer_id": "RET-005", "mode": "truck",
                     "cost_per_unit": 0.90, "transit_days": 2})
    return ships_to


# --------------------------------------------------------------------------- #
# Assemble + save
# --------------------------------------------------------------------------- #
def main() -> None:
    suppliers = build_suppliers(n_extra=36)      # ~48
    components = build_components(target=70)
    products = build_products(n_extra=14)        # ~24
    warehouses = build_warehouses()
    retailers = build_retailers()

    supplies, hero = build_supplies(suppliers, components)
    used_in = build_used_in(products, components)
    wire_hero_into_flagships(used_in, hero, products)
    stored_at = build_stored_at(products, warehouses)
    ships_to = build_ships_to(warehouses, retailers)

    # Backfill alt_supplier_count = number of alternative suppliers (0 = single source).
    supplier_count = Counter(s["component_id"] for s in supplies)
    for c in components:
        c["alt_supplier_count"] = max(0, supplier_count.get(c["id"], 0) - 1)

    data = {
        "suppliers": suppliers, "components": components, "products": products,
        "warehouses": warehouses, "retailers": retailers, "supplies": supplies,
        "used_in": used_in, "stored_at": stored_at, "ships_to": ships_to,
    }

    out_path = os.path.join(os.path.dirname(__file__), "supply_chain_data.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print("Data generated successfully!")
    for key in ("suppliers", "components", "products", "warehouses", "retailers",
                "supplies", "used_in", "stored_at", "ships_to"):
        print(f"  {key:<12} {len(data[key])}")

    single_source = [cid for cid, n in supplier_count.items() if n == 1]
    print(f"\n  Single-source components: {len(single_source)}")
    hero_supplier = next(s for s in supplies if s["component_id"] == hero["id"])
    supplier_name = next(s["name"] for s in suppliers if s["id"] == hero_supplier["supplier_id"])
    print(f"  Hero single-source: {hero['name']} <-- only from {supplier_name}")


if __name__ == "__main__":
    main()
