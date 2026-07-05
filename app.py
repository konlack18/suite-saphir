import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
from datetime import datetime

# 🛡️ CHARGEMENT DYNAMIQUE INTERNE — PROTÉGÉ PAR LES SECRETS STREAMLIT
import sys
import types

if "SAPHIR_ENGINE_CODE" in st.secrets:
    saphir_engine = types.ModuleType("saphir_engine")
    exec(st.secrets["SAPHIR_ENGINE_CODE"], saphir_engine.__dict__)
    sys.modules["saphir_engine"] = saphir_engine
    Saphir_Core_Engine = saphir_engine.Saphir_Core_Engine
else:
    st.error("🔒 Clé de chiffrement SAPHIR manquante dans l'infrastructure de production.")
    st.stop()

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(
    page_title="SAPHIR Suite v1.5 - Écosystème Industriel CEMAC",
    page_icon="🛡️",
    layout="wide"
)

# --- BASE DE DONNÉES GÉO-ADMINISTRATIVE CEMAC ---
GEO_CEMAC = {
    "Cameroun": {
        "Régions/Provinces": {
            "Centre": {
                "Départements": {
                    "Haute-Sanaga": ["Mbandjock", "Minta", "Nanga-Eboko", "Bibey", "Lembe-Yezoum"],
                    "Lekié": ["Obala", "Monatélé", "Evodoula", "Sa'a"],
                    "Mfoundi": ["Yaoundé I", "Yaoundé II", "Yaoundé III", "Yaoundé IV"]
                }
            },
            "Littoral": {
                "Départements": {
                    "Wouri": ["Douala I", "Douala II", "Douala III"],
                    "Moungo": ["Nkongsamba", "Njombé-Penja", "Mbanga"]
                }
            }
        }
    },
    "Gabon": {
        "Régions/Provinces": {
            "Estuaire": {
                "Départements": {
                    "Komo-Kango": ["Kango", "Chinchoua"],
                    "Komo-Mondah": ["Ntoum", "Kango", "Libreville"]
                }
            },
            "Woleu-Ntem": {
                "Départements": {
                    "Woleu": ["Oyem", "Mitzic"]
                }
            }
        }
    }
}

# --- LISTE DES SPÉCULATIONS COMPLETES ---
VEGETAUX = ["Cacao (Theobroma cacao)", "Manioc / Cassava", "Maïs Jaune", "Banane Plantain", "Café Robusta", "Café Arabica", "Poivre de Penja", "Macabo", "Taro", "Arachide", "Djansang", "Fruitier (Avocat/Mangue)"]
ANIMAUX = ["Poulets de chair", "Pondeuses", "Porcs", "Ovins/Caprins", "Bovins", "Pisciculture (Silures/Tilapias)"]

RENDEMENTS_THEORIQUES = {v: 1.0 for v in VEGETAUX}
RENDEMENTS_THEORIQUES["Cacao (Theobroma cacao)"] = 0.8
RENDEMENTS_THEORIQUES["Manioc / Cassava"] = 15.0
RENDEMENTS_THEORIQUES["Maïs Jaune"] = 3.5

PRIX_REF = {v: 500 for v in VEGETAUX}
PRIX_REF["Cacao (Theobroma cacao)"] = 2850
PRIX_REF["Manioc / Cassava"] = 450
PRIX_REF["Poivre de Penja"] = 8000

# --- INITIALISATION DES SESSIONS STATES ---
if "brouillon_producteur" not in st.session_state:
    st.session_state["brouillon_producteur"] = {}
if "consentement_valide" not in st.session_state:
    st.session_state["consentement_valide"] = False
if "offres_marche" not in st.session_state:
    st.session_state["offres_marche"] = []

# --- HEADER ---
st.title("🛡️ SAPHIR Suite v1.5 — Télédétection & Traçabilité CEMAC")
st.caption("Système Inter-États de Suivi Phytosanitaire & Souveraineté Alimentaire — Directeur de Projet : Ing. Roméo Moffo Konlack")

st.markdown(" ")

# --- VÉRIFICATION DU CONSENTEMENT ---
if not st.session_state["consentement_valide"]:
    st.header("🔐 Charte de Protection des Données & Consentement")
    st.warning("Conformément aux directives de l'OHADA, le recueil des données géospatiales, des visuels d'identité et des structures de ménages requiert un consentement éclairé.")
    with st.container(border=True):
        st.markdown("""
        **Formulaire de Consentement Éclairé (SAPHIR Ecosystem) :**
        1. **Données GPS & Cartographie :** J'autorise SAPHIR Field à enregistrer l'emplacement et la structure de mes parcelles.
        2. **Pièces d'Identité & Biométrie :** J'accepte la numérisation Recto/Verso de ma pièce d'identité pour authentifier mes transactions financières sécurisées.
        """)
        c1 = st.checkbox("Je donne mon consentement libre et explicite pour ces traitements régionaux.")
        c2 = st.checkbox("Je certifie l'exactitude des pièces d'identité et des structures de charges fournies.")
        if st.button("🔓 Débloquer l'accès à la Plateforme"):
            if c1 and c2:
                st.session_state["consentement_valide"] = True
                st.rerun()
            else:
                st.error("Validation requise pour accéder à la Suite SAPHIR.")
    st.stop()

user_role = st.sidebar.radio(
    "🧭 NAVIGATION MODULES :",
    ["🧑‍🌾 Enregistrement Producteurs & KYC (SAPHIR Field)", "💱 Bourse d'Échange Bi-latérale (SAPHIR TRADE)"]
)

st.markdown("---")

# =====================================================================
# MODULE ENQUÊTES, PARCELLES & KYC NUMÉRIQUE (SAPHIR FIELD)
# =====================================================================
if user_role == "🧑‍🌾 Enregistrement Producteurs & KYC (SAPHIR Field)":
    st.header("📍 SAPHIR Field — Enregistrement Unifié, Multi-Parcelles & KYC")
    
    # ÉTAPE 1 : ARBORESCENCE GÉO-ADMINISTRATIVE DYNAMIQUE
    st.subheader("🌐 Étape 1 : Localisation Géo-Administrative CEMAC")
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        pays_choisi = st.selectbox("1. Sélectionner le Pays :", list(GEO_CEMAC.keys()))
    
    provinces_dispo = list(GEO_CEMAC[pays_choisi]["Régions/Provinces"].keys())
    with col_g2:
        prov_choisie = st.selectbox("2. Sélectionner la Province / Région :", provinces_dispo)
        
    deps_dispo = list(GEO_CEMAC[pays_choisi]["Régions/Provinces"][prov_choisie]["Départements"].keys())
    with col_g3:
        dep_choisi = st.selectbox("3. Sélectionner le Département :", deps_dispo)
        
    col_g4, col_g5 = st.columns(2)
    arronds_dispo = GEO_CEMAC[pays_choisi]["Régions/Provinces"][prov_choisie]["Départements"][dep_choisi]
    with col_g4:
        arrond_choisi = st.selectbox("4. Sélectionner l'Arrondissement :", arronds_dispo)
    with col_g5:
        localite_saisie = st.text_input("5. Saisir la Localité / Village (Saisie Manuelle) :", placeholder="Ex: Meba, Village Angono...")

    st.info(f"📍 Pivot Spatial validé : **{pays_choisi}** ➡️ {prov_choisie} ➡️ {dep_choisi} ➡️ {arrond_choisi} ➡️ **{localite_saisie if localite_saisie else 'Non spécifiée'}**")

    st.markdown("---")
    st.subheader("📝 Étape 2 : Identité Judiciaire & Registre Familial (KYC)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        p_nom = st.text_input("Nom complet (tel que mentionné sur la CNI/Passeport)")
        p_piece_type = st.selectbox("Type de pièce d'identité produite :", ["Carte Nationale d'Identité (CNI)", "Passeport", "Carte de Planteur Rapproché"])
        p_piece_num = st.text_input("Numéro du document d'identité")
        p_situation = st.selectbox("Situation Matrimoniale", ["Célibataire", "Marié (Monogame)", "Marié (Polygame)", "Veuf"])
    
    with col_f2:
        st.write("📸 **Numérisation Réglementaire de la Pièce d'Identité (Double Face)**")
        photo_recto = st.camera_input("1. Scanner la face avant (RECTO)", key="cni_recto")
        photo_verso = st.camera_input("2. Scanner la face arrière (VERSO)", key="cni_verso")

    # REGISTRE DYNAMIQUE DES ENFANTS À CHARGE
    st.markdown("#### 👶 Structure Familiale & Enfants à Charge")
    nb_enfants = st.slider("Nombre d'enfants rattachés au foyer :", 0, 15, 0)
    
    enfants_data = []
    if nb_enfants > 0:
        st.info("Renseignez les données individuelles pour l'évaluation de l'indice de vulnérabilité sociale :")
        for i in range(nb_enfants):
            with st.container(border=True):
                st.markdown(f"**👦 Enfant N°{i+1}**")
                col_en1, col_en2, col_en3, col_en4, col_en5 = st.columns(5)
                with col_en1:
                    e_nom = st.text_input(f"Nom complet", key=f"e_nom_{i}")
                with col_en2:
                    e_naiss = st.number_input(f"Année de Naissance", min_value=1990, max_value=2026, value=2015, key=f"e_naiss_{i}")
                with col_en3:
                    e_age = datetime.now().year - e_naiss
                    st.metric("Âge calculé", f"{e_age} ans")
                with col_en4:
                    e_scol = st.selectbox("Scolarisé ?", ["Oui", "Non"], key=f"e_scol_{i}")
                with col_en5:
                    e_charge = st.selectbox("À la charge effective ?", ["Oui (Dépendance totale)", "Non (Pris en charge par un tiers/oncle)"], key=f"e_charge_{i}")
                
                enfants_data.append({"Nom": e_nom, "Age": e_age, "Scolarisé": e_scol, "A Charge": e_charge})

    st.markdown("---")
    st.subheader("🗺️ Étape 3 : Matrice Diversifiée d'Activités Économiques")
    
    # 4 RUBRIQUES DÉROULANTES D'ACTIVITÉS
    with st.expander("🥦 RUBRIQUE A : Production Végétale (Cultures & Vergers)", expanded=True):
        nb_p_veg = st.number_input("Nombre de parcelles végétales distinctes :", min_value=0, max_value=10, value=1)
        for k in range(int(nb_p_veg)):
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1: st.selectbox(f"Spéculation", VEGETAUX, key=f"veg_spec_{k}")
            with col_v2: st.number_input(f"Superficie (Hectares)", min_value=0.1, value=1.0, key=f"veg_surf_{k}")
            with col_v3: st.number_input(f"Âge de la plantation (Années)", min_value=0, key=f"veg_age_{k}")

    with st.expander("🐓 RUBRIQUE B : Production Animale (Élevages & Cheptels)"):
        nb_p_ani = st.number_input("Nombre d'ateliers d'élevage distincts :", min_value=0, max_value=10, value=0)
        for k in range(int(nb_p_ani)):
            col_an1, col_an2, col_an3 = st.columns(3)
            with col_an1: st.selectbox(f"Type d'Élevage", ANIMAUX, key=f"ani_spec_{k}")
            with col_an2: st.number_input(f"Effectif / Têtes / Sujets", min_value=1, value=100, key=f"ani_eff_{k}")
            with col_an3: st.selectbox(f"Type d'infrastructure", ["Bâtiment semi-moderne", "Traditionnel en brousse", "Cages/Étangs hors-sol"], key=f"ani_infra_{k}")

    with st.expander("🏪 RUBRIQUE C : Activités Commerciales Associées"):
        comm_active = st.checkbox("Le producteur possède-t-il une boutique ou activité de revente brousse ?")
        if comm_active:
            st.text_input("Nature des produits commercialisés :", placeholder="Ex: Intrants, Épicerie, Produits de première nécessité...")
            st.number_input("Estimation du chiffre d'affaires mensuel lié au commerce (FCFA) :", min_value=0, value=50000)

    with st.expander("🎨 RUBRIQUE D : Activités Artisanales & Transformations"):
        art_active = st.checkbox("Le producteur exerce-t-il une activité de transformation ou artisanat ?")
        if art_active:
            st.selectbox("Type d'artisanat :", ["Transformation de Manioc (Gari, Tapioca, Miondo)", "Pressage d'huile de palme", "Menuiserie / Vannerie", "Forge / Outillage agricole"])
            st.number_input("Revenus annuels générés par l'artisanat (FCFA) :", min_value=0, value=150000)

    # --- ÉVALUATION SANITAIRE INTERNE ---
    st.markdown("---")
    st.subheader("🧠 Étape 4 : Analyse Phytosanitaire Automatisée")
    user_severity = st.slider("Indice de Sévérité observé sur le terrain (0 à 4)", 0, 4, 1)
    
    # Appel sécurisé au moteur via les secrets
    res_core = Saphir_Core_Engine(user_severity, 12.5) # distance simulée
    st.success(f"Résultat du moteur analytique : {res_core['diagnostic']} (Score de risque : {res_core['score_fraude']}%)")

    if st.button("💾 Enregistrer la fiche unifiée du producteur"):
        st.toast("Fiche enregistrée avec succès dans la base centrale SAPHIR !", icon="🛰️")

# =====================================================================
# MODULE BOURSE D'ÉCHANGE BI-LATÉRALE (SAPHIR TRADE)
# =====================================================================
else:
    st.header("💱 SAPHIR TRADE — Gestion des Volumes, Stocks & Intentions de Campagne")
    
    tab_prod, tab_ach = st.tabs(["🧑‍🌾 ESPACE VENDEUR (Producteur)", "🏢 ESPACE ACHETEUR (Industriels/Chocolatiers)"])
    
    with tab_prod:
        st.subheader("📊 Déclarations de Campagne du Producteur")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            prod_spec = st.selectbox("Sélectionner la Spéculation à mettre sur le marché :", VEGETAUX)
        with col_t2:
            prev_2027 = st.number_input("Vos prévisions de récolte pour la Campagne 2027 (en Tonnes) :", min_value=0.0, value=5.0)
        with col_t3:
            tonnage_reel = st.number_input("Tonnage Réel actuellement récolté (en Tonnes) :", min_value=0.0, value=3.5)
            
        col_t4, col_t5 = st.columns(2)
        with col_t4:
            statut_stock = st.radio("Destination immédiate du volume récolté :", ["En Stock (Conservation/Attente des prix)", "À vendre immédiatement"])
        with col_t5:
            volume_a_vendre = st.number_input("Sur ce volume, quelle quantité mettre en vente aujourd'hui (Tonnes) :", min_value=0.0, max_value=tonnage_reel, value=0.0 if statut_stock == "En Stock (Conservation/Attente des prix)" else tonnage_reel)

        if st.button("🚀 Publier l'offre sur la Bourse Régionale"):
            st.session_state["offres_marche"].append({
                "Spéculation": prod_spec, "Volume Dispo": volume_a_vendre, "Statut": statut_stock, "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("Votre déclaration est désormais visible par tous les acheteurs agréés CEMAC.")

    with tab_ach:
        st.subheader("🛒 Demandes de l'Acheteur & Consultation du Marché")
        
        st.markdown("#### 📡 Offres actuellement disponibles sur le marché (Temps Réel) :")
        if len(st.session_state["offres_marche"]) == 0:
            st.info("Aucun producteur n'a émis d'offre de vente pour le moment.")
        else:
            st.dataframe(pd.DataFrame(st.session_state["offres_marche"]), use_container_width=True)
            
        st.markdown("---")
        st.subheader("🔒 Émission d'une Intention d'Achat (Compte Séquestre)")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            a_spec = st.selectbox("Spéculation recherchée par l'industriel :", VEGETAUX, key="ach_spec")
            a_req = st.number_input("Besoin prévisionnel total pour la campagne (Tonnes) :", min_value=1.0, value=50.0)
        with col_a2:
            a_prix = st.number_input("Prix d'achat proposé (FCFA / Kg) :", min_value=1, value=2900)
            
        montant_total = int(a_req * 1000 * a_prix)
        st.metric("Volume financier total à bloquer sur compte séquestre OAPI :", f"{montant_total:,} FCFA")
        if st.button("🔐 Émettre l'ordre d'achat sécurisé"):
            st.success(f"Ordre d'achat de {a_req} Tonnes validé. Fonds provisionnés sur la Banque de Règlement SAPHIR.")

st.markdown("---")
st.caption("© 2026 GODGIE Group — Plateforme Inter-États d'Harmonisation Phytosanitaire. Droits réservés OAPI/OHADA.")
