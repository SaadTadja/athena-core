"""
Athena Core — Custom CSS Styles
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

h1, h2, h3, h4, h5, h6, p, .metric-value, .sub-header, .metric-label {
    font-family: 'Roboto', sans-serif;
}

/* Main header */
.main-header {
    color: #F8FAFC;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #1E3A8A;
}

.sub-header {
    color: #94A3B8;
    font-size: 1.05rem;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* Metric cards */
.metric-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 0.5rem;
}
.metric-label {
    font-size: 0.8rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}
.metric-delta-positive {
    color: #10B981;
    font-size: 0.85rem;
    font-weight: 500;
}
.metric-delta-negative {
    color: #EF4444;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Recommendation cards */
.rec-card {
    background: #1E293B;
    border-left: 4px solid;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border-top: 1px solid #334155;
    border-right: 1px solid #334155;
    border-bottom: 1px solid #334155;
}
.rec-high { border-left-color: #EF4444; }
.rec-medium { border-left-color: #F59E0B; }
.rec-low { border-left-color: #10B981; }

/* SWOT grid */
.swot-card {
    border-radius: 4px;
    padding: 1.2rem;
    min-height: 150px;
}
.swot-force { background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); }
.swot-faiblesse { background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); }
.swot-opportunite { background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); }
.swot-menace { background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); }

/* Section dividers */
.section-divider {
    border: none;
    height: 1px;
    background: #334155;
    margin: 2rem 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0F172A;
    border-right: 1px solid #1E293B;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 4px 4px 0 0;
    padding: 8px 16px;
    background: transparent;
}
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
