# Athena Core

![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/-Streamlit-05122A?style=flat&logo=streamlit)
![scikit-learn](https://img.shields.io/badge/-scikit--learn-05122A?style=flat&logo=scikit-learn)

**Athena Core** is an intelligent, end-to-end Decision-Support Platform designed for modern enterprises. It processes complex sales data and strategic inputs to deliver actionable insights through a powerful four-tiered intelligence architecture.

<!-- A screenshot or short GIF of the dashboard belongs here: it is the single
     biggest factor in whether a visitor explores the repo. Save one as
     docs/screenshot.png and uncomment the line below.
![Athena Core dashboard](docs/screenshot.png)
-->

## Features

Athena Core provides insights across four distinct levels:

1. **Classic KPIs** — Revenue, Orders, Average Basket, Gross Margin, and Top Products.
2. **Advanced Analytics** — Trend detection, RFM (Recency, Frequency, Monetary) segmentation, and deeper performance metrics.
3. **Strategic Models** — Automatically generated strategic frameworks including the BCG Matrix, McKinsey Matrix, SWOT, PESTEL, and Porter's Five Forces.
4. **Advanced Algorithms** — Machine learning for revenue forecasting, anomaly detection, automated recommendations, and a predictive chatbot assistant.

## Machine learning

| Task | Approach | Notes |
|---|---|---|
| Revenue forecasting | `RandomForestRegressor` validated with `TimeSeriesSplit` | R² ≈ 0.92 on the test set; feature importances exposed in the UI |
| Anomaly detection | `IsolationForest` | Combined with a z-score check to flag revenue spikes and drops |
| Segmentation | RFM scoring | Recency, frequency and monetary value per customer |
| Recommendations | Rule and score based | Derived from the analytics layer |

Forecasting is validated chronologically rather than with a random split, so a
model is never scored on data that precedes its training window.

## Architecture & tech stack

- **Interface** — [Streamlit](https://streamlit.io/), multi-page, with a themed dark UI
- **Data processing** — `pandas` and `numpy`
- **Database** — `SQLite`, a lightweight local store
- **Machine learning** — `scikit-learn`, with `xgboost` and `statsmodels` available for the analytics layer
- **Visualisation** — interactive charts with `plotly`

## Project structure

```
app.py                  entry point
pages/                  Import, KPIs, Advanced analysis, Strategic models,
                        Advanced analytics, Final report, Strategy assistant
ai/                     sales_predictor, anomaly_detector,
                        recommendation_engine, chatbot_engine
analytics/              kpis, performance, segmentation, trends
strategy/               strategic framework generation
core/                   config, data_loader, database
data/                   data_ingestion, seed_data
```

## Installation & setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SaadTadja/athena-core.git
   cd athena-core
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Using your own data

Athena Core features a flexible data import pipeline. Open the **Import Données**
page in the app to upload your own CSV or Excel transaction files — the built-in
column mapping interface adapts your schema to the core models, so column names
do not have to match in advance.

## License

MIT — see [LICENSE](LICENSE).
