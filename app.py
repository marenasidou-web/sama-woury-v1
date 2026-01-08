import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SAMA WOURY ELITE", layout="wide", initial_sidebar_state="expanded")

# --- BASE DE DONNÉES ---
conn = sqlite3.connect('ferme_elite.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS betail (id TEXT PRIMARY KEY, type TEXT, poids REAL, sante TEXT, date_entree TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS finances (id INTEGER PRIMARY KEY, type TEXT, montant REAL, date TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS stock (aliment TEXT PRIMARY KEY, qte REAL)')
    conn.commit()

init_db()

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #2E7D32; color: white; }
    .worker-card { padding: 20px; background-color: white; border-radius: 15px; border-left: 5px solid #1976D2; margin-bottom: 10px; }
    .owner-card { padding: 20px; background-color: white; border-radius: 15px; border-left: 5px solid #2E7D32; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
st.sidebar.title("🔐 SAMA WOURY ELITE")
role = st.sidebar.selectbox("Rôle", ["Travailleur", "Propriétaire"])
mdp = st.sidebar.text_input("Code d'accès", type="password")

# ---------------------------------------------------------
# INTERFACE TRAVAILLEUR (L'ESSENTIEL)
# ---------------------------------------------------------
if role == "Travailleur" and mdp == "1234":
    st.markdown("<h1 style='color: #1976D2;'>👷 Espace Terrain</h1>", unsafe_allow_html=True)
    
    onglet1, onglet2, onglet3 = st.tabs(["📝 Saisie", "🏥 Santé IA", "📦 Stocks"])

    with onglet1:
        st.subheader("Enregistrer un mouvement")
        with st.form("form_travailleur"):
            id_anim = st.text_input("ID de la bête (Boucle)")
            poids = st.number_input("Poids mesuré (kg)", min_value=0.0)
            if st.form_submit_button("Valider la pesée"):
                c.execute("INSERT OR REPLACE INTO betail (id, poids, date_entree) VALUES (?,?,?)", 
                          (id_anim, poids, datetime.now().strftime("%d-%m-%Y")))
                conn.commit()
                st.success("Donnée enregistrée !")

    with onglet2:
        st.subheader("🩺 Check-up Santé Rapide")
        st.write("Cochez les signes observés :")
        s1 = st.checkbox("Ne mange pas")
        s2 = st.checkbox("Yeux qui coulent / Toux")
        s3 = st.checkbox("Boiterie (marche mal)")
        if st.button("Analyser les risques"):
            if s1 or s2 or s3:
                st.error("⚠️ ALERTE : Risque de maladie détecté. Isolez l'animal et prévenez le patron.")
            else:
                st.success("✅ L'animal semble en bonne santé.")

    with onglet3:
        st.subheader("Vérification des aliments")
        st.info("Consultez les sacs restants en magasin.")
        # Affichage simple des quantités pour le travailleur
        data = pd.read_sql_query("SELECT aliment, qte FROM stock", conn)
        st.table(data)

# ---------------------------------------------------------
# INTERFACE PROPRIÉTAIRE (GESTION COMPLÈTE)
# ---------------------------------------------------------
elif role == "Propriétaire" and mdp == "admin":
    st.markdown("<h1 style='color: #2E7D32;'>👑 Administration Ferme</h1>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Navigation", ["Tableau de Bord", "IA & Nutrition", "Marché & Ventes", "Météo & Risques"])

    if menu == "Tableau de Bord":
        col1, col2, col3 = st.columns(3)
        res = pd.read_sql_query("SELECT COUNT(*) FROM betail", conn).iloc[0,0]
        col1.metric("Bétail Total", f"{res} têtes")
        
        ventes = pd.read_sql_query("SELECT SUM(montant) FROM finances WHERE type='Vente'", conn).iloc[0,0] or 0
        col2.metric("Chiffre d'Affaire", f"{ventes:,} FCFA")
        col3.metric("État Alerte", "Faible", delta="-2%")

        st.subheader("Registre du Bétail")
        df_b = pd.read_sql_query("SELECT * FROM betail", conn)
        st.dataframe(df_b, use_container_width=True)

    elif menu == "IA & Nutrition":
        st.subheader("🥗 Calculateur de Ration IA")
        poids_cible = st.slider("Poids cible (kg)", 50, 500, 200)
        st.write("Pour atteindre ce poids en 3 mois, l'IA conseille :")
        st.success(f"• Mélange : {poids_cible*0.02:.1f}kg de foin + {poids_cible*0.01:.1f}kg de concentrés / jour.")

    elif menu == "Marché & Ventes":
        st.subheader("🛒 Place de Marché (Export WhatsApp)")
        st.write("Générez une fiche de vente pour vos clients.")
        id_vente = st.selectbox("Choisir l'animal à vendre", pd.read_sql_query("SELECT id FROM betail", conn))
        prix = st.number_input("Prix de vente (FCFA)", min_value=0)
        if st.button("Partager sur WhatsApp"):
            msg = f"Vente Ferme Elite : Animal ID {id_vente} disponible. Prix : {prix} FCFA."
            st.info(f"Texte à copier : {msg}")
            # Note: Le lien réel whatsapp://send se ferait via un composant HTML

    elif menu == "Météo & Risques":
        st.subheader("🌦️ Prévisions & Alertes")
        st.warning("🔥 ALERTE CHALEUR : Température prévue 42°C demain. Augmentez l'eau de 30%.")
        st.info("💡 Conseil : Nettoyage des enclos recommandé ce jeudi avant les pluies de vendredi.")

else:
    if mdp != "":
        st.error("Code d'accès incorrect.")
    else:
        st.info("Veuillez vous connecter à gauche.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("SAMA WOURY v2.0 - 2026")
