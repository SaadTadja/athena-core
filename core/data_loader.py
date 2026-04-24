"""
Athena Core — Data Loader with Caching
"""
import streamlit as st
import pandas as pd
from core.database import query_df


@st.cache_data(ttl=3600)
def load_orders():
    """Load all orders with customer info."""
    return query_df("""
        SELECT o.*, c.name as customer_name, c.segment, c.city, c.country
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
    """)


@st.cache_data(ttl=3600)
def load_order_items():
    """Load all order items with product and category info."""
    return query_df("""
        SELECT oi.*, o.order_date, o.customer_id, o.channel,
               p.name as product_name, p.category_id, p.price as catalog_price, p.cost,
               cat.name as category_name
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        LEFT JOIN categories cat ON p.category_id = cat.id
    """)


@st.cache_data(ttl=3600)
def load_products():
    """Load all products with category info."""
    return query_df("""
        SELECT p.*, cat.name as category_name
        FROM products p
        LEFT JOIN categories cat ON p.category_id = cat.id
    """)


@st.cache_data(ttl=3600)
def load_customers():
    """Load all customers."""
    return query_df("SELECT * FROM customers")


@st.cache_data(ttl=3600)
def load_market_data():
    """Load market data for strategic analysis."""
    return query_df("""
        SELECT md.*, p.name as product_name, cat.name as category_name
        FROM market_data md
        JOIN products p ON md.product_id = p.id
        LEFT JOIN categories cat ON p.category_id = cat.id
    """)


@st.cache_data(ttl=3600)
def load_daily_revenue():
    """Load daily revenue aggregation."""
    return query_df("""
        SELECT o.order_date,
               SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) as revenue,
               COUNT(DISTINCT o.id) as num_orders,
               SUM(oi.quantity) as units_sold
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.order_date
        ORDER BY o.order_date
    """)


@st.cache_data(ttl=3600)
def load_strategic_inputs():
    """Load strategic inputs for SWOT/PESTEL/Porter."""
    return query_df("SELECT * FROM strategic_inputs")
