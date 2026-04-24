"""
Athena Core — Plotly Chart Factories
"""
import plotly.express as px
import plotly.graph_objects as go
from core.config import COLORS, BCG_COLORS, PLOTLY_TEMPLATE


def _base_layout(fig, title=""):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text=title, font=dict(size=16, color=COLORS["text"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text_muted"]),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="rgba(45,53,72,0.5)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(45,53,72,0.5)", zeroline=False)
    return fig


def line_chart(df, x, y, title="", color=None):
    if df.empty:
        return _base_layout(go.Figure(), title)
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_traces(line=dict(width=2.5))
    return _base_layout(fig, title)


def bar_chart(df, x, y, title="", orientation="v", color=None):
    if df.empty:
        return _base_layout(go.Figure(), title)
    fig = px.bar(df, x=x, y=y, orientation=orientation, color=color, title=title)
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return _base_layout(fig, title)


def pie_chart(df, names, values, title=""):
    if df.empty:
        return _base_layout(go.Figure(), title)
    fig = px.pie(df, names=names, values=values, title=title, hole=0.45)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _base_layout(fig, title)


def scatter_chart(df, x, y, size=None, color=None, text=None, title=""):
    if df.empty:
        return _base_layout(go.Figure(), title)
    fig = px.scatter(df, x=x, y=y, size=size, color=color, text=text,
                     title=title, size_max=60)
    if text:
        fig.update_traces(textposition="top center")
    return _base_layout(fig, title)


def bcg_chart(bcg_df):
    fig = go.Figure()
    if bcg_df.empty:
        fig.update_layout(xaxis_title="Part de Marché Relative", yaxis_title="Taux de Croissance")
        return _base_layout(fig, "Matrice BCG — Portefeuille Produits")
    for quad in bcg_df["quadrant"].unique():
        subset = bcg_df[bcg_df["quadrant"] == quad]
        fig.add_trace(go.Scatter(
            x=subset["relative_market_share"], y=subset["market_growth_rate"],
            mode="markers", name=quad,
            marker=dict(size=subset["revenue"] / subset["revenue"].max() * 50 + 10,
                        color=BCG_COLORS.get(quad, "#888"), opacity=0.8,
                        line=dict(width=1, color="white")),
            hovertext=subset["product_name"],
            hovertemplate="<b>%{hovertext}</b><br>Part de marché: %{x:.2f}<br>Croissance: %{y:.2f}<extra></extra>"
        ))
    ms = bcg_df["median_share"].iloc[0]
    mg = bcg_df["median_growth"].iloc[0]
    fig.add_hline(y=mg, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig.add_vline(x=ms, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig.update_layout(xaxis_title="Part de Marché Relative", yaxis_title="Taux de Croissance")
    return _base_layout(fig, "Matrice BCG — Portefeuille Produits")


def mckinsey_chart(mck_df):
    if mck_df.empty:
        return _base_layout(go.Figure(), "Matrice McKinsey / GE")
    fig = px.scatter(mck_df, x="position_score", y="attractiveness_score",
                     size="revenue", color="strategy", hover_name="product_name",
                     size_max=50, color_discrete_map={
                         "Investir": "#10B981", "Sélectif": "#F59E0B",
                         "Récolter": "#EF4444"})
    # Removed textposition since text is removed
    fig.add_hline(y=6, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_hline(y=3, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=6, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=3, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.update_layout(xaxis_title="Position Concurrentielle", yaxis_title="Attractivité du Marché",
                      xaxis=dict(range=[0, 10]), yaxis=dict(range=[0, 10]))
    return _base_layout(fig, "Matrice McKinsey / GE")


def radar_chart(categories, values, title=""):
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(108,99,255,0.2)",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=8, color=COLORS["primary"]),
    ))
    fig.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, gridcolor="rgba(45,53,72,0.5)", color=COLORS["text_muted"]),
        angularaxis=dict(gridcolor="rgba(45,53,72,0.5)", color=COLORS["text"]),
    ))
    return _base_layout(fig, title)


def anomaly_chart(df):
    fig = go.Figure()
    if df.empty:
        return _base_layout(fig, "Détection d'Anomalies — Revenue")
    normal = df[~df["is_anomaly"]]
    anomalies = df[df["is_anomaly"]]
    fig.add_trace(go.Scatter(x=normal["order_date"], y=normal["revenue"],
                             mode="lines", name="Revenue", line=dict(color=COLORS["primary"], width=1.5)))
    fig.add_trace(go.Scatter(x=anomalies["order_date"], y=anomalies["revenue"],
                             mode="markers", name="Anomalies",
                             marker=dict(size=10, color=COLORS["danger"], symbol="diamond",
                                         line=dict(width=2, color="white"))))
    return _base_layout(fig, "Détection d'Anomalies — Revenue")


def forecast_chart(hist_df, forecast_df, metrics):
    fig = go.Figure()
    if hist_df.empty or forecast_df.empty:
        return _base_layout(fig, "Prévision des Ventes — 30 Jours")
    fig.add_trace(go.Scatter(x=hist_df["order_date"], y=hist_df["revenue"],
                             mode="lines", name="Historique", line=dict(color=COLORS["primary"], width=1.5)))
    fig.add_trace(go.Scatter(x=forecast_df["date"], y=forecast_df["predicted_revenue"],
                             mode="lines+markers", name="Prévision",
                             line=dict(color=COLORS["success"], width=2, dash="dash"),
                             marker=dict(size=4)))
    if metrics.get("test_dates") is not None and len(metrics["test_dates"]) > 0:
        fig.add_trace(go.Scatter(x=metrics["test_dates"], y=metrics["y_pred"],
                                 mode="lines", name="Prédiction (test)",
                                 line=dict(color=COLORS["warning"], width=1.5, dash="dot")))
    return _base_layout(fig, "Prévision des Ventes — 30 Jours")
