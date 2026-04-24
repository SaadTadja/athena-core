"""
Athena Core — Helper Utilities
"""
import streamlit as st


def format_currency(value):
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M€"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K€"
    return f"{value:.0f}€"


def format_number(value):
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:.0f}"


def format_pct(value):
    return f"{value:+.1f}%"


def render_metric_card(label, value, delta=None, prefix="", suffix=""):
    delta_html = ""
    if delta is not None:
        css = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{css}">{arrow} {abs(delta):.1f}%</div>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def page_header(title, subtitle=""):
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sub-header">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
