import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_data(rows=10005):
    start_date = datetime(2023, 1, 1)
    data = {
        'order id': [f'ORD-{i}' for i in range(rows)],
        'date': [(start_date + timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d') for i in range(rows)],
        'sales': np.random.uniform(10, 500, rows).round(2),
        'quantity': np.random.randint(1, 10, rows),
        'product id': [f'PROD-{np.random.randint(1, 100)}' for i in range(rows)],
        'product name': [f'Product {np.random.randint(1, 100)}' for i in range(rows)],
        'customer': [f'Customer {np.random.randint(1, 500)}' for i in range(rows)],
        'category': [np.random.choice(['Electronics', 'Office', 'Furniture']) for i in range(rows)],
        'profit': np.random.uniform(2, 100, rows).round(2)
    }
    df = pd.DataFrame(data)
    df.to_csv('large_dataset.csv', index=False)
    print(f"Generated large_dataset.csv with {len(df)} rows.")

if __name__ == "__main__":
    generate_dummy_data()
