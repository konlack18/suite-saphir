# ================================================================
# SAPHIR Suite v3.0 — Plateforme Agro-Industrielle Intégrée
# Propriété exclusive de GODDIE Group
# Directeur : Ing. Roméo Moffo Konlack
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import math
import json
import time
from datetime import datetime, timedelta

# ── CONFIGURATION ──
st.set_page_config(
    page_title="SAPHIR Suite v3.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS GLOBAL ──
st.markdown("""
<style>
.saphir-header {background:linear-gradient(135deg,#1F3864,#1E6B3C);color:white;padding:20px;border-radius:8px;margin-bottom:16px;}
.alert-rouge {background:#FAE8E8;border-left:5px solid #8B1A1A;padding:12px;border-radius:4px;}
.alert-orange {background:#FFF3E0;border-left:5px solid #E07B00;padding:12px;border-radius:4px;}
.alert-vert {background:#D6EFE1;border-left:5px solid #1E6B3C;padding:12px;border-radius:4px;}
.metric-card {background:#F5F7FA;border-radius:8px;padding:16px;border-top:4px solid #1F3864;}
.sms-preview {background:#1a1a2e;color:#00ff88;font-family:monospace;padding:12px;border-radius:6px;font-size:12px;}
</style>
""", unsafe_allow_html=True)

# ================================================================
# MODULE A — PERSISTANCE DES DONNÉES (session_state + export CSV)
# ================================================================

def init_session_state():
    defaults = {
        "consentement_valide": False,
        "parcelles_db": [],          # Base de données des parcelles mappées
        "alertes_db": [],            # Historique des alertes SAPHIR PHARMA
        "trade_offres_vendeurs": [], # Offres des vendeurs
        "trade_demandes_acheteurs": [], # Demandes des acheteurs
        "step_mapping_actif": False,
        "parcelles_session": [],
        "sms_envoyes": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ================================================================
# SAPHIR CORE ENGINE — MOTEUR ALGORITHMIQUE (version protégée)
# Les formules exactes IMG/IMQG sont encapsulées
# ================================================================

def calcul_distance_km(lat1, lon1, lat2, lon2):
    """Formule de Haversine — distance réelle en km"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def Saphir_Core_Engine(lat_parcelle, lon_lat_cheflieu, severity_ndvi, pays="Cameroun"):
    """
    Moteur de calcul SAPHIR CORE.
    Calcule IMQG et IMG, puis le score de risque global.
    Formules exactes protégées par dépôt OAPI — GODDIE Group 2026.
    """
    # Points de référence par pays (chef-lieu/port d'entrée)
    refs = {
        "Cameroun": (4.6927, 12.6743),  # Nanga-Eboko
        "Gabon": (-0.3989, 9.4673),      # Libreville
        "Congo-Brazzaville": (-4.2661, 15.2832),
        "Centrafrique": (4.3612, 18.5550),
        "Tchad": (12.1048, 15.0445),
        "Guinée Équatoriale": (3.7523, 8.7829),
    }
    ref = refs.get(pays, (4.6927, 12.6743))
    distance_km = calcul_distance_km(lat_parcelle, lon_lat_cheflieu[0], ref[0], ref[1])

    # IMQG — gradient spatial (formule protégée OAPI)
    imqg = min(0.21 + 0.0047 * distance_km, 1.0)

    # IMG — simulé selon les données disponibles (formule complète protégée OAPI)
    img = min(0.30 * 0.6 + 0.40 * (severity_ndvi / 4.0) + 0.30 * 0.5, 1.0)

    # Score de fraude global F_fraude
    f_fraude = ((1.0 - imqg) * 0.6) + (img * 0.4)

    # Score NDVI-risque combiné
    score_global = min(f_fraude * 100 * (1 + severity_ndvi * 0.2), 100.0)

    # Classification
    if score_global >= 65 or severity_ndvi >= 3:
        zone = "ROUGE"
        diagnostic = "ALERTE CRITIQUE — Anomalie majeure détectée"
        action = "PROTOCOLE J+1 ACTIVÉ — Intervention brigade sous 24h"
        emoji = "🔴"
    elif score_global >= 40 or severity_ndvi == 2:
        zone = "ORANGE"
        diagnostic = "ALERTE BIOLOGIQUE — Surveillance renforcée requise"
        action = "PROT-J1-BETA — Prélèvement conservatoire"
        emoji = "🟠"
    elif score_global >= 20:
        zone = "JAUNE"
        diagnostic = "VIGILANCE — Paramètres à surveiller"
        action = "PROT-ROUTINE-SAPHIR — Inspection dans les 7 jours"
        emoji = "🟡"
    else:
        zone = "VERT"
        diagnostic = "STABLE — Écosystème conforme"
        action = "PROT-ROUTINE-SAPHIR — Surveillance standard"
        emoji = "🟢"

    return {
        "imqg": round(imqg, 3),
        "img": round(img, 3),
        "f_fraude": round(f_fraude, 3),
        "score_global": round(score_global, 1),
        "distance_km": round(distance_km, 1),
        "zone": zone,
        "diagnostic": diagnostic,
        "action": action,
        "emoji": emoji
    }

# ================================================================
# MODULE B — SURVEILLANCE SATELLITE SENTINEL-2 (NDVI)
# ================================================================

def simuler_analyse_sentinel2(lat, lon, culture, date_derniere_analyse=None):
    """
    Simule l'analyse NDVI Sentinel-2.
    En production : remplacer par l'API Copernicus Open Access Hub.
    URL API réelle : https://scihub.copernicus.eu/dhus/
    Paramètre clé : NDVI = (NIR - RED) / (NIR + RED)
    """
    np.random.seed(int(abs(lat * lon * 100)) % 1000)

    # NDVI simulé selon la culture (valeurs réalistes)
    ndvi_base = {
        "Cacao (Theobroma cacao)": 0.72,
        "Manioc / Cassava": 0.65,
        "Maïs Jaune": 0.58,
        "Banane Plantain": 0.70,
        "Café Robusta": 0.68,
        "Palmier à huile": 0.75,
    }
    base = ndvi_base.get(culture, 0.60)
    ndvi = round(base + np.random.uniform(-0.15, 0.10), 3)
    ndvi = max(0.1, min(0.9, ndvi))

    # Déterminer la sévérité selon NDVI
    if ndvi >= 0.6:
        severite = 0
        statut_ndvi = "Végétation saine"
        couleur = "🟢"
    elif ndvi >= 0.4:
        severite = 1
        statut_ndvi = "Légère dégradation"
        couleur = "🟡"
    elif ndvi >= 0.25:
        severite = 2
        statut_ndvi = "Stress végétatif détecté"
        couleur = "🟠"
    else:
        severite = 3
        statut_ndvi = "Anomalie grave — Infestation probable"
        couleur = "🔴"

    prochaine_analyse = datetime.now() + timedelta(days=5)

    return {
        "ndvi": ndvi,
        "severite": severite,
        "statut_ndvi": statut_ndvi,
        "couleur": couleur,
        "date_analyse": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "prochaine_analyse": prochaine_analyse.strftime("%d/%m/%Y"),
        "source": "Sentinel-2 (ESA Copernicus) — Résolution 10m",
        "bande_NIR": round(np.random.uniform(0.3, 0.6), 3),
        "bande_RED": round(np.random.uniform(0.05, 0.2), 3),
    }

# ================================================================
# MODULE C — SAPHIR PHARMA (Alertes SMS via Africa's Talking)
# ================================================================

def generer_sms_alerte(parcelle, resultat_core, resultat_satellite, tel_planteur, tel_brigade):
    """
    Génère les SMS d'alerte SAPHIR PHARMA.
    En production : remplacer par l'API Africa's Talking.
    API : https://africastalking.com/sms
    Coût : ~4-5 FCFA par SMS, compatible MTN/Orange/Nexttel/Airtel
    """
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    sms_planteur = f"""SAPHIR PHARMA - ALERTE {resultat_core['zone']}
Parcelle: {parcelle.get('id_unique','N/A')}
Culture: {parcelle.get('speculation','N/A')}
Date: {timestamp}
NDVI: {resultat_satellite['ndvi']} — {resultat_satellite['statut_ndvi']}
Score risque: {resultat_core['score_global']}/100
ACTION: {resultat_core['action']}
Contacter votre brigade: {tel_brigade}
GODDIE-SAPHIR"""

    sms_brigade = f"""SAPHIR J+1 - ALERTE CHEF BRIGADE
Producteur: {parcelle.get('nom_producteur','N/A')}
Parcelle: {parcelle.get('id_unique','N/A')}
GPS: {parcelle.get('lat',0)},{parcelle.get('lon',0)}
Culture: {parcelle.get('speculation','N/A')}
NDVI: {resultat_satellite['ndvi']} ({resultat_satellite['statut_ndvi']})
IMG: {resultat_core['img']} | IMQG: {resultat_core['imqg']}
SCORE: {resultat_core['score_global']}/100
ZONE: {resultat_core['zone']}
PROTOCOLE: {resultat_core['action']}
Contact planteur: {tel_planteur}
GODDIE-SAPHIR"""

    return {
        "sms_planteur": sms_planteur,
        "sms_brigade": sms_brigade,
        "tel_planteur": tel_planteur,
        "tel_brigade": tel_brigade,
        "timestamp": timestamp,
        "zone": resultat_core['zone'],
        "cout_estime": "8-10 FCFA (2 SMS)",
        "statut": "ENVOYÉ (simulation)" if resultat_core['zone'] in ["ROUGE","ORANGE"] else "Non requis"
    }

# ================================================================
# DONNÉES DE RÉFÉRENCE
# ================================================================

CEMAC_DATA = {
    "Cameroun": {
        "type": "Région",
        "divisions": {
            "Centre": {
                "Haute-Sanaga": ["Mbandjock", "Minta", "Nanga-Eboko", "Bibey", "Lembe-Yezoum"],
                "Lekié": ["Obala", "Monatélé", "Sa'a"],
                "Mbam-et-Kim": ["Mbangassina", "Ntui", "Mbam-Kim Centre"]
            },
            "Littoral": {
                "Wouri": ["Douala 1er", "Douala 2e", "Douala 3e"],
                "Moungo": ["Nkongsamba", "Njombé-Penja", "Mbanga"]
            },
            "Sud": {
                "Mvila": ["Ebolowa", "Biwong-Bane"],
                "Océan": ["Kribi", "Campo"]
            },
            "Sud-Ouest": {
                "Kupe-Manenguba": ["Bangem", "Nguti"],
                "Ndian": ["Mundemba", "Ekondo-Titi"]
            }
        }
    },
    "Gabon": {
        "type": "Province",
        "divisions": {
            "Estuaire": {
                "Kango": ["Kango Centre", "Menei", "Ebel-Abanga"],
                "Ntoum": ["Ntoum Centre", "Bikélé"]
            },
            "Woleu-Ntem": {
                "Oyem": ["Oyem Ville", "Mitzic", "Bitam"]
            }
        }
    },
    "Congo-Brazzaville": {"type": "Département", "divisions": {"Bouenza": {"Madingou": ["Madingou Ville"]}}},
    "Centrafrique": {"type": "Préfecture", "divisions": {"Ombella-M'Poko": {"Bimbo": ["Bimbo 1"]}}},
    "Tchad": {"type": "Province", "divisions": {"Chari-Baguirmi": {"Massenya": ["Massenya Ville"]}}},
    "Guinée Équatoriale": {"type": "Province", "divisions": {"Bioko-Norte": {"Malabo": ["Malabo Urban"]}}}
}

RUBRIQUES_ACTIVITES = {
    "Production Végétale": [
        "Cacao (Theobroma cacao)", "Café Robusta", "Café Arabica",
        "Manioc / Cassava", "Maïs Jaune", "Banane Plantain",
        "Poivre de Penja", "Palmier à huile", "Hévéa",
        "Arachide", "Macabo", "Taro", "Igname"
    ],
    "Production Animale": [
        "Élevage Porcin", "Aviculture (Poulets de chair)",
        "Aviculture (Pondeuses)", "Élevage Bovin", "Pisciculture"
    ],
    "Commerce Agricole": [
        "Vente de produits vivriers", "Boutique d'intrants",
        "Collecte et revente cacao/café"
    ],
    "Transformation": [
        "Transformation du manioc (Gari/Miondo)",
        "Trituration huile de palme artisanale"
    ]
}

PRIX_REF_CEMAC = {
    "Cacao (Theobroma cacao)": 2850,
    "Café Robusta": 1950,
    "Manioc / Cassava": 450,
    "Maïs Jaune": 320,
    "Banane Plantain": 600,
    "Poivre de Penja": 8000,
    "Palmier à huile": 280,
    "Hévéa": 1200,
}

RENDEMENTS_THEORIQUES = {
    "Cacao (Theobroma cacao)": 0.8,
    "Manioc / Cassava": 15.0,
    "Maïs Jaune": 3.5,
    "Banane Plantain": 10.0,
    "Café Robusta": 0.7,
    "Poivre de Penja": 1.5,
    "Palmier à huile": 12.0,
}

# ================================================================
# INTERFACE PRINCIPALE
# ================================================================

st.markdown("""
<div class="saphir-header">
    <h1>🛡️ SAPHIR Suite v3.0</h1>
    <p>Plateforme Agro-Industrielle Intégrée — Zone CEMAC</p>
    <small>Propriété exclusive de GODDIE Group | Ing. Roméo Moffo Konlack | konlack18@yahoo.com</small>
</div>
""", unsafe_allow_html=True)

# ── BANDEAU PRIX ──
prix_ticker = " 〡 ".join([f"{k}: {v:,} FCFA/kg" for k, v in PRIX_REF_CEMAC.items()])
st.markdown(f"""
<div style="background:#1E6B3C;color:white;padding:8px 16px;border-radius:4px;font-size:12px;white-space:nowrap;overflow:hidden;">
    📊 Prix de référence CEMAC (Source : GODDIE Market Intelligence) — {prix_ticker}
</div>
""", unsafe_allow_html=True)

st.markdown(" ")

# ── CONSENTEMENT OBLIGATOIRE ──
if not st.session_state["consentement_valide"]:
    st.header("🔐 Charte de Protection des Données Personnelles")
    st.warning("Conformément aux lois de protection des données en vigueur au Cameroun, au Gabon et dans la zone CEMAC (OHADA), votre consentement explicite est requis avant tout enregistrement.")

    with st.container(border=True):
        st.markdown("""
        **Ce que SAPHIR collecte et pourquoi :**
        - **Coordonnées GPS** : pour cartographier vos parcelles et surveiller leur état via satellite
        - **Photo d'identité** : pour l'identification sécurisée lors des transactions SAPHIR TRADE
        - **Données agricoles** : pour calculer votre score de risque et vous alerter en cas de problème
        - **Numéro de téléphone** : pour vous envoyer des alertes SMS SAPHIR PHARMA

        **Vos droits** : accès, rectification, opposition et suppression de vos données sur simple demande à konlack18@yahoo.com
        """)
        c1 = st.checkbox("✅ J'autorise SAPHIR à collecter mes données GPS, photo et agricoles aux fins décrites ci-dessus.")
        c2 = st.checkbox("✅ J'ai lu et accepté la Charte de Protection des Données GODDIE Group.")
        c3 = st.checkbox("✅ Je certifie avoir au moins 18 ans et être habilité à représenter mon exploitation.")

        if st.button("🔓 Accéder à SAPHIR Suite", type="primary"):
            if c1 and c2 and c3:
                st.session_state["consentement_valide"] = True
                st.rerun()
            else:
                st.error("Veuillez cocher toutes les cases pour accéder à l'application.")
    st.stop()

# ── NAVIGATION PRINCIPALE ──
onglet_principal = st.sidebar.radio(
    "🧭 Navigation SAPHIR",
    [
        "📍 SAPHIR FIELD — Mapping & KYC",
        "🛰️ SAPHIR CORE — Surveillance Satellite",
        "💊 SAPHIR PHARMA — Alertes",
        "💱 SAPHIR TRADE — Marché",
    ]
)

# Indicateurs sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Tableau de Bord")
nb_parcelles = len(st.session_state["parcelles_db"])
nb_alertes = len([a for a in st.session_state["alertes_db"] if a.get("zone") in ["ROUGE","ORANGE"]])
nb_offres = len(st.session_state["trade_offres_vendeurs"])

st.sidebar.metric("Parcelles enregistrées", nb_parcelles)
st.sidebar.metric("Alertes actives", nb_alertes, delta=None)
st.sidebar.metric("Offres sur le marché", nb_offres)
st.sidebar.markdown("---")
st.sidebar.caption(f"Dernière synchronisation : {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ================================================================
# ONGLET 1 — SAPHIR FIELD
# ================================================================
if onglet_principal == "📍 SAPHIR FIELD — Mapping & KYC":
    st.header("📍 SAPHIR FIELD — Enregistrement & Cartographie")

    tab_nouveau, tab_registre = st.tabs(["➕ Nouveau Producteur", "📋 Registre des Parcelles"])

    with tab_nouveau:
        if not st.session_state["step_mapping_actif"]:

            st.subheader("🌐 Étape 1 — Localisation Géo-Administrative")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                sel_pays = st.selectbox("Pays :", list(CEMAC_DATA.keys()))
            with col_g2:
                list_prov = list(CEMAC_DATA[sel_pays]["divisions"].keys())
                sel_prov = st.selectbox(f"{CEMAC_DATA[sel_pays]['type']} :", list_prov)
            with col_g3:
                list_dept = list(CEMAC_DATA[sel_pays]["divisions"][sel_prov].keys())
                sel_dept = st.selectbox("Département :", list_dept)

            col_g4, col_g5, col_g6 = st.columns(3)
            with col_g4:
                list_arr = CEMAC_DATA[sel_pays]["divisions"][sel_prov][sel_dept]
                sel_arr = st.selectbox("Arrondissement :", list_arr)
            with col_g5:
                sel_localite = st.text_input("Localité / Village :", placeholder="Ex: Meba, Ntui Centre...")
            with col_g6:
                geo_lat = st.number_input("Latitude GPS (°N)", format="%.5f", value=4.46210)
                geo_lon = st.number_input("Longitude GPS (°E)", format="%.5f", value=11.91240)

            st.markdown("---")
            st.subheader("📝 Étape 2 — Identité du Producteur (KYC)")
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                p_nom = st.text_input("Nom complet (selon pièce d'identité) :")
                p_age = st.number_input("Âge :", min_value=18, max_value=100, value=40)
                p_tel = st.text_input("Téléphone principal :", placeholder="+237 6XX XXX XXX")
                p_piece_type = st.selectbox("Type de pièce :", ["Carte Nationale d'Identité", "Passeport", "Carte de Planteur"])
                p_piece_num = st.text_input("Numéro de pièce :")
                p_situation = st.selectbox("Situation matrimoniale :", ["Célibataire", "Marié(e) Monogame", "Marié(e) Polygame", "Veuf/Veuve"])
            with col_k2:
                st.write("📸 Photo du producteur (obligatoire)")
                photo_chef = st.camera_input("Portrait du producteur", key="photo_chef")
                st.write("🪪 Pièce d'identité")
                photo_recto = st.camera_input("Recto CNI/Passeport", key="cni_r")
                photo_verso = st.camera_input("Verso CNI/Passeport", key="cni_v")

            if "Polygame" in p_situation or "Monogame" in p_situation:
                st.markdown("---")
                st.subheader("👩‍🌾 Étape 2.1 — Épouses")
                nb_f = st.slider("Nombre d'épouses :", 1, 4, 1)
                for i in range(nb_f):
                    with st.expander(f"Épouse N°{i+1}"):
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            st.text_input(f"Nom épouse N°{i+1}", key=f"f_nom_{i}")
                            st.number_input(f"Âge épouse N°{i+1}", 18, 100, 30, key=f"f_age_{i}")
                        with col_f2:
                            rub_f = st.selectbox(f"Activité épouse N°{i+1}", list(RUBRIQUES_ACTIVITES.keys()), key=f"f_rub_{i}")
                            st.selectbox(f"Spéculation N°{i+1}", RUBRIQUES_ACTIVITES[rub_f], key=f"f_spec_{i}")

            st.markdown("---")
            st.subheader("👶 Étape 2.2 — Enfants à charge")
            nb_enf = st.slider("Nombre d'enfants :", 0, 15, 0)
            for j in range(nb_enf):
                with st.expander(f"Enfant N°{j+1}"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    with col_e1:
                        st.text_input(f"Nom enfant N°{j+1}", key=f"e_nom_{j}")
                        annee = st.number_input(f"Année naissance N°{j+1}", 1990, 2026, 2015, key=f"e_an_{j}")
                        st.caption(f"Âge calculé : {2026 - annee} ans")
                    with col_e2:
                        st.radio(f"Scolarisé(e) ?", ["Oui", "Non"], key=f"e_scol_{j}", horizontal=True)
                    with col_e3:
                        implication = st.selectbox(f"Implication plantation N°{j+1}",
                            ["Aucune / Uniquement vacances", "Aide après école", "Travail à temps plein"],
                            key=f"e_trav_{j}")
                        age_enfant = 2026 - annee
                        if implic