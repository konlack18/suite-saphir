import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
import time
from datetime import datetime, timedelta

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(
    page_title="SAPHIR Suite v1.0 - Écosystème Industriel Sécurisé",
    page_icon="🛡️",
    layout="wide"
)

# --- SIMULATION DE BASE DE DONNÉES PERMANENTE EN SESSIONS STATE ---
# Dans une vraie prod, cela pointerait vers une base de données PostgreSQL / PostGIS
if "base_champs_systeme" not in st.session_state:
    st.session_state["base_champs_systeme"] = [
        {
            "id": "Cacao_Minta_01",
            "producteur": "Jean-Pierre Omgba",
            "pays": "Cameroun",
            "localite": "Meba",
            "speculation": "Cacao (Theobroma cacao)",
            "superficie": 2.5,
            "statut": "✅ Mapée (Polygone validé)",
            "dernier_passage_satellite": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "indice_sante_ndvi": 0.78, # 1.0 = Parfaite santé, proche de 0 = anomalie/maladie
            "alerte_active": False
        },
        {
            "id": "Maïs_Kango_02",
            "producteur": "Marc Ndong",
            "pays": "Gabon",
            "localite": "Menei",
            "speculation": "Maïs Jaune (Zea mays)",
            "superficie": 4.0,
            "statut": "✅ Mapée (Polygone validé)",
            "dernier_passage_satellite": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
            "indice_sante_ndvi": 0.32, # Alerte critique détectée par le satellite
            "alerte_active": True,
            "pathologie_detectee": "Helminthosporiose du Maïs",
            "protocole_active": "J+1 Engagé (Traitement antifongique cuprique localisé)"
        }
    ]

# Autre initialisation des sessions states
if "consentement_valide" not in st.session_state:
    st.session_state["consentement_valide"] = False
if "step_mapping_actif" not in st.session_state:
    st.session_state["step_mapping_actif"] = False
if "sms_envoyes_log" not in st.session_state:
    st.session_state["sms_envoyes_log"] = []

# --- BASE DE DONNÉES ADMINISTRATIVE CEMAC ---
CEMAC_DATA = {
    "Cameroun": {"type": "Région", "divisions": {"Centre": {"Haute-Sanaga": ["Mbandjock", "Minta", "Nanga-Eboko"]}}},
    "Gabon": {"type": "Province", "divisions": {"Estuaire": {"Kango": ["Kango Centre", "Menei"]}}}
}

RUBRIQUES_ACTIVITES = {
    "Production Végétale": ["Cacao (Theobroma cacao)", "Café Robusta", "Maïs Jaune", "Manioc / Cassava"]
}

# --- HEADER ET BANDEAU CONNECTÉ ---
st.title("🛡️ SAPHIR Suite v1.0 — Plateforme Agro-Industrielle Intégrée")
st.caption("Propriété exclusive de GODGIE Group — Directeur de Projet : Ing. Roméo Moffo Konlack")

st.markdown("---")

# SÉLECTION DES NIVEAUX D'ACCÈS
user_role = st.radio(
    "Veuillez choisir votre profil d'accès pour adapter l'affichage :",
    ["🧑‍🌾 Espace Terrain & Enquêtes (SAPHIR Field)", "📡 Centre de Contrôle Satellitaire & Phytosanitaire (SAPHIR Core & Pharma)"],
    horizontal=True
)

st.markdown("---")

# =====================================================================
# MODULE FIELD & ENREGISTREMENT PERMANENT
# =====================================================================
if user_role == "🧑‍🌾 Espace Terrain & Enquêtes (SAPHIR Field)":
    st.header("📍 SAPHIR Field — Capture & Mapping Polygonal")
    
    if not st.session_state["step_mapping_actif"]:
        with st.form("form_producteur"):
            st.subheader("📝 Étape 1 : Informations Générales & Géographiques")
            col1, col2, col3 = st.columns(3)
            with col1:
                sel_pays = st.selectbox("Pays :", list(CEMAC_DATA.keys()))
            with col2:
                sel_localite = st.text_input("Localité (Saisie Manuelle) :", value="Meba")
            with col3:
                p_nom = st.text_input("Nom complet du producteur :", value="Ebenezer Manga")
                
            col4, col5 = st.columns(2)
            with col4:
                p_spec = st.selectbox("Spéculation principale :", RUBRIQUES_ACTIVITES["Production Végétale"])
            with col5:
                p_surf = st.number_input("Superficie estimée (Ha) :", min_value=0.1, value=1.5)
                
            st.write("📸 **Biométrie & Pièce d'identité**")
            st.camera_input("Prise de vue du producteur", key="p_photo")
            
            signature = st.checkbox("Le producteur signe numériquement le registre foncier.")
            
            submit_btn = st.form_submit_button("💾 Enregistrer et Passer au Mapping")
            if submit_btn and signature:
                st.session_state["nouveau_champ_temp"] = {
                    "id": f"{p_spec.split(' ')[0]}_{sel_localite}_{np.random.randint(10,99)}",
                    "producteur": p_nom, "pays": sel_pays, "localite": sel_localite,
                    "speculation": p_spec, "superficie": p_surf, "statut": "❌ Non Mapée",
                    "dernier_passage_satellite": "Aucun (En attente d'acquisition)",
                    "indice_sante_ndvi": 1.0, "alerte_active": False
                }
                st.session_state["step_mapping_actif"] = True
                st.rerun()

    else:
        st.subheader("🛰️ Arpentage Radar & Sauvegarde dans le Système")
        champ = st.session_state["nouveau_champ_temp"]
        st.info(f"Parcelle en cours d'arpentage : **{champ['id']}** ({champ['speculation']})")
        
        st.caption("Marchez le long des limites physiques de la parcelle pour clore le polygone.")
        
        if st.button("🏁 Valider le contour polygonal et injecter dans le système permanent"):
            champ["statut"] = "✅ Mapée (Polygone validé)"
            champ["dernier_passage_satellite"] = datetime.now().strftime("%Y-%m-%d")
            
            # Injection permanente dans la base du système
            st.session_state["base_champs_systeme"].append(champ)
            
            st.success(f"🎉 Le champ **{champ['id']}** a été enregistré avec succès et est désormais surveillé par le réseau satellite !")
            st.session_state["step_mapping_actif"] = False
            time.sleep(2)
            st.rerun()

# =====================================================================
# CENTRE DE CONTRÔLE SATELLITAIRE & PHYTO (SAPHIR CORE & PHARMA)
# =====================================================================
else:
    st.header("🛰️ SAPHIR Core & Pharma — Tour de Contrôle Spatiale")
    st.write("Ce module simule l'acquisition des données des satellites **Sentinel-2** et **Landsat** (fréquence de survol : 7 jours) et la distribution automatisée des alertes brousse.")
    
    # Affichage de la base de données globale des champs
    st.subheader("🗂️ Registre Permanent des Parcelles Surveillées")
    df_champs = pd.DataFrame(st.session_state["base_champs_systeme"])
    st.dataframe(df_champs)
    
    st.markdown("---")
    st.subheader("🧠 Analyseur de Spectre Spatial & Déclenchement d'Alerte")
    
    # Sélectionner un champ pour simuler une détection d'anomalie
    liste_champs_id = [c["id"] for c in st.session_state["base_champs_systeme"]]
    target_champ_id = st.selectbox("Sélectionner une parcelle pour lancer l'audit de santé par satellite :", liste_champs_id)
    
    col_sat1, col_sat2 = st.columns(2)
    with col_sat1:
        st.markdown("**🔄 Simulation d'un nouveau survol Satellite (Fréquence : 7 jours)**")
        nv_ndvi = st.slider("Indice de Végétation NDVI mesuré (Une valeur faible indique un stress/maladie)", 0.0, 1.0, 0.45, step=0.05)
    
    with col_sat2:
        patho_choix = st.selectbox("Si anomalie, pathologie suspectée par SAPHIR Pharma :", ["Pourriture brune des cabosses", "Maladie du Swollen Shoot", "Attaque de Mirides / Capsides", "Aucune (Parfaite santé)"])

    if st.button("📡 Exécuter l'analyse spectrale SAPHIR Core"):
        # Trouver la parcelle dans notre base permanente
        for c in st.session_state["base_champs_systeme"]:
            if c["id"] == target_champ_id:
                c["indice_sante_ndvi"] = nv_ndvi
                c["dernier_passage_satellite"] = datetime.now().strftime("%Y-%m-%d")
                
                if nv_ndvi < 0.6 and patho_choix != "Aucune (Parfaite santé)":
                    c["alerte_active"] = True
                    c["pathologie_detectee"] = patho_choix
                    c["protocole_active"] = "⚠️ J+1 Engagé"
                    
                    # --- BOUCLE DE COMMUNICATION AUTOMATIQUE ---
                    # 1. Transfert de Saphir Core vers Saphir Pharma pour traitement
                    message_pharma = f"SAPHIR PHARMA : Pour contrer '{patho_choix}', appliquez le protocole d'urgence phytosanitaire sous 24h."
                    
                    # 2. Génération des SMS Offline à envoyer via la passerelle
                    sms_planteur = f"SAPHIR ALERT [Planteur {c['producteur']}] : Anomalie détectée par satellite sur votre champ {c['id']}. Diagnostic : {patho_choix}. Un Chef de Brigade intervient demain (Protocole J+1)."
                    sms_brigadier = f"SAPHIR DIRECTION [Chef de Brigade] : Alerte Critique sur la parcelle {c['id']} ({c['localite']}). Déclenchez le Protocole d'intervention Terrain J+1. Traitement requis : {message_pharma}"
                    
                    # Sauvegarde des logs SMS
                    st.session_state["sms_envoyes_log"].append({"Heure": datetime.now().strftime("%H:%M:%S"), "Destinataire": "Planteur", "Contenu": sms_planteur})
                    st.session_state["sms_envoyes_log"].append({"Heure": datetime.now().strftime("%H:%M:%S"), "Destinataire": "Chef de Brigade", "Contenu": sms_brigadier})
                    
                    st.error("🚨 ALERTE CRITIQUE GÉNÉRÉE PAR LE SATELLITE !")
                    st.markdown(f"**Flux Interne :** `SAPHIR Core` ➡️ `SAPHIR Pharma` ➡️ `Passerelle SMS GSM`")
                else:
                    c["alerte_active"] = False
                    c["pathologie_detectee"] = "Aucune"
                    c["protocole_active"] = "Aucun (R.A.S)"
                    st.success("✅ Analyse effectuée : La végétation est vigoureuse. Aucune anomalie détectée.")
        time.sleep(1)
        st.rerun()

    # --- JOURNAL DES SMS OFFLINE DÉPÊCHÉS ---
    if len(st.session_state["sms_envoyes_log"]) > 0:
        st.markdown("---")
        st.subheader("📟 Passerelle SMS (Flux GSM Brousse Offline Déclenché)")
        st.write("Les SMS ci-dessous ont été injectés dans la file d'attente de la passerelle matérielle pour envoi immédiat sur les téléphones des acteurs de terrain sans passer par Internet.")
        st.table(st.session_state["sms_envoyes_log"])

st.markdown("---")
st.caption("© 2026 GODGIE Group — Plateforme Rapprochée d'Harmonisation Phytosanitaire. Droits réservés OAPI/OHADA.")
