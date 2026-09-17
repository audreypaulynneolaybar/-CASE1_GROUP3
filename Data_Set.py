import random
import importlib
pd = importlib.import_module("pandas")
np = importlib.import_module("numpy")
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

DAYS = 90
START_DATE = datetime(2026, 1, 1)

MARKETS_CONFIG = {
    "MKT_01": {"stalls": 30, "commodities_count": 10, "scales_per_stall_range": (1, 2)},
    "MKT_02": {"stalls": 30, "commodities_count": 20, "scales_per_stall_range": (3, 5)},
    "MKT_03": {"stalls": 33, "commodities_count": 8,  "scales_per_stall_range": (1, 2)},
    "MKT_04": {"stalls": 40, "commodities_count": 15, "scales_per_stall_range": (1, 3)},
    "MKT_05": {"stalls": 10, "commodities_count": 10, "scales_per_stall_range": (1, 2)},
}

ALL_COMMODITIES = {
    "Carrots": (20.0, 23.0),
    "Pork": (300.0, 330.0),
    "Rice (Sinandomeng)": (48.0, 60.0),
    "Chicken (Whole)": (160.0, 200.0),
    "Beef (Rump)": (390.0, 460.0),
    "Tilapia": (120.0, 160.0),
    "Bangus": (150.0, 210.0),
    "Tomatoes": (60.0, 110.0),
    "Red Onions": (90.0, 160.0),
    "Garlic": (80.0, 130.0),
    "Cabbage": (40.0, 70.0),
    "Potatoes": (70.0, 110.0),
    "Whole Fish (Galunggong)": (180.0, 240.0),
}

commodity_names = list(ALL_COMMODITIES.keys())

# Map exact commodity subsets to markets
market_commodities = {
    mkt: commodity_names[: cfg["commodities_count"]]
    for mkt, cfg in MARKETS_CONFIG.items()
}

# Generate stall & scale mapping based on market specifications
stall_info = []
scale_counter = 1

for mkt, cfg in MARKETS_CONFIG.items():
    num_stalls = cfg["stalls"]
    min_sc, max_sc = cfg["scales_per_stall_range"]
    for s in range(1, num_stalls + 1):
        stall_id = f"{mkt}_STL_{s:03d}"
        num_scales = random.randint(min_sc, max_sc)
        scale_ids = [f"SCL_{scale_counter + i:04d}" for i in range(num_scales)]
        scale_counter += num_scales
        stall_info.append({"market_id": mkt, "stall_id": stall_id, "scale_ids": scale_ids})

df_stalls = pd.DataFrame(stall_info)

# 1. Generate prices.csv
prices_data = []
for day_idx in range(DAYS):
    current_date = (START_DATE + timedelta(days=day_idx)).strftime("%Y-%m-%d")
    for mkt, comms in market_commodities.items():
        mkt_num = int(mkt.split("_")[1])
        mkt_bias = (mkt_num - 3) * 0.02
        for comm in comms:
            base_min, base_max = ALL_COMMODITIES[comm]
            day_noise = np.random.normal(0, 0.015)

            low = round(base_min * (1 + mkt_bias + day_noise), 2)
            high = round(base_max * (1 + mkt_bias + day_noise), 2)
            avg = round(np.random.uniform(low + 0.5, high - 0.5), 2)

            prices_data.append({
                "date": current_date,
                "market_id": mkt,
                "commodity": comm,
                "min_price_per_kg": low,
                "max_price_per_kg": high,
                "avg_price_per_kg": avg
            })

df_prices = pd.DataFrame(prices_data)
df_prices.to_csv("prices.csv", index=False)

# 2. Generate inspections.csv
INSPECTORS = [f"INS_{i:02d}" for i in range(1, 6)]
inspections_data = []
NOMINAL_WEIGHT_G = 1000

for row in df_stalls.itertuples():
    mkt = row.market_id
    stall_id = row.stall_id
    scales = row.scale_ids

    for scale_id in scales:
        inspection_days = sorted(random.sample(range(DAYS), 3))
        is_faulty_scale = random.random() < 0.20

        for day_idx in inspection_days:
            insp_date = START_DATE + timedelta(days=day_idx)
            date_str = insp_date.strftime("%Y-%m-%d")
            inspector = random.choice(INSPECTORS)

            if not is_faulty_scale:
                #-2g to +1g (998g - 1001g)
                reading = random.choice([998, 999, 1000, 1001])
                is_cert = "Y"
                if random.random() < 0.20:
                    last_cert = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 1800))
                else:
                    last_cert = insp_date - timedelta(days=random.randint(30, 300))
            else:
                reading = random.randint(1005, 1050)
                is_cert = "N"
                if random.random() < 0.60:
                    last_cert = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 1800))
                else:
                    last_cert = insp_date - timedelta(days=random.randint(30, 365))

            if random.random() < 0.10:
                is_cert = "N" if is_cert == "Y" else "Y"

            inspections_data.append({
                "date": date_str,
                "market_id": mkt,
                "stall_id": stall_id,
                "scale_id": scale_id,
                "nominal_weight_g (test mass)": NOMINAL_WEIGHT_G,
                "reading_g (scale reading)": reading,
                "is_certified (Y/N)": is_cert,
                "last_cert_date": last_cert.strftime("%Y-%m-%d"),
                "inspector_id": inspector
            })

df_inspections = pd.DataFrame(inspections_data)
df_inspections.to_csv("inspections.csv", index=False)

# 3. Generate sales_samples.csv
sales_data = []
price_lookup = df_prices.set_index(["date", "market_id", "commodity"])["avg_price_per_kg"].to_dict()

for day_idx in range(DAYS):
    current_date = (START_DATE + timedelta(days=day_idx)).strftime("%Y-%m-%d")
    daily_shops = random.randint(20, 35)

    for _ in range(daily_shops):
        stall_row = df_stalls.sample(1).iloc[0]
        mkt = stall_row["market_id"]
        stall = stall_row["stall_id"]

        comm = random.choice(market_commodities[mkt])
        posted_price = price_lookup.get((current_date, mkt, comm), ALL_COMMODITIES[comm][0])

        actual_weight = round(random.uniform(0.5, 3.5), 3)
        stall_insp = df_inspections[df_inspections["stall_id"] == stall]
        is_bad_stall = (stall_insp["is_certified (Y/N)"] == "N").any()

        if is_bad_stall:
            label_weight = round(actual_weight * random.uniform(1.04, 1.10), 3)
        else:
            label_weight = round(actual_weight * random.uniform(0.998, 1.001), 3)

        paid_amount = round(label_weight * posted_price, 2)

        sales_data.append({
            "date": current_date,
            "market_id": mkt,
            "stall_id": stall,
            "commodity": comm,
            "paid_amount_php": paid_amount,
            "label_weight_kg": label_weight,
            "actual_weight_kg": actual_weight
        })

df_sales = pd.DataFrame(sales_data)
df_sales.to_csv("sales_samples.csv", index=False)

print("Data generation according to screenshot parameters complete.")