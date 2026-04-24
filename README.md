# Athena Core

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)

**Athena Core** is an intelligent, end-to-end Decision-Support Platform designed for modern enterprises. It processes complex sales data and strategic inputs to deliver actionable insights through a powerful four-tiered intelligence architecture.

## 🚀 Features

Athena Core provides insights across four distinct levels:

1. **Classic KPIs:** Revenue, Orders, Average Basket, Gross Margin, and Top Products.
2. **Advanced Analytics:** Trend detection, RFM (Recency, Frequency, Monetary) segmentation, and deeper performance metrics.
3. **Strategic Models:** Automatically generated strategic frameworks including the BCG Matrix, McKinsey Matrix, SWOT, PESTEL, and Porter's Five Forces.
4. **Artificial Intelligence:** Machine Learning models (Scikit-learn, XGBoost) for sales forecasting, anomaly detection, automated recommendations, and an AI-driven Chatbot Assistant.

## 🛠️ Architecture & Tech Stack

- **Frontend Interface:** Built with [Streamlit](https://streamlit.io/) for a dynamic, reactive user experience.
- **Data Processing:** Powered by `pandas` and `numpy`.
- **Database:** `SQLite` ensures a lightweight, reliable local data store.
- **Machine Learning:** `scikit-learn` and `xgboost` power the predictive intelligence.
- **Visualizations:** Interactive charts built with `plotly`.

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/athena-core.git
   cd athena-core
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📊 Using Your Own Data

Athena Core features a highly flexible data import pipeline. 
Navigate to the **"Import Données"** tab in the application to upload your own CSV or Excel transaction files. The built-in column mapping interface will seamlessly adapt your data schema to the core models.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
