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
                        if implication == "Travail à temps plein" and age_enfant < 16:
                            st.error("⚠️ Risque travail des enfants — non-conformité EUDR/OIT")

            st.markdown("---")
            st.subheader("🗺️ Étape 3 — Parcelles à cartographier")
            nb_parc = st.number_input("Nombre de parcelles :", min_value=1, max_value=20, value=1)
            parcelles_temp = []
            for k in range(int(nb_parc)):
                with st.expander(f"Parcelle N°{k+1}"):
                    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                    with col_p1:
                        rub_p = st.selectbox(f"Secteur N°{k+1}", list(RUBRIQUES_ACTIVITES.keys()), key=f"p_rub_{k}")
                    with col_p2:
                        spec_p = st.selectbox(f"Spéculation N°{k+1}", RUBRIQUES_ACTIVITES[rub_p], key=f"p_spec_{k}")
                    with col_p3:
                        surf_p = st.number_input(f"Superficie (ha) N°{k+1}", 0.1, 500.0, 1.0, key=f"p_surf_{k}")
                    with col_p4:
                        cond_p = st.selectbox(f"Conduite N°{k+1}", ["Intensif", "Traditionnel", "Agroforesterie"], key=f"p_cond_{k}")

                    id_parcelle = f"GODDIE-{sel_pays[:3].upper()}-{(p_nom or 'AUTO').replace(' ','-').upper()[:10]}-P{k+1:02d}"
                    parcelles_temp.append({
                        "id_unique": id_parcelle,
                        "nom_producteur": p_nom,
                        "tel_producteur": p_tel,
                        "pays": sel_pays,
                        "province": sel_prov,
                        "departement": sel_dept,
                        "arrondissement": sel_arr,
                        "localite": sel_localite,
                        "lat": geo_lat,
                        "lon": geo_lon,
                        "rubrique": rub_p,
                        "speculation": spec_p,
                        "superficie": surf_p,
                        "conduite": cond_p,
                        "statut_mapping": "❌ Non mappée",
                        "date_enregistrement": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "ndvi_dernier": None,
                        "date_dernier_scan": None,
                    })

            st.markdown("---")
            st.subheader("✍️ Étape 4 — Signature & Validation")
            sig = st.checkbox("Le producteur certifie l'exactitude des informations et consent au mapping satellitaire de ses parcelles.")
            if sig:
                if st.button("🚀 Valider et ouvrir le module de mapping", type="primary"):
                    st.session_state["parcelles_session"] = parcelles_temp
                    st.session_state["step_mapping_actif"] = True
                    st.rerun()
            else:
                st.info("🔒 Signature requise pour accéder au mapping terrain.")

        else:
            # ── MODULE MAPPING TERRAIN ──
            st.header("🛰️ Module de Mapping Polygonal — Arpentage Terrain")
            st.success("✅ Dossier signé. Procédez au mapping des parcelles une à une.")

            parcelles = st.session_state["parcelles_session"]
            non_mappees = [p for p in parcelles if p["statut_mapping"] == "❌ Non mappée"]
            mappees = [p for p in parcelles if p["statut_mapping"] != "❌ Non mappée"]

            with st.sidebar:
                st.markdown("### 📋 Parcelles")
                for p in parcelles:
                    st.markdown(f"**{p['id_unique']}** : {p['statut_mapping']}")
                if st.button("↩️ Retour au formulaire"):
                    st.session_state["step_mapping_actif"] = False
                    st.rerun()

            if non_mappees:
                sel_map = st.selectbox("Parcelle à arpenter :", [p["id_unique"] for p in non_mappees])
                parc_active = next(p for p in non_mappees if p["id_unique"] == sel_map)

                with st.container(border=True):
                    st.markdown(f"### 🚶 Arpentage — `{sel_map}`")
                    st.info(f"Culture : {parc_active['speculation']} | Superficie déclarée : {parc_active['superficie']} ha")
                    st.markdown("""
                    **Instructions terrain :**
                    1. Positionnez-vous à l'angle initial du champ
                    2. Cliquez "Borne 0" pour démarrer
                    3. Marchez le long du périmètre en cliquant à chaque pivot
                    4. Revenez au point de départ et cliquez "Clôturer"
                    """)

                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.button("🟢 Borne 0 — Démarrer")
                    with col_m2:
                        st.button("📍 Enregistrer un pivot")
                    with col_m3:
                        if st.button("🏁 Clôturer le polygone", type="primary"):
                            for p in parcelles:
                                if p["id_unique"] == sel_map:
                                    p["statut_mapping"] = "✅ Mappée"
                            st.toast(f"Parcelle {sel_map} cartographiée !", icon="🛰️")
                            st.rerun()

                    # Visualisation carte
                    lat_v = parc_active["lat"] + np.random.uniform(-0.002, 0.002, 8)
                    lon_v = parc_active["lon"] + np.random.uniform(-0.002, 0.002, 8)
                    st.map(pd.DataFrame({"lat": lat_v, "lon": lon_v}), zoom=13)

            else:
                st.balloons()
                st.success("🎉 Toutes les parcelles ont été cartographiées !")
                df_export = pd.DataFrame(parcelles)
                st.dataframe(df_export[["id_unique","nom_producteur","speculation","superficie","statut_mapping","lat","lon"]])

                # Enregistrer dans la base persistante
                if st.button("💾 Enregistrer dans la base SAPHIR", type="primary"):
                    for p in parcelles:
                        if not any(x["id_unique"] == p["id_unique"] for x in st.session_state["parcelles_db"]):
                            st.session_state["parcelles_db"].append(p)
                    st.success(f"✅ {len(parcelles)} parcelles enregistrées dans la base SAPHIR !")
                    st.session_state["step_mapping_actif"] = False
                    st.rerun()

                csv = df_export.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter CSV", csv, "SAPHIR_PARCELLES.csv", "text/csv")

    with tab_registre:
        st.subheader("📋 Registre Global des Parcelles")
        if st.session_state["parcelles_db"]:
            df_reg = pd.DataFrame(st.session_state["parcelles_db"])
            cols_show = ["id_unique","nom_producteur","pays","arrondissement","speculation","superficie","statut_mapping","date_enregistrement"]
            cols_show = [c for c in cols_show if c in df_reg.columns]
            st.dataframe(df_reg[cols_show], use_container_width=True)
            csv_reg = df_reg.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exporter le registre complet", csv_reg, "SAPHIR_REGISTRE.csv", "text/csv")
        else:
            st.info("Aucune parcelle enregistrée. Commencez par enregistrer un producteur.")

# ================================================================
# ONGLET 2 — SAPHIR CORE (Surveillance Satellite)
# ================================================================
elif onglet_principal == "🛰️ SAPHIR CORE — Surveillance Satellite":
    st.header("🛰️ SAPHIR CORE — Surveillance Sentinel-2 & Calcul de Risque")

    tab_scan, tab_historique = st.tabs(["🔍 Lancer une analyse", "📈 Historique des scans"])

    with tab_scan:
        if st.session_state["parcelles_db"]:
            ids = [p["id_unique"] for p in st.session_state["parcelles_db"]]
            sel_id = st.selectbox("Sélectionner une parcelle à analyser :", ids)
            parc = next(p for p in st.session_state["parcelles_db"] if p["id_unique"] == sel_id)

            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.info(f"**Producteur :** {parc.get('nom_producteur','N/A')}")
            with col_info2:
                st.info(f"**Culture :** {parc.get('speculation','N/A')}")
            with col_info3:
                st.info(f"**GPS :** {parc.get('lat',0):.4f}°N, {parc.get('lon',0):.4f}°E")

            st.markdown("---")
            if st.button("🛰️ Lancer l'analyse Sentinel-2 maintenant", type="primary"):
                with st.spinner("Connexion au serveur Sentinel-2 (ESA Copernicus)... Analyse NDVI en cours..."):
                    time.sleep(2)

                sat = simuler_analyse_sentinel2(
                    parc.get("lat", 4.46),
                    parc.get("lon", 11.91),
                    parc.get("speculation", "Cacao (Theobroma cacao)")
                )

                core = Saphir_Core_Engine(
                    lat_parcelle=parc.get("lat", 4.46),
                    lon_lat_cheflieu=(parc.get("lat", 4.46), parc.get("lon", 11.91)),
                    severity_ndvi=sat["severite"],
                    pays=parc.get("pays", "Cameroun")
                )

                # Affichage résultats
                st.markdown(f"""
                <div class="alert-{'rouge' if core['zone']=='ROUGE' else 'orange' if core['zone']=='ORANGE' else 'vert'}">
                    <h3>{core['emoji']} {core['diagnostic']}</h3>
                    <p><strong>Action requise :</strong> {core['action']}</p>
                </div>
                """, unsafe_allow_html=True)

                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                with col_r1:
                    st.metric("NDVI", sat["ndvi"], help="0=sol nu, 1=végétation dense")
                with col_r2:
                    st.metric("Score de risque", f"{core['score_global']}/100")
                with col_r3:
                    st.metric("IMQG", core["imqg"], help="Gradient qualité intrants")
                with col_r4:
                    st.metric("Distance chef-lieu", f"{core['distance_km']} km")

                with st.expander("📊 Détails de l'analyse satellite"):
                    st.write(f"**Source :** {sat['source']}")
                    st.write(f"**Date d'analyse :** {sat['date_analyse']}")
                    st.write(f"**Prochaine analyse :** {sat['prochaine_analyse']}")
                    st.write(f"**Bande NIR :** {sat['bande_NIR']} | **Bande RED :** {sat['bande_RED']}")
                    st.write(f"**Statut végétatif :** {sat['couleur']} {sat['statut_ndvi']}")

                # Sauvegarder l'alerte
                alerte = {
                    "id_parcelle": sel_id,
                    "nom_producteur": parc.get("nom_producteur"),
                    "speculation": parc.get("speculation"),
                    "date": sat["date_analyse"],
                    "ndvi": sat["ndvi"],
                    "zone": core["zone"],
                    "score": core["score_global"],
                    "diagnostic": core["diagnostic"],
                    "action": core["action"],
                    "img": core["img"],
                    "imqg": core["imqg"],
                }
                st.session_state["alertes_db"].append(alerte)

                # Mettre à jour la parcelle
                for p in st.session_state["parcelles_db"]:
                    if p["id_unique"] == sel_id:
                        p["ndvi_dernier"] = sat["ndvi"]
                        p["date_dernier_scan"] = sat["date_analyse"]

                if core["zone"] in ["ROUGE", "ORANGE"]:
                    st.warning("⚠️ Alerte détectée — Rendez-vous dans SAPHIR PHARMA pour envoyer les SMS d'alerte.")
        else:
            st.info("Aucune parcelle enregistrée. Commencez par enregistrer un producteur dans SAPHIR FIELD.")

    with tab_historique:
        st.subheader("📈 Historique des Analyses Satellite")
        if st.session_state["alertes_db"]:
            df_al = pd.DataFrame(st.session_state["alertes_db"])
            st.dataframe(df_al, use_container_width=True)
            rouges = len(df_al[df_al["zone"] == "ROUGE"])
            oranges = len(df_al[df_al["zone"] == "ORANGE"])
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("🔴 Alertes critiques", rouges)
            col_s2.metric("🟠 Alertes modérées", oranges)
            col_s3.metric("Total analyses", len(df_al))
        else:
            st.info("Aucune analyse réalisée pour l'instant.")

# ================================================================
# ONGLET 3 — SAPHIR PHARMA (SMS Alertes J+1)
# ================================================================
elif onglet_principal == "💊 SAPHIR PHARMA — Alertes":
    st.header("💊 SAPHIR PHARMA — Système d'Alertes & Protocole J+1")

    st.markdown("""
    **Comment ça fonctionne :**
    SAPHIR PHARMA reçoit automatiquement les alertes de SAPHIR CORE, génère les messages personnalisés
    et les envoie par SMS (via Africa's Talking) au planteur ET au chef de brigade.
    En zone sans internet, les SMS fonctionnent sur tout réseau GSM (MTN, Orange, Nexttel, Airtel).
    """)

    # Alertes actives
    alertes_actives = [a for a in st.session_state["alertes_db"] if a.get("zone") in ["ROUGE","ORANGE"]]

    if alertes_actives:
        st.subheader(f"🚨 {len(alertes_actives)} alerte(s) nécessitant une action")

        for alerte in alertes_actives:
            with st.expander(f"{alerte.get('zone','?')} — {alerte.get('id_parcelle','?')} | {alerte.get('date','?')}"):
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.markdown(f"**Producteur :** {alerte.get('nom_producteur','N/A')}")
                    st.markdown(f"**Culture :** {alerte.get('speculation','N/A')}")
                    st.markdown(f"**NDVI :** {alerte.get('ndvi','N/A')}")
                    st.markdown(f"**Score :** {alerte.get('score','N/A')}/100")
                with col_a2:
                    st.markdown(f"**Diagnostic :** {alerte.get('diagnostic','N/A')}")
                    st.markdown(f"**Action :** {alerte.get('action','N/A')}")

                # Saisie des numéros pour l'envoi
                parc_match = next((p for p in st.session_state["parcelles_db"]
                                   if p["id_unique"] == alerte.get("id_parcelle")), {})
                tel_p = st.text_input("Tel planteur :", value=parc_match.get("tel_producteur",""), key=f"tel_p_{alerte.get('id_parcelle')}")
                tel_b = st.text_input("Tel chef de brigade :", value="+237 600 000 000", key=f"tel_b_{alerte.get('id_parcelle')}")

                if st.button(f"📱 Envoyer SMS d'alerte J+1", key=f"sms_{alerte.get('id_parcelle')}"):
                    sms_data = generer_sms_alerte(parc_match, alerte, {"ndvi": alerte.get("ndvi"), "statut_ndvi": alerte.get("diagnostic")}, tel_p, tel_b)

                    st.success("✅ SMS envoyés via Africa's Talking (simulation)")

                    col_sms1, col_sms2 = st.columns(2)
                    with col_sms1:
                        st.markdown("**📱 SMS Planteur :**")
                        st.markdown(f"""<div class="sms-preview">{sms_data['sms_planteur'].replace(chr(10), '<br>')}</div>""", unsafe_allow_html=True)
                    with col_sms2:
                        st.markdown("**📱 SMS Chef de Brigade :**")
                        st.markdown(f"""<div class="sms-preview">{sms_data['sms_brigade'].replace(chr(10), '<br>')}</div>""", unsafe_allow_html=True)

                    st.caption(f"💰 Coût estimé : {sms_data['cout_estime']}")
                    st.session_state["sms_envoyes"].append(sms_data)
    else:
        st.success("✅ Aucune alerte active. Toutes les parcelles sont dans les normes.")
        st.info("Les alertes apparaissent automatiquement après une analyse SAPHIR CORE en zone ORANGE ou ROUGE.")

    # Historique SMS
    if st.session_state["sms_envoyes"]:
        st.markdown("---")
        st.subheader(f"📋 Historique — {len(st.session_state['sms_envoyes'])} SMS envoyé(s)")
        for sms in st.session_state["sms_envoyes"]:
            st.caption(f"🕐 {sms.get('timestamp')} | Zone : {sms.get('zone')} | {sms.get('cout_estime')}")

# ================================================================
# ONGLET 4 — SAPHIR TRADE (Marché Agricole)
# ================================================================
else:
    st.header("💱 SAPHIR TRADE — Bourse Agricole CEMAC")

    tab_acheteur, tab_vendeur, tab_marche = st.tabs([
        "🏢 Espace Acheteur",
        "🧑‍🌾 Espace Vendeur",
        "📊 Tableau du Marché"
    ])

    # ── ESPACE ACHETEUR ──
    with tab_acheteur:
        st.subheader("🏢 Déclarer vos Besoins d'Approvisionnement")
        st.info("Déclarez vos besoins annuels par campagne. Vos prix restent confidentiels jusqu'au matching.")

        with st.form("form_acheteur"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                a_entreprise = st.text_input("Nom de votre entreprise :")
                a_contact = st.text_input("Contact :")
                a_spec = st.selectbox("Spéculation recherchée :", RUBRIQUES_ACTIVITES["Production Végétale"])
                a_campagne = st.selectbox("Campagne cible :", ["2026-2027", "2027-2028", "2028-2029"])
            with col_a2:
                a_vol_total = st.number_input("Volume total annuel nécessaire (Tonnes) :", 0.0, 10000.0, 100.0)
                a_t1 = st.number_input("Besoin T1 (Tonnes) :", 0.0, a_vol_total, a_vol_total/4)
                a_t2 = st.number_input("Besoin T2 (Tonnes) :", 0.0, a_vol_total, a_vol_total/4)
                a_t3 = st.number_input("Besoin T3 (Tonnes) :", 0.0, a_vol_total, a_vol_total/4)
                a_t4 = st.number_input("Besoin T4 (Tonnes) :", 0.0, a_vol_total, a_vol_total/4)
                a_prix_secret = st.number_input("Prix maximum offert (FCFA/kg) — Confidentiel :", 0, 20000, PRIX_REF_CEMAC.get(a_spec, 2000))

            submitted_a = st.form_submit_button("🔐 Soumettre ma demande (prix sécurisé)")
            if submitted_a:
                demande = {
                    "type": "demande_acheteur",
                    "entreprise": a_entreprise,
                    "contact": a_contact,
                    "speculation": a_spec,
                    "campagne": a_campagne,
                    "vol_total": a_vol_total,
                    "repartition": {"T1": a_t1, "T2": a_t2, "T3": a_t3, "T4": a_t4},
                    "prix_max_confidentiel": a_prix_secret,
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "statut": "En attente de matching"
                }
                st.session_state["trade_demandes_acheteurs"].append(demande)
                st.success(f"✅ Demande enregistrée ! Volume : {a_vol_total}T de {a_spec} pour {a_campagne}")

    # ── ESPACE VENDEUR ──
    with tab_vendeur:
        st.subheader("🧑‍🌾 Gérer vos Stocks et Mises en Vente")

        subtab_prev, subtab_stock, subtab_vente = st.tabs([
            "📅 Déclarer une prévision",
            "📦 Déclarer la récolte réelle",
            "🏷️ Mettre en vente"
        ])

        with subtab_prev:
            st.markdown("**Avant la récolte — déclarez ce que vous pensez récolter cette campagne.**")
            with st.form("form_prevision"):
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    v_nom = st.text_input("Votre nom / coopérative :")
                    v_spec = st.selectbox("Culture :", RUBRIQUES_ACTIVITES["Production Végétale"])
                    v_campagne = st.selectbox("Campagne :", ["2026-2027", "2027-2028"])
                with col_v2:
                    v_prev = st.number_input("Volume prévu (Tonnes) :", 0.0, 1000.0, 5.0)
                    v_parc = st.text_input("ID Parcelle concernée :", placeholder="GODDIE-CAM-...")
                sub_prev = st.form_submit_button("📅 Enregistrer ma prévision")
                if sub_prev:
                    offre = {
                        "id": f"OFFRE-{len(st.session_state['trade_offres_vendeurs'])+1:04d}",
                        "vendeur": v_nom,
                        "speculation": v_spec,
                        "campagne": v_campagne,
                        "vol_prevision": v_prev,
                        "vol_recolte_reel": None,
                        "vol_en_stock": None,
                        "vol_en_vente": None,
                        "statut": "📅 Prévision déclarée",
                        "date_creation": datetime.now().strftime("%d/%m/%Y"),
                        "id_parcelle": v_parc
                    }
                    st.session_state["trade_offres_vendeurs"].append(offre)
                    st.success(f"✅ Prévision de {v_prev}T de {v_spec} enregistrée !")

        with subtab_stock:
            st.markdown("**Après la récolte — déclarez votre récolte réelle.**")
            mes_offres_prev = [o for o in st.session_state["trade_offres_vendeurs"] if o["statut"] == "📅 Prévision déclarée"]
            if mes_offres_prev:
                ids_prev = [o["id"] for o in mes_offres_prev]
                sel_off = st.selectbox("Sélectionner votre prévision :", ids_prev)
                offre_sel = next(o for o in mes_offres_prev if o["id"] == sel_off)
                st.info(f"Prévision : {offre_sel['vol_prevision']}T de {offre_sel['speculation']}")
                vol_reel = st.number_input("Volume réellement récolté (Tonnes) :", 0.0, 1000.0, offre_sel["vol_prevision"] * 0.9)
                if st.button("📦 Enregistrer la récolte réelle"):
                    for o in st.session_state["trade_offres_vendeurs"]:
                        if o["id"] == sel_off:
                            o["vol_recolte_reel"] = vol_reel
                            o["vol_en_stock"] = vol_reel
                            o["vol_en_vente"] = 0.0
                            o["statut"] = "📦 En stock"
                    st.success(f"✅ {vol_reel}T enregistrées en stock !")
                    st.rerun()
            else:
                st.info("Aucune prévision en attente. Commencez par déclarer une prévision.")

        with subtab_vente:
            st.markdown("**Mettez une partie de votre stock en vente sur le marché.**")
            mes_offres_stock = [o for o in st.session_state["trade_offres_vendeurs"] if o["statut"] == "📦 En stock" and o["vol_en_stock"] and o["vol_en_stock"] > 0]
            if mes_offres_stock:
                ids_stock = [f"{o['id']} — {o['speculation']} — Stock : {o['vol_en_stock']}T" for o in mes_offres_stock]
                sel_stock = st.selectbox("Sélectionner votre lot en stock :", ids_stock)
                idx_sel = ids_stock.index(sel_stock)
                offre_active = mes_offres_stock[idx_sel]

                col_st1, col_st2, col_st3 = st.columns(3)
                with col_st1:
                    st.metric("Stock total", f"{offre_active['vol_en_stock']}T")
                with col_st2:
                    st.metric("Déjà en vente", f"{offre_active.get('vol_en_vente',0)}T")
                with col_st3:
                    prix_ref = PRIX_REF_CEMAC.get(offre_active["speculation"], 1000)
                    st.metric("Prix référence CEMAC", f"{prix_ref:,} FCFA/kg")

                vol_vente = st.number_input(
                    f"Quantité à mettre en vente (max {offre_active['vol_en_stock']}T) :",
                    0.0, float(offre_active["vol_en_stock"]), min(5.0, float(offre_active["vol_en_stock"]))
                )

                # Simulation financière
                montant_brut = int(vol_vente * 1000 * prix_ref)
                commission = int(montant_brut * 0.02)
                net = montant_brut - commission

                col_f1, col_f2, col_f3 = st.columns(3)
                col_f1.metric("Valeur brute", f"{montant_brut:,} FCFA")
                col_f2.metric("Commission SAPHIR (2%)", f"-{commission:,} FCFA")
                col_f3.metric("Net estimé reçu", f"{net:,} FCFA")

                if st.button("🏷️ Mettre en vente sur le marché SAPHIR TRADE", type="primary"):
                    for o in st.session_state["trade_offres_vendeurs"]:
                        if o["id"] == offre_active["id"]:
                            o["vol_en_vente"] = (o.get("vol_en_vente") or 0) + vol_vente
                            o["vol_en_stock"] = o["vol_en_stock"] - vol_vente
                            o["statut"] = "🏷️ En vente partielle" if o["vol_en_stock"] > 0 else "🏷️ Tout en vente"
                    st.success(f"✅ {vol_vente}T de {offre_active['speculation']} mises en vente !")
                    st.rerun()
            else:
                st.info("Aucun stock disponible. Déclarez d'abord votre récolte réelle.")

    # ── TABLEAU DU MARCHÉ ──
    with tab_marche:
        st.subheader("📊 Tableau de Bord du Marché SAPHIR TRADE")
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("#### 🏷️ Offres Vendeurs disponibles")
            offres_marche = [o for o in st.session_state["trade_offres_vendeurs"] if "vente" in o.get("statut","").lower()]
            if offres_marche:
                for o in offres_marche:
                    with st.container(border=True):
                        prix = PRIX_REF_CEMAC.get(o["speculation"], 1000)
                        st.markdown(f"**{o['speculation']}** | Vendeur : {o['vendeur']}")
                        st.markdown(f"Volume en vente : **{o.get('vol_en_vente',0)}T** | Prix réf : {prix:,} FCFA/kg")
                        st.caption(f"ID : {o['id']} | Parcelle : {o.get('id_parcelle','N/A')}")
            else:
                st.info("Aucune offre disponible pour l'instant.")

        with col_m2:
            st.markdown("#### 🏢 Demandes Acheteurs")
            if st.session_state["trade_demandes_acheteurs"]:
                for d in st.session_state["trade_demandes_acheteurs"]:
                    with st.container(border=True):
                        st.markdown(f"**{d['speculation']}** | {d['entreprise']}")
                        st.markdown(f"Besoin : **{d['vol_total']}T** | Campagne : {d['campagne']}")
                        st.caption(f"Répartition : T1={d['repartition']['T1']}T T2={d['repartition']['T2']}T T3={d['repartition']['T3']}T T4={d['repartition']['T4']}T")
            else:
                st.info("Aucune demande acheteur pour l'instant.")

# ── FOOTER ──
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#888;font-size:12px;">
🛡️ SAPHIR Suite v3.0 — Propriété exclusive de GODDIE Group<br>
Ing. Roméo Moffo Konlack | konlack18@yahoo.com | +241 065 894 852<br>
Protégé par les conventions OAPI et OHADA — Tous droits réservés 2026
</div>
""", unsafe_allow_html=True)
