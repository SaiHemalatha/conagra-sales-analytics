from pathlib import Path
import hashlib
import random

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# Synthetic Data Generator for Conagra / Gardein Sales Analytics
# ------------------------------------------------------------
# Data Note:
# This script generates synthetic sample data that mirrors the
# structure of the original academic project dataset.
# The original dataset is not included due to access restrictions.
# These files are intended to demonstrate the analysis workflow only.
# ------------------------------------------------------------

random.seed(42)
np.random.seed(42)

# If this file is inside scripts/, save outputs to the project root folders
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)


# Core dimensions
brands = {
    "MORNINGSTAR FARMS": 0.467,
    "GARDEIN": 0.214,
    "IMPOSSIBLE": 0.156,
    "BEYOND MEAT BEYOND BURGER": 0.093,
    "BEYOND MEAT": 0.069,
}

flavors_by_brand = {
    "MORNINGSTAR FARMS": [
        "REGULAR",
        "ORIGINAL",
        "BACON",
        "SPICY BLACK BEAN",
        "BUFFALO",
        "CLASSIC",
    ],
    "GARDEIN": [
        "REGULAR",
        "ORIGINAL",
        "CLASSIC",
        "HERB",
    ],
    "IMPOSSIBLE": [
        "REGULAR",
        "ORIGINAL",
        "SPICY BLACK BEAN",
        "BUFFALO",
    ],
    "BEYOND MEAT BEYOND BURGER": [
        "REGULAR",
        "ORIGINAL",
    ],
    "BEYOND MEAT": [
        "REGULAR",
        "ORIGINAL",
        "BACON",
    ],
}

product_desc_by_brand = {
    "MORNINGSTAR FARMS": [
        "MORNINGSTAR FARMS VEGGIE BURGER 9OZ",
        "MORNINGSTAR FARMS SPICY BLACK BEAN BURGER 9OZ",
        "MORNINGSTAR FARMS BACON STRIPS 5.25OZ",
        "MORNINGSTAR FARMS BUFFALO WINGS 8OZ",
        "MORNINGSTAR FARMS ORIGINAL BURGER 8OZ",
    ],
    "GARDEIN": [
        "GARDEIN ULTIMATE BEEFLESS BURGER 14OZ",
        "GARDEIN SEVEN GRAIN CRISPY TENDERS 10.5OZ",
        "GARDEIN MANDARIN ORANGE CRISPY CHKN 10.5OZ",
        "GARDEIN MEATLESS MEATBALLS 12.7OZ",
    ],
    "IMPOSSIBLE": [
        "IMPOSSIBLE BURGER PLANT-BASED MEAT 12OZ",
        "IMPOSSIBLE SPICY BURGER 12OZ",
        "IMPOSSIBLE CHICKEN NUGGETS 13.1OZ",
    ],
    "BEYOND MEAT BEYOND BURGER": [
        "BEYOND BURGER PLANT-BASED PATTIES 8OZ",
        "BEYOND BURGER ORIGINAL 8OZ",
    ],
    "BEYOND MEAT": [
        "BEYOND SAUSAGE PLANT-BASED LINKS 14OZ",
        "BEYOND BREAKFAST SAUSAGE 7OZ",
        "BEYOND BACON PLANT-BASED STRIPS 3OZ",
    ],
}

seasons = ["Spring", "Summer", "Fall", "Winter"]

season_to_months = {
    "Spring": [3, 4, 5],
    "Summer": [6, 7, 8],
    "Fall": [9, 10, 11],
    "Winter": [12, 1, 2],
}

promo_types = [
    "Any Merch",
    "Display Only",
    "Feature And Display",
    "Feature Only",
    "Price Reductions Only",
    "Special Pack Only",
    "No Merch",
]

markets = [
    "TOTAL US",
    "SOUTHEAST",
    "MIDWEST",
    "NORTHEAST",
    "WEST",
    "CALIFORNIA",
    "NEW YORK",
    "TEXAS",
    "FLORIDA",
]

season_multiplier = {
    "Spring": 1.45,
    "Summer": 1.30,
    "Fall": 1.10,
    "Winter": 1.00,
}

promo_multiplier = {
    "Any Merch": 1.60,
    "Feature Only": 1.20,
    "Price Reductions Only": 1.10,
    "Feature And Display": 1.05,
    "Display Only": 1.00,
    "Special Pack Only": 0.95,
    "No Merch": 0.70,
}

# Synthetic assumption: Gardein underperforms in merchandised promotions
gardein_promo_penalty = 0.52

price_map = {
    "MORNINGSTAR FARMS": (5.49, 7.99),
    "GARDEIN": (4.99, 8.49),
    "IMPOSSIBLE": (7.99, 10.99),
    "BEYOND MEAT BEYOND BURGER": (7.49, 9.99),
    "BEYOND MEAT": (6.99, 9.49),
}


def stable_upc(product_name: str) -> int:
    """
    Creates a stable synthetic UPC-like number from product name.
    This avoids Python's built-in hash randomization.
    """
    digest = hashlib.md5(product_name.encode("utf-8")).hexdigest()
    return 1000000000000 + int(digest[:8], 16) % 999999


rows = []

for _ in range(1500):
    brand_name = random.choices(
        list(brands.keys()),
        weights=list(brands.values()),
        k=1,
    )[0]

    flavor = random.choice(flavors_by_brand[brand_name])
    product = random.choice(product_desc_by_brand[brand_name])
    season = random.choice(seasons)
    month = random.choice(season_to_months[season])
    year = random.choice([2022, 2023])
    market = random.choice(markets)
    promo = random.choice(promo_types)

    week_end = (
        pd.Timestamp(year=year, month=month, day=random.randint(1, 28))
        + pd.offsets.Week(weekday=5)
    )

    base_units = random.randint(400, 2000)
    sales_multiplier = season_multiplier[season] * promo_multiplier[promo]

    if brand_name == "GARDEIN" and promo != "No Merch":
        sales_multiplier *= gardein_promo_penalty

    unit_sales = int(base_units * sales_multiplier * random.uniform(0.85, 1.15))

    low_price, high_price = price_map[brand_name]
    price_per_unit = round(random.uniform(low_price, high_price), 2)

    if promo in ["Price Reductions Only", "Any Merch", "Special Pack Only"]:
        price_per_unit = round(price_per_unit * random.uniform(0.80, 0.92), 2)

    dollar_sales = round(unit_sales * price_per_unit, 2)

    rows.append(
        {
            "week_end_date": week_end.strftime("%Y-%m-%d"),
            "market": market,
            "brand": brand_name,
            "product_description": product,
            "upc": stable_upc(product),
            "flavor": flavor,
            "category": "FROZEN PLANT-BASED MEAT",
            "season": season,
            "merchandise_condition": promo,
            "unit_sales": unit_sales,
            "dollar_sales": dollar_sales,
            "price_per_unit": price_per_unit,
        }
    )


# Main sample dataset
df = pd.DataFrame(rows)
df = df.sort_values(["week_end_date", "brand"]).reset_index(drop=True)

sample_sales_path = DATA_DIR / "sample_sales_data.csv"
df.to_csv(sample_sales_path, index=False)


# Market share summary
market_share_df = (
    df.groupby("brand", as_index=False)
    .agg(
        total_dollar_sales=("dollar_sales", "sum"),
        total_unit_sales=("unit_sales", "sum"),
    )
)

total_dollar_sales = market_share_df["total_dollar_sales"].sum()
market_share_df["market_share_pct"] = (
    market_share_df["total_dollar_sales"] / total_dollar_sales * 100
).round(1)

market_share_df = market_share_df.sort_values(
    "market_share_pct",
    ascending=False,
).reset_index(drop=True)

market_share_path = OUTPUTS_DIR / "market_share.csv"
market_share_df.to_csv(market_share_path, index=False)


# Flavor summary
flavor_analysis_df = (
    df.groupby(["flavor", "brand"], as_index=False)
    .agg(
        total_unit_sales=("unit_sales", "sum"),
        total_dollar_sales=("dollar_sales", "sum"),
    )
    .sort_values("total_unit_sales", ascending=False)
)

flavor_analysis_path = OUTPUTS_DIR / "flavor_analysis.csv"
flavor_analysis_df.to_csv(flavor_analysis_path, index=False)


print("Synthetic data generation completed successfully.")
print(f"Sales data saved to: {sample_sales_path}")
print(f"Market share output saved to: {market_share_path}")
print(f"Flavor analysis output saved to: {flavor_analysis_path}")
print()
print(f"Sales data shape: {df.shape}")
print()
print("Market share summary:")
print(market_share_df.to_string(index=False))
