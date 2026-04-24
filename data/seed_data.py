"""
Athena Core — Synthetic Data Generator
Generates 2 years of realistic business data for the MVP demo.
"""
import random
import sqlite3
import os
import numpy as np
from datetime import datetime, timedelta
from core.config import DB_PATH, SEED_CUSTOMERS, SEED_PRODUCTS, SEED_ORDERS, SEED_DAYS
from core.database import init_tables, get_connection

random.seed(42)
np.random.seed(42)

# ─── Reference Data ──────────────────────────────────────────────
CATEGORIES = [
    ("Électronique", "Appareils et accessoires électroniques"),
    ("Mode & Textile", "Vêtements, chaussures et accessoires"),
    ("Maison & Déco", "Mobilier, décoration et aménagement"),
    ("Sport & Loisirs", "Équipements sportifs et activités"),
    ("Beauté & Santé", "Cosmétiques, soins et bien-être"),
]

PRODUCT_NAMES = {
    "Électronique": [
        "Écouteurs Bluetooth Pro", "Chargeur Sans Fil", "Webcam HD 4K",
        "Clavier Mécanique RGB", "Souris Ergonomique", "Hub USB-C",
        "Enceinte Portable", "Montre Connectée", "Batterie Externe 20000mAh",
        "Support Laptop Alu",
    ],
    "Mode & Textile": [
        "T-Shirt Premium Coton", "Sneakers Urban", "Sac à Dos City",
        "Casquette Brodée", "Veste Imperméable", "Jean Slim Stretch",
        "Écharpe Cachemire", "Ceinture Cuir", "Lunettes de Soleil Polarisées",
        "Portefeuille RFID",
    ],
    "Maison & Déco": [
        "Lampe LED Design", "Coussin Velours", "Cadre Photo Bambou",
        "Bougie Parfumée Soja", "Miroir Rond Doré", "Vase Céramique",
        "Tapis Berbère", "Horloge Murale Minimaliste", "Set de Table Lin",
        "Plante Artificielle XL",
    ],
    "Sport & Loisirs": [
        "Tapis de Yoga Premium", "Haltères Ajustables", "Bande Élastique Set",
        "Gourde Isotherme 750ml", "Sac de Sport Étanche", "Corde à Sauter Pro",
        "Montre Cardio GPS", "Rouleau Massage Mousse", "Genouillères Sport",
        "Lampe Frontale Trail",
    ],
    "Beauté & Santé": [
        "Sérum Vitamine C Bio", "Brosse Nettoyante Visage", "Huile Essentielle Set",
        "Crème Hydratante SPF50", "Palette Maquillage Pro", "Diffuseur Aromathérapie",
        "Masque Cheveux Kératine", "Lime à Ongles Cristal", "Baume à Lèvres Naturel",
        "Trousse de Toilette Voyage",
    ],
}

CITIES = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Nice",
    "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
    "Rennes", "Reims", "Le Havre", "Grenoble", "Dijon",
]

FIRST_NAMES = [
    "Emma", "Gabriel", "Louise", "Raphaël", "Jade", "Léo", "Alice", "Louis",
    "Chloé", "Adam", "Lina", "Jules", "Mia", "Hugo", "Léa", "Lucas",
    "Inès", "Arthur", "Manon", "Ethan", "Sarah", "Nathan", "Camille", "Tom",
    "Anna", "Théo", "Eva", "Noah", "Zoé", "Mathis",
]

LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier",
]

CHANNELS = ["web", "mobile", "marketplace", "boutique"]


def generate_all():
    """Generate all synthetic data and insert into database."""
    init_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False  # Data already seeded

    print("Seeding database with synthetic data...")

    # ── 1. Categories ────────────────────────────────────────────
    for name, desc in CATEGORIES:
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, desc))
    conn.commit()

    # ── 2. Products ──────────────────────────────────────────────
    product_id = 0
    product_prices = {}
    product_costs = {}
    for cat_idx, (cat_name, _) in enumerate(CATEGORIES, 1):
        for prod_name in PRODUCT_NAMES[cat_name]:
            product_id += 1
            base_price = round(random.uniform(9.99, 199.99), 2)
            cost = round(base_price * random.uniform(0.3, 0.65), 2)
            stock = random.randint(20, 500)
            cursor.execute(
                "INSERT INTO products (name, category_id, price, cost, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                (prod_name, cat_idx, base_price, cost, stock),
            )
            product_prices[product_id] = base_price
            product_costs[product_id] = cost
    conn.commit()
    num_products = product_id

    # ── 3. Customers ─────────────────────────────────────────────
    segments = ["Premium", "Premium", "Standard", "Standard", "Standard",
                "Standard", "Occasionnel", "Occasionnel", "Occasionnel", "Nouveau"]
    for i in range(SEED_CUSTOMERS):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{i}@email.com"
        segment = random.choice(segments)
        city = random.choice(CITIES)
        days_ago = random.randint(30, SEED_DAYS)
        created = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO customers (name, email, segment, city, country, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, segment, city, "France", created),
        )
    conn.commit()

    # ── 4. Orders & Order Items ──────────────────────────────────
    start_date = datetime.now() - timedelta(days=SEED_DAYS)
    order_id = 0

    # Create seasonality pattern: higher sales in Nov-Dec, lower in Jan-Feb
    for _ in range(SEED_ORDERS):
        order_id += 1
        customer_id = random.randint(1, SEED_CUSTOMERS)

        # Add seasonality to order dates
        day_offset = random.randint(0, SEED_DAYS - 1)
        order_date = start_date + timedelta(days=day_offset)
        month = order_date.month

        # Seasonal weight — more orders in Q4
        seasonal_weight = {
            1: 0.7, 2: 0.65, 3: 0.8, 4: 0.85, 5: 0.9, 6: 1.0,
            7: 0.85, 8: 0.75, 9: 1.0, 10: 1.1, 11: 1.4, 12: 1.6,
        }
        if random.random() > seasonal_weight.get(month, 1.0):
            continue

        channel = random.choices(CHANNELS, weights=[40, 30, 20, 10])[0]
        num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        total = 0.0

        items_data = []
        for _ in range(num_items):
            prod_id = random.randint(1, num_products)
            qty = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
            price = product_prices[prod_id]
            discount = random.choices([0, 0.05, 0.1, 0.15, 0.2], weights=[60, 15, 12, 8, 5])[0]
            line_total = qty * price * (1 - discount)
            total += line_total
            items_data.append((prod_id, qty, price, discount))

        # Add a growth trend — slightly increase total over time
        growth_factor = 1 + (day_offset / SEED_DAYS) * 0.15
        total *= growth_factor

        cursor.execute(
            "INSERT INTO orders (customer_id, order_date, total_amount, status, channel) VALUES (?, ?, ?, ?, ?)",
            (customer_id, order_date.strftime("%Y-%m-%d"), round(total, 2), "completed", channel),
        )
        real_order_id = cursor.lastrowid

        for prod_id, qty, price, discount in items_data:
            adjusted_price = round(price * growth_factor, 2)
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES (?, ?, ?, ?, ?)",
                (real_order_id, prod_id, qty, adjusted_price, discount),
            )

    conn.commit()

    # ── 5. Market Data ───────────────────────────────────────────
    for pid in range(1, num_products + 1):
        growth = round(random.uniform(-0.1, 0.35), 4)
        rel_share = round(random.uniform(0.1, 3.0), 4)
        competitor = round(random.uniform(0.1, 0.6), 4)
        attractiveness = round(random.uniform(2, 9), 2)
        position = round(random.uniform(2, 9), 2)
        cursor.execute(
            "INSERT INTO market_data (product_id, market_growth_rate, relative_market_share, "
            "competitor_share, market_attractiveness, competitive_position, period) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (pid, growth, rel_share, competitor, attractiveness, position,
             datetime.now().strftime("%Y-%m-%d")),
        )
    conn.commit()

    # ── 6. Strategic Inputs (SWOT / PESTEL / Porter) ─────────────
    swot_data = [
        ("SWOT", "Force", "Large base de clients fidèles (segment Premium)", 8, 0),
        ("SWOT", "Force", "Marges élevées sur les produits électroniques", 7, 0),
        ("SWOT", "Force", "Présence multicanale (web, mobile, marketplace)", 9, 0),
        ("SWOT", "Faiblesse", "Dépendance aux promotions pour les ventes", 6, 0),
        ("SWOT", "Faiblesse", "Logistique coûteuse sur les petites commandes", 5, 0),
        ("SWOT", "Faiblesse", "Manque de notoriété de marque vs leaders", 7, 0),
        ("SWOT", "Opportunité", "Croissance du e-commerce en France (+15%/an)", 9, 0),
        ("SWOT", "Opportunité", "Expansion vers le marché B2B", 7, 0),
        ("SWOT", "Opportunité", "Tendance éco-responsable (produits verts)", 6, 0),
        ("SWOT", "Menace", "Concurrence accrue d'Amazon et Temu", 9, 0),
        ("SWOT", "Menace", "Inflation et baisse du pouvoir d'achat", 8, 0),
        ("SWOT", "Menace", "Réglementation RGPD plus stricte", 5, 0),
    ]
    pestel_data = [
        ("PESTEL", "Politique", "Politique de soutien au commerce digital", 3, 70),
        ("PESTEL", "Politique", "Taxes sur le e-commerce transfrontalier", -2, 50),
        ("PESTEL", "Économique", "Croissance du PIB modérée (+1.2%)", 2, 80),
        ("PESTEL", "Économique", "Inflation persistante (3-4%)", -3, 75),
        ("PESTEL", "Socioculturel", "Adoption croissante du shopping mobile", 4, 90),
        ("PESTEL", "Socioculturel", "Préférence pour les marques éthiques", 3, 65),
        ("PESTEL", "Technologique", "IA et personnalisation en temps réel", 5, 85),
        ("PESTEL", "Technologique", "Edge computing pour la logistique", 3, 60),
        ("PESTEL", "Environnemental", "Normes carbone pour la livraison", -2, 70),
        ("PESTEL", "Environnemental", "Demande d'emballages recyclables", 2, 80),
        ("PESTEL", "Légal", "RGPD et protection des données renforcée", -3, 90),
        ("PESTEL", "Légal", "Droit de rétractation étendu", -1, 60),
    ]
    porter_data = [
        ("PORTER", "Pouvoir Fournisseurs", "Fournisseurs diversifiés, faible dépendance", 2, 0),
        ("PORTER", "Pouvoir Clients", "Clients sensibles au prix, faible coût de switch", 4, 0),
        ("PORTER", "Menace Nouveaux Entrants", "Barrières faibles, marché accessible", 4, 0),
        ("PORTER", "Menace Substituts", "Alternatives nombreuses (magasins physiques, marketplaces)", 3, 0),
        ("PORTER", "Rivalité Concurrentielle", "Marché très concurrentiel, guerre des prix", 5, 0),
    ]
    for data_list in [swot_data, pestel_data, porter_data]:
        for type_, cat, desc, score, impact in data_list:
            cursor.execute(
                "INSERT INTO strategic_inputs (type, category, description, score, impact) VALUES (?, ?, ?, ?, ?)",
                (type_, cat, desc, score, impact),
            )
    conn.commit()
    conn.close()
    print("Database seeded successfully!")
    return True
