import streamlit as st
import pandas as pd
import io
import docx
from PyPDF2 import PdfReader

from utils.styles import inject_css
from utils.helpers import page_header
from core.database import get_connection, init_tables

st.set_page_config(page_title="Import de Données — Athena Core", layout="wide")
inject_css()
page_header("Importation des Données", "Ajoutez vos propres jeux de données (Excel/CSV) et rapports stratégiques (Word/PDF)")

tab1, tab2 = st.tabs(["Données Chiffrées (Ventes)", "Données Qualitatives (Notes)"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — VENTES (CSV / EXCEL)
# ═══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Importation des Transactions (Commandes & Produits)")
    st.info("Veuillez importer un fichier de ventes. Vous pourrez associer vos colonnes aux champs requis par la plateforme.")
    
    uploaded_file = st.file_uploader("Glissez votre fichier de ventes", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='utf-8', low_memory=False)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.success(f"Fichier chargé avec succès ! ({len(df)} lignes trouvées)")
            st.dataframe(df.head(3), width="stretch")
            
            st.markdown("### 🔄 Mappage des colonnes")
            st.write("Associez les colonnes de votre fichier aux champs requis par Athena Core.")
            
            cols = list(df.columns)
            
            def get_index(possible_names):
                for name in possible_names:
                    for i, col in enumerate(cols):
                        if name.lower() in str(col).lower():
                            return i
                return 0

            col1, col2 = st.columns(2)
            with col1:
                col_order_id = st.selectbox("ID Commande (Requis)", options=cols, index=get_index(["order id", "commande", "id"]))
                col_date = st.selectbox("Date de Commande (Requis)", options=cols, index=get_index(["date"]))
                col_sales = st.selectbox("Chiffre d'Affaires / Ventes (Requis)", options=cols, index=get_index(["sales", "vente", "ca", "revenue"]))
                col_qty = st.selectbox("Quantité (Requis)", options=cols, index=get_index(["quantit", "qty"]))
            with col2:
                col_profit = st.selectbox("Profit / Marge (Optionnel)", options=["--- Non disponible ---"] + cols, index=get_index(["profit", "marge"])+1 if get_index(["profit", "marge"]) != 0 else 0)
                col_product_id = st.selectbox("ID Produit (Requis)", options=cols, index=get_index(["product id", "produit id", "ref"]))
                col_product_name = st.selectbox("Nom du Produit (Requis)", options=cols, index=get_index(["product name", "nom produit", "article"]))
                col_customer = st.selectbox("Nom du Client (Requis)", options=cols, index=get_index(["customer", "client"]))
                col_category = st.selectbox("Catégorie (Optionnel)", options=["--- Non disponible ---"] + cols, index=get_index(["categor", "famille"])+1 if get_index(["categor", "famille"]) != 0 else 0)
            
            if st.button("Remplacer la base de données avec ce fichier", type="primary"):
                with st.spinner("Traitement et injection des données..."):
                    from data.data_ingestion import reset_database, process_and_inject_df
                    
                    mapping = {
                        col_order_id: "order_id", col_date: "order_date", col_sales: "sales",
                        col_qty: "quantity", col_product_id: "product_id", 
                        col_product_name: "product_name", col_customer: "customer_name"
                    }
                    if col_profit != "--- Non disponible ---": mapping[col_profit] = "profit"
                    if col_category != "--- Non disponible ---": mapping[col_category] = "sub_category"
                        
                    df_mapped = df.rename(columns=mapping)
                    
                    # Apply defaults for optional columns if missing
                    if "profit" not in df_mapped.columns: df_mapped["profit"] = df_mapped["sales"] * 0.2
                    if "sub_category" not in df_mapped.columns: df_mapped["sub_category"] = "Général"
                    if "category" not in df_mapped.columns: df_mapped["category"] = df_mapped["sub_category"]
                    if "discount" not in df_mapped.columns: df_mapped["discount"] = 0.0
                    if "customer_id" not in df_mapped.columns: df_mapped["customer_id"] = df_mapped["customer_name"]
                    if "segment" not in df_mapped.columns: df_mapped["segment"] = "Standard"
                    if "city" not in df_mapped.columns: df_mapped["city"] = "Inconnue"
                    if "country" not in df_mapped.columns: df_mapped["country"] = "Inconnu"
                    if "ship_mode" not in df_mapped.columns: df_mapped["ship_mode"] = "Standard Class"
                        
                    try:
                        df_mapped["order_date"] = pd.to_datetime(df_mapped["order_date"])
                        reset_database()
                        process_and_inject_df(df_mapped)
                        st.cache_data.clear()
                        st.success("✅ Base de données remplacée avec succès ! Vous pouvez maintenant explorer vos propres données.")
                    except Exception as e:
                        st.error(f"⚠️ Erreur lors de l'injection : {e}")

        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
# ═══════════════════════════════════════════════════════════════════
# TAB 2 — QUALITATIF (PDF / WORD)
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Importation de Rapports et Notes Stratégiques")
    st.caption("Le texte extrait sera ajouté aux inputs stratégiques de l'entreprise (SWOT, PESTEL, etc.)")
    
    doc_file = st.file_uploader("Glissez votre rapport", type=['pdf', 'docx', 'txt'])
    
    if doc_file is not None:
        text_content = ""
        try:
            if doc_file.name.endswith('.pdf'):
                reader = PdfReader(doc_file)
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            elif doc_file.name.endswith('.docx'):
                doc = docx.Document(doc_file)
                for para in doc.paragraphs:
                    text_content += para.text + "\n"
            elif doc_file.name.endswith('.txt'):
                text_content = doc_file.getvalue().decode("utf-8")
                
            st.success("Texte extrait avec succès !")
            with st.expander("Aperçu du contenu extrait", expanded=True):
                st.text(text_content[:1000] + ("..." if len(text_content) > 1000 else ""))
                
            category_choice = st.selectbox("Catégoriser ce document", ["Analyse SWOT", "PESTEL", "Analyse Concurrentielle", "Notes Diverses"])
            
            if st.button("Ajouter à la base de connaissances", type="primary"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO strategic_inputs (type, category, description, score, impact) VALUES (?, ?, ?, ?, ?)",
                               (category_choice, "Document Uploadé", f"Extrait du fichier {doc_file.name}", 5, 0))
                conn.commit()
                conn.close()
                st.success("Document archivé et indexé pour les recommandations IA.")
                
        except Exception as e:
            st.error(f"Impossible d'extraire le texte : {e}")
