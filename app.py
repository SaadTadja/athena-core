import streamlit as st
from utils.styles import inject_css

def main():
    # Page configuration
    st.set_page_config(
        page_title="Athena Core — Intelligence Stratégique",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom styles
    inject_css()
    
    # Hero Section
    st.markdown('<div class="main-header">Athena Core v1.0.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Plateforme d\'intelligence stratégique et d\'analyse prédictive pour la Supply Chain.</div>', unsafe_allow_html=True)
    
    import base64
    def get_img_as_base64(file):
        try:
            with open(file, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception:
            return ""

    img_base64 = get_img_as_base64("assets/aristotle.png")
    img_html = f'<img src="data:image/png;base64,{img_base64}" style="width: 120px; border-radius: 8px; border: 1px solid #D4AF37; box-shadow: 0 4px 12px rgba(0,0,0,0.5); object-fit: cover;">' if img_base64 else ''

    st.markdown(f"""
    <div class="greek-quote-container" style="display: flex; align-items: center; justify-content: center; gap: 2rem; text-align: left;">
        {img_html}
        <div>
            <div class="greek-quote">
                "L'intelligence ne consiste pas seulement dans la connaissance, mais dans l'aptitude à appliquer la connaissance à la pratique."
            </div>
            <div class="greek-author">— Aristote</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Actions
    with st.sidebar:
        if st.button("Vider le cache complet", use_container_width=True):
            # Clear all data from the SQLite database
            from core.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            tables = ["strategic_inputs", "market_data", "order_items",
                       "orders", "products", "customers", "categories"]
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            conn.close()
            # Clear Streamlit cache so loaders fetch the now-empty database
            st.cache_data.clear()
            # Clear any session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            

    # Overview Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Bienvenue dans votre poste de pilotage")
        st.info("""
        Athena Core est conçu pour transformer vos données brutes en décisions stratégiques. 
        Utilisez les modules dans la barre latérale pour naviguer à travers les différentes étapes de l'analyse.
        """)
        
        st.markdown("#### Pour commencer")
        st.write("""
        1. **Importation :** Allez dans la section **'Import Donnees'** pour charger vos fichiers.
        2. **KPIs :** Visualisez vos indicateurs de performance en temps réel.
        3. **Analyses :** Explorez les tendances et les anomalies détectées par l'IA.
        4. **Stratégie :** Générez des modèles SWOT et des recommandations actionnables.
        """)
        
        st.markdown("---")
        st.markdown("#### Jeu de données de test")
        st.success(f"Un jeu de données de test a été généré pour vous sur votre Bureau : `athena_test_dataset.csv`")
        st.write("Vous pouvez l'utiliser immédiatement dans l'onglet **Import Donnees** pour tester les capacités de traitement de plus de 10,000 lignes.")

    with col2:
        st.markdown("#### État du Système")
        st.markdown('<div class="metric-card"><div class="metric-label">Status</div><div class="metric-value">Opérationnel</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><div class="metric-label">Version</div><div class="metric-value">1.0.0-Stable</div></div>', unsafe_allow_html=True)
        
        with st.expander("Notes de version"):
            st.write("""
            - Intégration de modèles XGBoost pour la prédiction.
            - Nouveau moteur de rendu pour les rapports PDF.
            - Assistant IA contextuel amélioré.
            """)

    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.caption("Athena Core — Système d'aide à la décision propulsé par l'IA.")

if __name__ == "__main__":
    main()
