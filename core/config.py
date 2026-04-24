"""
Athena Core — Configuration Globale
"""
import os

# ─── Database ────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "antigravity.db")
DB_URL = f"sqlite:///{DB_PATH}"

# ─── App ─────────────────────────────────────────────────────────
APP_NAME = "Athena Core"
APP_ICON = "■"
APP_VERSION = "1.0.0"

# ─── Colors ──────────────────────────────────────────────────────
COLORS = {
    "primary": "#2563EB", # Corporate Blue
    "secondary": "#64748B", # Slate
    "success": "#10B981", # Emerald
    "warning": "#F59E0B", # Amber
    "danger": "#EF4444", # Red
    "info": "#3B82F6",
    "purple": "#6366F1", # Indigo
    "pink": "#EC4899",
    "bg_dark": "#0F172A", # Dark Slate
    "bg_card": "#1E293B", # Slate
    "bg_card_hover": "#334155",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border": "#334155",
}

# ─── BCG Quadrant Colors ────────────────────────────────────────
BCG_COLORS = {
    "Star": "#3B82F6",         # Blue
    "Cash Cow": "#10B981",     # Emerald
    "Question Mark": "#F59E0B", # Amber
    "Dog": "#EF4444",          # Red
}

# ─── Chart Template ─────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"

# ─── Seed Data Parameters ───────────────────────────────────────
SEED_CUSTOMERS = 500
SEED_PRODUCTS = 50
SEED_CATEGORIES = 5
SEED_ORDERS = 10000
SEED_DAYS = 730  # 2 years
