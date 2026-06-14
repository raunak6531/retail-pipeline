import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

CATEGORIES = ["Electronics", "Clothing", "Grocery", "Home & Kitchen", "Sports"]
REGIONS = ["North", "South", "East", "West", "Central"]
PAYMENT_METHODS = ["Credit Card", "UPI", "Cash", "Debit Card", "Net Banking"]

PRODUCTS = {
    "Electronics":    [("Wireless Earbuds", 1299), ("Smart Watch", 2999), ("Bluetooth Speaker", 899),
                       ("USB Hub", 499), ("Laptop Stand", 799)],
    "Clothing":       [("Casual T-Shirt", 399), ("Denim Jeans", 999), ("Formal Shirt", 699),
                       ("Winter Jacket", 1799), ("Sports Shoes", 1499)],
    "Grocery":        [("Organic Rice 5kg", 349), ("Olive Oil 1L", 499), ("Almonds 500g", 599),
                       ("Green Tea Box", 199), ("Protein Bar Pack", 449)],
    "Home & Kitchen": [("Non-stick Pan", 799), ("Water Purifier", 3499), ("Coffee Maker", 1999),
                       ("Air Fryer", 2799), ("Dinner Set", 1299)],
    "Sports":         [("Yoga Mat", 599), ("Resistance Bands", 349), ("Dumbbells Set", 1499),
                       ("Cycling Gloves", 299), ("Fitness Tracker", 1999)],
}

def generate_sales_data(num_records=50000):
    records = []
    start_date = datetime(2023, 1, 1)

    for i in range(num_records):
        category = random.choice(CATEGORIES)
        product_name, base_price = random.choice(PRODUCTS[category])

        # Add some price variation (+/- 10%)
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        quantity = random.randint(1, 5)
        discount = round(random.uniform(0, 0.25), 2)
        final_price = round(price * quantity * (1 - discount), 2)

        # Weighted date generation — more sales on weekends and year-end
        days_offset = random.randint(0, 364)
        sale_date = start_date + timedelta(days=days_offset)

        region = random.choice(REGIONS)
        payment = random.choice(PAYMENT_METHODS)

        # Simulate some returns (5% of records)
        is_returned = random.random() < 0.05

        records.append({
            "transaction_id": f"TXN{100000 + i}",
            "date": sale_date.strftime("%Y-%m-%d"),
            "product_name": product_name,
            "category": category,
            "region": region,
            "quantity": quantity,
            "unit_price": price,
            "discount_pct": discount,
            "final_amount": final_price,
            "payment_method": payment,
            "is_returned": is_returned
        })

    df = pd.DataFrame(records)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_sales.csv", index=False)
    print(f"Generated {num_records} records -> data/raw_sales.csv")
    return df

if __name__ == "__main__":
    generate_sales_data()
