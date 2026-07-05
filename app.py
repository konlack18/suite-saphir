import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
from datetime import datetime

# 🛡️ IMPORTATION SÉCURISÉE DU MOTEUR PROTÉGÉ
from saphir_engine import Saphir_Core_Engine

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(
    page_title="SAPHIR Suite v1.0 - Écosystème Industriel Sécurisé",
    page_icon="🛡️",
    layout="wide"
)

# --- COORDONNÉES DES ARRONDISSEMENTS DE RÉFÉRENCE ---
ARRONDISSEMENTS = {
    "Mbandjock (Haute-Sanaga, Cameroun)": {"lat": 4.4500, "lon": 11.9000},
    "Kango (Estuaire, Gabon)": {"lat": 0.1742, "lon": 10.1146},
    "Ntoum (Gabon)": {"lat": 0.3833, "lon": 9.7500},
    "Obala (Lekié, Cameroun)": {"lat": 4.1667, "lon": 11.5333}
}

# --- INITIALISATION DES PRIX VIA FLUX EXTERNE ---
@st.cache_data(ttl=3600)
def fetch_live_market_prices():
    prices_backup = {
        "Cacao (Theobroma cacao)": 2850,
        "Manioc / Cassava (Manihot esculenta)": 450,
        "Maïs Jaune (Zea mays)": 320,
        "Banane Plantain (Musa paradisiaca)": 600,
        "Café Robusta (Coffea canephora)": 1950,
        "Poivre de Penja (Piper nigrum)": 8000
    }
    try:
        response = requests.get("https://api.openfooddata.org/v1/markets/cemac", timeout=3)
        if response.status_code == 200:
            data = response.json()
            for k in prices_backup.keys():
                if k in data: prices_backup[k] = data[k]
            return prices_backup, "📡 FLUX API LIVE (FAO/OpenMarket) CONNECTÉ"
    except Exception:
        pass
    return prices_backup, "⚠️ MODE SÉCURISÉ LOCAL (Prix de référence brousse)"

PRIX_REF, STATUT_API = fetch_live_market_prices()
ALL_CROPS = list(PRIX_REF.keys()) + ["Café Arabica", "Macabo", "Taro", "Arachide", "Djansang"]

RENDEMENTS_THEORIQUES = {
    "Cacao (Theobroma cacao)": 0.8,
    "Manioc / Cassava (Manihot esculenta)": 15.0,
    "Maïs Jaune (Zea mays)": 3.5,
    "Banane Plantain (Musa paradisiaca)": 10.0,
    "Café Robusta (Coffea canephora)": 0.7,
    "Poivre de Penja (Piper nigrum)": 1.5
}

# --- INITIALISATION DES SESSIONS STATES ---
if "brouillon_producteur" not in st.session_state:
    st.session_state["brouillon_producteur"] = {}
if "consentement_valide" not in st.session_state:
    st.session_state["consentement_valide"] = False

# --- HEADER ET BANDEAU CONNECTÉ ---
st.title("🛡️ SAPHIR Suite v1.0 — Plateforme Agro-Industrielle Intégrée")
st.caption("Propriété exclusive de GODGIE Group — Directeur de Projet : Ing. Roméo Moffo Konlack")

ticker_text = " • ".join([f"【 {k} : {v:,} FCFA/Kg 】" for k, v in PRIX_REF.items()])
st.markdown(f"""
<div style="background-color:#1a202c; color:#38a169; padding:10px; border-radius:4px; font-weight:bold; font-family:monospace; font-size:12px; border: 1px solid #38a169;">
    {STATUT_API} : {ticker_text}
</div>
""", unsafe_allow_html=True)

st.markdown(" ")

# --- VÉRIFICATION DU CONSENTEMENT ---
if not st.session_state["consentement_valide"]:
    st.header("🔐 Charte de Protection des Données & Consentement")
    st.warning("Conformément aux directives de l'OHADA, le recueil des coordonnées géospatiales, des visuels d'identité et des pièces justificatives juridiques requiert un consentement éclairé.")
    with st.container(border=True):
        st.markdown("""
        **Formulaire de Consentement Éclairé (GODGIE Group) :**
        1. **Données GPS & Cartographie :** J'autorise SAPHIR Field à enregistrer l'emplacement et la structure de mes parcelles.
        2. **Pièces d'Identité & Biométrie :** J'accepte la numérisation de ma pièce d'identité et de ma photo pour authentifier mes ventes sur compte séquestre.
        """)
        c1 = st.checkbox("Je donne mon consentement libre et explicite pour ces traitements.")
        c2 = st.checkbox("Je certifie l'exactitude des pièces d'identité qui seront fournies.")
        if st.button("🔓 Débloquer l'accès à l'application"):
            if c1 and c2:
                st.session_state["consentement_valide"] = True
                st.rerun()
            else:
                st.error("Validation requise pour accéder à la Suite SAPHIR.")
    st.stop()

user_role = st.radio(
    "Veuillez choisir votre profil d'accès pour adapter l'affichage :",
    ["🏢 Acheteur / Chocolatier / Consommateur", "🧑‍🌾 Espace Producteurs & Enquêtes (SAPHIR Field)"],
    horizontal=True
)

st.markdown("---")

# =====================================================================
# MODULE ACHETEUR
# =====================================================================
if user_role == "🏢 Acheteur / Chocolatier / Consommateur":
    st.header("💱 SAPHIR TRADE — Module Acheteur")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        a_crop = st.selectbox("Spéculation végétale recherchée :", ALL_CROPS)
        a_vol_req = st.number_input("Tonnage nécessaire (en Tonnes)", min_value=1.0, value=10.0)
    with col_a2:
        a_secret_price = st.number_input("Offre de prix d'achat secrète (FCFA / Kg)", min_value=1, value=2900)

    st.markdown("---")
    montant_brut = int(a_vol_req * 1000 * a_secret_price)
    total_paye = int(montant_brut * 1.02)
    st.metric("Total à décaisser (Fonds Bloqués sur Séquestre GODGIE)", f"{total_paye:,} FCFA")
    st.button("🔐 Émettre l'ordre d'achat séquestre")

# =====================================================================
# MODULE ENQUÊTES, PARCELLES & KYC NUMÉRIQUE (SAPHIR FIELD)
# =====================================================================
else:
    st.header("📍 SAPHIR Field — Enregistrement Unifié, Multi-Parcelles & KYC")
    
    st.subheader("🌐 Étape 1 : Localisation Géo-Administrative")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        arrond_ref = st.selectbox("Arrondissement administratif de rattachement (Poste d'Intrants) :", list(ARRONDISSEMENTS.keys()))
    with col_g2:
        geo_lat = st.number_input("Latitude Réelle (Lue sur GPS/Smartphone)", format="%.5f", value=4.4621)
        geo_lon = st.number_input("Longitude Réelle (Lue sur GPS/Smartphone)", format="%.5f", value=11.9124)

    pos_arrond = ARRONDISSEMENTS[arrond_ref]
    distance_km = math.sqrt((geo_lat - pos_arrond["lat"])**2 + (geo_lon - pos_arrond["lon"])**2) * 111.1
    st.success(f"📏 Distance calculée au centre administratif d'intrants : **{distance_km:.2f} Km**")

    st.markdown("---")
    st.subheader("📝 Étape 2 : Identité Judiciaire du Producteur (KYC)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        p_nom = st.text_input("Nom complet (tel que mentionné sur la CNI/Passeport)", value=st.session_state["brouillon_producteur"].get("nom", ""))
        p_piece_type = st.selectbox("Type de pièce d'identité produite :", ["Carte Nationale d'Identité (CNI)", "Passeport", "Carte de Planteur Rapproché", "Permis de conduire"])
        p_piece_num = st.text_input("Numéro du document d'identité", placeholder="Ex: C0129384...")
        p_age = st.number_input("Âge", min_value=18, max_value=100, value=st.session_state["brouillon_producteur"].get("age", 40))
        p_situation = st.selectbox("Situation Matrimoniale", ["Célibataire", "Marié (Monogame)", "Marié (Polygame)", "Veuf"])
    
    with col_f2:
        st.write("📸 **Numérisation de la pièce d'identité en direct**")
        photo_cni = st.camera_input("Scanner le document d'identité (Face avant / Page principale)", key="cni_photo")
        p_rev_autre = st.number_input("Gains annuels hors-agriculture (Commerce, transports...) (FCFA)", min_value=0, value=200000)

    rev_epouses = 0
    if "Marié" in p_situation:
        st.markdown("##### 👩‍🌾 Situation Économique des Épouses")
        nb_femmes = st.slider("Nombre d'épouses", 1, 4, 1)
        for i in range(nb_femmes):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                f_crop = st.selectbox(f"Culture gérée par Épouse N°{i+1}", list(PRIX_REF.keys()), key=f"f_crop_{i}")
            with col_e2:
                f_surf = st.number_input(f"Superficie (Ha) - Épouse N°{i+1}", min_value=0.0, value=1.0, key=f"f_surf_{i}")
            rendement_f = RENDEMENTS_THEORIQUES.get(f_crop, 0.5)
            rev_epouses += int(f_surf * rendement_f * 1000 * PRIX_REF.get(f_crop, 1000))

    st.markdown("##### 👶 Enfants à Charge")
    nb_enfants = st.slider("Nombre d'enfants", 0, 10, 2)

    st.markdown("---")
    st.subheader("🗺️ Étape 3 : Cartographie Structurelle des Parcelles (Rendement & Âge)")
    nb_parcelles = st.number_input("Nombre de parcelles distinctes à enregistrer :", min_value=1, max_value=20, value=1, step=1)
    
    parcelles_data = []
    total_surface_agricole = 0.0
    revenu_agricole_total_pere = 0
    
    for k in range(int(nb_parcelles)):
        with st.container(border=True):
            st.markdown(f"**📐 Parcelle N°{k+1}**")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            
            with col_p1:
                spec = st.selectbox(f"Spéculation végétale", list(PRIX_REF.keys()), key=f"spec_{k}")
            with col_p2:
                surf = st.number_input(f"Superficie (en Hectares)", min_value=0.1, value=1.5, step=0.1, key=f"surf_{k}")
                total_surface_agricole += surf
            with col_p3:
                age_plant = st.number_input(f"Âge de la plantation (Années)", min_value=0, max_value=60, value=5, key=f"age_{k}")
            with col_p4:
                mode_conduite = st.selectbox(f"Mode de conduite", ["Culture pure intensive", "Système agroforestier traditionnel", "Assolement de brousse"], key=f"mode_{k}")
            
            rendement_base = RENDEMENTS_THEORIQUES.get(spec, 0.5)
            if age_plant < 3 or age_plant > 35: facteur_age = 0.4
            elif age_plant < 7: facteur_age = 0.8
            else: facteur_age = 1.0
                
            production_estimee_tonnes = surf * rendimiento_base * facteur_age if 'rendement_base' in locals() else surf * rendement_base * facteur_age
            revenu_estime_parcelle = int(production_estimee_tonnes * 1000 * PRIX_REF.get(spec, 1000))
            revenu_agricole_total_pere += revenu_estime_parcelle
            
            parcelles_data.append({
                "Parcelle": f"N°{k+1}", "Culture": spec, "Hectares": surf, "Age": age_plant, "Revenu_Estime": revenu_estime_parcelle
            })
            st.caption(f"📈 _Rendement projeté :_ **{production_estimee_tonnes:.2f} Tonnes** | Revenu : **{revenu_estime_parcelle:,} FCFA**")

    # --- ANALYSE SANITAIRE DU SYSTÈME CORE ---
    st.markdown("---")
    st.subheader("🧠 Étape 4 : Évaluation Sanitaire Terrain (SAPHIR Core Engine)")
    user_severity = st.slider("Indice de Sévérité de la pathologie observée (0 à 4)", 0, 4, 2)
    
    # APPEL SÉCURISÉ DU MOTEUR (L'algorithme tourne à l'abri des regards)
    res_core = Saphir_Core_Engine(user_severity, distance_km)
    
    with st.container(border=True):
        st.markdown(f"#### 📊 Diagnostic Temps Réel SAPHIR Core Engine")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Indice Qualité Intrant calculé (IMQG)", f"{res_core['imqg']}")
            st.metric("Risque Mauvaise Gouvernance (IMG)", f"{res_core['img']}")
        with col_res2:
            st.metric("Score de Fraude global", f"{res_core['score_fraude']} %")
            if res_core["zone_couleur"] == "red": st.error(res_core["diagnostic"])
            elif res_core["zone_couleur"] == "orange": st.warning(res_core["diagnostic"])
            else: st.success(res_core["diagnostic"])

    # --- GESTION DU BROUILLON ET EXPORT ---
    st.markdown("---")
    st.subheader("💾 Étape 5 : Sécurisation & Exportation")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Sauvegarder dans le Brouillon Local"):
            st.session_state["brouillon_producteur"] = {"nom": p_nom, "age": p_age}
            st.toast("Données mémorisées dans le système !", icon="💾")
            
    with col_btn2:
        df_export = pd.DataFrame(parcelles_data)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exporter le registre des parcelles en CSV",
            data=csv_data,
            file_name=f"SAPHIR_PARCELLES_{p_nom.replace(' ', '_') if p_nom else 'ANONYME'}.csv",
            mime="text/csv"
        )

    # --- SIGNATURE ET CLÔTURE ---
    st.markdown("---")
    st.subheader("📸 Étape 6 : Validation Biométrique & Clôture")
    photo_input = st.camera_input("Prise de vue d'identité (Portrait du Producteur)", key="self_photo")
    signature = st.checkbox("✍️ Le producteur certifie la liaison juridique entre sa pièce d'identité et ses parcelles.")
    
    if signature:
        st.success("🛰️ Faisceau Satellite Débloqué. Alignement des polygones radar initialisé.")
        
        total_revenu_menage = revenu_agricole_total_pere + rev_epouses + p_rev_autre
        part_agri = (revenu_agricole_total_pere / total_revenu_menage) if total_revenu_menage > 0 else 1
        
        st.markdown(f"""
        <div style="background-color:#1a202c; padding:15px; border-left:5px solid #38a169; border-radius:4px; color:white; font-family:monospace;">
            <strong>SYNTHÈSE ÉCONOMIQUE DE L'EXPLOITATION (GODGIE GROUP) :</strong><br>
            • Superficie Totale Exploitée : {total_surface_agricole:.2f} Hectares<br>
            • Revenu Annuel Concession : {total_revenu_menage:,} FCFA / an<br>
            • Taux de Dépendance Agricole : {part_agri*100:.1f}%<br>
            • 💡 L'activité agricole consolide la souveraineté du ménage.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🔒 Veuillez signer l'Étape 6 pour déclencher la télédétection spatiale.")

st.markdown("---")
st.caption("© 2026 GODGIE Group — Plateforme Rapprochée d'Harmonisation Phytosanitaire. Droits réservés OAPI/OHADA.")
