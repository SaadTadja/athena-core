"""
Athena Core — Local Chatbot Engine (TF-IDF Intent Matching)
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from analytics.kpis import compute_revenue
from strategy.bcg_matrix import bcg_summary

class LocalChatbot:
    def __init__(self):
        # Base d'intentions (Corpus d'entrainement)
        self.intents = [
            {"intent": "greeting", "examples": ["bonjour", "salut", "hello", "coucou", "hey"]},
            {"intent": "kpi_revenue", "examples": ["quel est le chiffre d'affaires", "ca total", "combien on a gagné", "revenus actuels", "bilan financier"]},
            {"intent": "strategy_bcg", "examples": ["matrice bcg", "produits stars", "quels sont les produits vaches a lait", "stratégie produit", "produits à abandonner", "dogs"]},
            {"intent": "anomalies", "examples": ["y a t il des anomalies", "alertes", "problèmes", "baisse de ventes", "détection d'anomalies", "risques"]},
            {"intent": "recommendations", "examples": ["que dois je faire", "quelles sont les recommandations", "plan d'action", "conseils", "urgences"]},
        ]
        
        self.corpus = []
        self.intent_labels = []
        
        for item in self.intents:
            for ex in item["examples"]:
                self.corpus.append(ex.lower())
                self.intent_labels.append(item["intent"])
                
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def detect_intent(self, user_input):
        input_vec = self.vectorizer.transform([user_input.lower()])
        similarities = cosine_similarity(input_vec, self.tfidf_matrix)[0]
        max_idx = similarities.argmax()
        max_score = similarities[max_idx]
        
        if max_score > 0.3: # Threshold of confidence
            return self.intent_labels[max_idx]
        return "unknown"

    def get_response(self, user_input, context):
        """
        context is a dict containing precomputed data like:
        {'rev': 150000, 'bcg': df, 'recs': list, 'alerts': list}
        """
        intent = self.detect_intent(user_input)
        
        if intent == "greeting":
            return "Bonjour ! Je suis votre Assistant IA Athena Core. Comment puis-je vous aider avec l'analyse de vos données aujourd'hui ?"
            
        elif intent == "kpi_revenue":
            rev = context.get('rev', 0)
            return f"Le chiffre d'affaires global actuellement calculé est de **{rev:,.0f} €**. Vous pouvez voir les détails dans l'onglet **KPIs**."
            
        elif intent == "strategy_bcg":
            bcg = context.get('bcg')
            if bcg is not None and not bcg.empty:
                sum_bcg = bcg_summary(bcg)
                stars = sum_bcg[sum_bcg["quadrant"] == "Star"]["count"].sum() if "Star" in sum_bcg["quadrant"].values else 0
                dogs = sum_bcg[sum_bcg["quadrant"] == "Dog"]["count"].sum() if "Dog" in sum_bcg["quadrant"].values else 0
                return f"L'analyse BCG montre que nous avons **{int(stars)} produit(s) Star** (moteurs de croissance) et **{int(dogs)} produit(s) Dog** (à surveiller ou éliminer). Allez dans la page **Modèles Stratégiques** pour les détails."
            return "Je n'ai pas accès aux données BCG pour le moment."
            
        elif intent == "anomalies":
            alerts = context.get('alerts', [])
            if not alerts:
                return "Je n'ai détecté **aucune anomalie** ou alerte majeure dans les ventes récentes."
            else:
                resp = "J'ai détecté quelques alertes récentes :\n"
                for a in alerts[:3]:
                    resp += f"- {a['message']}\n"
                return resp
                
        elif intent == "recommendations":
            recs = context.get('recs', [])
            high = [r for r in recs if r["priority"] == "HIGH"]
            if high:
                resp = f"J'ai identifié **{len(high)} action(s) prioritaire(s)** :\n"
                for r in high[:3]:
                    resp += f"- **[{r['action']}]** sur {r['target']} : {r['reason']}\n"
                return resp
            else:
                return "Tout semble nominal. Je vous recommande de maintenir la stratégie actuelle."
                
        else:
            return "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ? (Essayez de m'interroger sur : *les recommandations, le chiffre d'affaires, les anomalies ou la stratégie BCG*)."
