"""
Athena Core — Load Real Superstore Dataset
Downloads a real e-commerce dataset (Superstore Sales) and seeds the SQLite database.
"""
import pandas as pd
import sqlite3
import os
import numpy as np
from datetime import datetime
from core.database import get_connection

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "antigravity.db")

def reset_database():
    """Drop all tables and recreate them to ensure a clean state."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Drop tables
    tables = ["strategic_inputs", "market_data", "order_items", "orders", "products", "customers", "categories"]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()
    
    # Recreate tables using init_tables
    from core.database import init_tables
    init_tables()


def load_superstore_data():
    print("Telechargement du dataset Superstore...")
    url = "https://raw.githubusercontent.com/zpio/datasets/main/sample_superstore.csv"
    df = pd.read_csv(url, encoding="windows-1252")
    
    # Nettoyage des noms de colonnes
    df.columns = [c.lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    
    print("Traitement et nettoyage des donnees...")
    df["order_date"] = pd.to_datetime(df["order_date"])
    process_and_inject_df(df)

def process_and_inject_df(df):
    """Parses and injects a raw dataframe into the SQLite schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Catégories (Sub-Categories)
    print("Insertion des categories...")
    categories = df[["sub_category", "category"]].drop_duplicates().reset_index(drop=True)
    cat_map = {}
    for idx, row in categories.iterrows():
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                       (row["sub_category"], row["category"]))
        cat_map[row["sub_category"]] = cursor.lastrowid
    
    # 2. Produits
    print("Insertion des produits...")
    # Calculer le prix et le coût unitaire moyen pour chaque produit
    # Cost = Sales - Profit
    df["total_cost"] = df["sales"] - df["profit"]
    # Handle division by zero
    df_safe = df[df["quantity"] > 0].copy()
    df_safe["unit_price_calc"] = df_safe["sales"] / (df_safe["quantity"] * (1 - df_safe["discount"].clip(upper=0.99)))
    df_safe["unit_cost_calc"] = df_safe["total_cost"] / df_safe["quantity"]
    
    prod_agg = df_safe.groupby(["product_id", "product_name", "sub_category"]).agg(
        avg_price=("unit_price_calc", "mean"),
        avg_cost=("unit_cost_calc", "mean")
    ).reset_index()
    
    prod_map = {} # product_id (string) -> db_id (int)
    for idx, row in prod_agg.iterrows():
        cat_id = cat_map[row["sub_category"]]
        cursor.execute("INSERT INTO products (name, category_id, price, cost, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                       (row["product_name"][:100], cat_id, round(row["avg_price"], 2), round(row["avg_cost"], 2), 500))
        prod_map[row["product_id"]] = cursor.lastrowid
        
    # 3. Clients
    print("Insertion des clients...")
    customers = df[["customer_id", "customer_name", "segment", "city", "country"]].drop_duplicates().reset_index(drop=True)
    cust_map = {}
    for idx, row in customers.iterrows():
        cursor.execute("INSERT INTO customers (name, segment, city, country) VALUES (?, ?, ?, ?)",
                       (row["customer_name"], row["segment"], row["city"], row["country"]))
        cust_map[row["customer_id"]] = cursor.lastrowid
        
    # 4. Commandes
    print("Insertion des commandes...")
    orders = df.groupby("order_id").agg(
        customer_id=("customer_id", "first"),
        order_date=("order_date", "first"),
        total_amount=("sales", "sum"),
        ship_mode=("ship_mode", "first")
    ).reset_index()
    
    order_map = {}
    for idx, row in orders.iterrows():
        c_id = cust_map[row["customer_id"]]
        channel = "web" if row["ship_mode"] == "Standard Class" else "premium"
        cursor.execute("INSERT INTO orders (customer_id, order_date, total_amount, status, channel) VALUES (?, ?, ?, ?, ?)",
                       (c_id, row["order_date"].strftime("%Y-%m-%d"), round(row["total_amount"], 2), "completed", channel))
        order_map[row["order_id"]] = cursor.lastrowid
        
    # 5. Order Items
    print("Insertion des lignes de commande...")
    items_data = []
    for idx, row in df.iterrows():
        if row["product_id"] not in prod_map:
            continue # Skip if product aggregate failed
        o_id = order_map[row["order_id"]]
        p_id = prod_map[row["product_id"]]
        
        # Calculate derived unit price for this specific line item
        qty = max(1, row["quantity"])
        disc = min(0.99, max(0, row["discount"]))
        unit_price = row["sales"] / (qty * (1 - disc))
        
        items_data.append((o_id, p_id, qty, round(unit_price, 2), disc))
        
    cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES (?, ?, ?, ?, ?)", items_data)
    
    # 6. Market Data (Synthetic but based on real category performance)
    print("Generation des donnees marche strategiques...")
    cat_sales = df.groupby("sub_category")["sales"].sum()
    max_sales = cat_sales.max()
    
    for prod_id_str, db_prod_id in prod_map.items():
        subcat = prod_agg[prod_agg["product_id"] == prod_id_str]["sub_category"].iloc[0]
        # Relative market share inside its category (simulated)
        prod_sales = df[df["product_id"] == prod_id_str]["sales"].sum()
        rel_share = min(5.0, max(0.1, (prod_sales / cat_sales[subcat]) * 10))
        
        # Category growth (simulated: larger categories grow slightly more)
        growth = (cat_sales[subcat] / max_sales) * 0.25 - 0.05
        
        attractiveness = min(10, max(1, 5 + growth * 20))
        position = min(10, max(1, rel_share * 3))
        
        cursor.execute(
            "INSERT INTO market_data (product_id, market_growth_rate, relative_market_share, competitor_share, market_attractiveness, competitive_position, period) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (db_prod_id, round(growth, 4), round(rel_share, 4), 0.3, round(attractiveness, 2), round(position, 2), "2018-01-01")
        )

    # 7. Strategic Inputs (SWOT / PESTEL / Porter)
    print("Insertion des modeles strategiques (SWOT/PESTEL/Porter)...")
    from data.seed_data import generate_all
    # We can just steal the strategic inputs from seed_data logic, let's hardcode a few
    swot_data = [
        ("SWOT", "Force", "Excellente rétention des clients 'Consumer'", 8, 0),
        ("SWOT", "Faiblesse", "Pertes sur la catégorie 'Furniture/Tables'", 7, 0),
        ("SWOT", "Opportunité", "Expansion dans l'Est des États-Unis", 8, 0),
        ("SWOT", "Menace", "Augmentation des coûts de transport ('Same Day')", 6, 0),
    ]
    for type_, cat, desc, score, impact in swot_data:
        cursor.execute("INSERT INTO strategic_inputs (type, category, description, score, impact) VALUES (?, ?, ?, ?, ?)",
                       (type_, cat, desc, score, impact))

    conn.commit()
    conn.close()
    print("Database Superstore chargée avec succès !")

if __name__ == "__main__":
    reset_database()
    load_superstore_data()
