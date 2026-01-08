import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="SAMA WOURY ELITE", layout="wide", page_icon="🐄")

# --- CONNEXION DB ---
conn = sqlite3.connect('ferme_elite_v4.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Table des travailleurs
    c.execute('CREATE TABLE IF NOT EXISTS utilisateurs (nom TEXT, code TEXT PRIMARY KEY)')
    # Table bétail
    c.execute('CREATE TABLE IF NOT EXISTS betail (id TEXT PRIMARY KEY, poids REAL, date TEXT, auteur TEXT)')
    # Table vaccins
    c.execute('CREATE TABLE IF NOT EXISTS vaccins (id_anim TEXT, vaccin TEXT, date_prevue TEXT, statut TEXT)')
    # Création du compte admin par défaut si vide
    c.execute("INSERT OR IGNORE INTO utilisateurs VALUES ('Admin', 'admin')")
    conn.commit()

init_db()

# --- AUTHENTIFICATION ---
st.sidebar.title("🇸🇳 SAMA WOURY V4")
nom_utilisateur = st.sidebar.text_input("Nom d'utilisateur")
code_acces = st.sidebar.text_input("Code secret", type="password")

# Vérification des identifiants
def verifier_login(nom, code):
    c.execute('SELECT * FROM utilisateurs WHERE nom=? AND code=?', (nom, code))
    return c.fetchone()

user_data = verifier_login(nom_utilisateur, code_acces)

# -------------------------------------------------------------------
# 1. INTERFACE PROPRIÉTAIRE (Si l'utilisateur est "Admin")
# -------------------------------------------------------------------
if user_data and user_data[0] == "Admin":
    st.header(f"👑 Bienvenue Patron ({nom_utilisateur})")
    
    menu = st.tabs(["📊 Stats & Bétail", "👥 Gestion Équipe", "📅 Vaccins"])

    with menu[0]:
        st.subheader("Registre du bétail")
        df_b = pd.read_sql_query("SELECT * FROM betail", conn)
        st.dataframe(df_b, use_container_width=True)

    with menu[1]:
        st.subheader("Créer un compte pour un travailleur")
        with st.form("nouveau_travailleur"):
            nouveau_nom = st.text_input("Nom du travailleur")
            nouveau_code = st.text_input("Code secret (ex: 1234)")
            if st.form_submit_button("Créer le compte"):
                try:
                    c.execute("INSERT INTO utilisateurs VALUES (?,?)", (nouveau_nom, nouveau_code))
                    conn.commit()
                    st.success(f"Compte créé pour {nouveau_nom} !")
                except:
                    st.error("Ce code est déjà utilisé par quelqu'un d'autre.")
        
        st.subheader("Liste de l'équipe")
        df_u = pd.read_sql_query("SELECT nom FROM utilisateurs WHERE nom != 'Admin'", conn)
        st.table(df_u)

    with menu[2]:
        st.subheader("Programmer un vaccin")
        v_anim = st.text_input("ID Animal")
        v_nom = st.selectbox("Vaccin", ["PPCB", "PPR", "Charbon"])
        if st.button("Valider"):
            c.execute("INSERT INTO vaccins VALUES (?,?,?,'A faire')", (v_anim, v_nom, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("Programmé !")

# -------------------------------------------------------------------
# 2. INTERFACE TRAVAILLEUR (Pour tous les autres comptes créés)
# -------------------------------------------------------------------
elif user_data:
    st.header(f"👷 Espace Terrain - {nom_utilisateur}")
    
    with st.form("saisie_terrain"):
        id_a = st.text_input("ID Animal")
        poids = st.number_input("Poids (kg)")
        if st.form_submit_button("Enregistrer la pesée"):
            c.execute("INSERT OR REPLACE INTO betail VALUES (?,?,?,?)", 
                      (id_a, poids, datetime.now().strftime("%Y-%m-%d"), nom_utilisateur))
            conn.commit()
            st.success("Donnée enregistrée !")

else:
    if nom_utilisateur or code_acces:
        st.error("Identifiants incorrects")
    else:
        st.info("Veuillez entrer votre nom et votre code à gauche.")
