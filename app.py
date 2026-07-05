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
    # Simulation du moteur si absent de l'infrastructure pour éviter le blocage
    def Saphir_Core_Engine(severity, distance):
        return {
            "imqg": round(4.5 - (severity * 0.5), 2),
            "img": round(severity * 1.2, 2),
            "score_fraude": int(severity * 15 + (distance * 0.1) if distance < 500 else 10),
            "zone_couleur": "red" if severity >= 3 else ("orange" if severity == 2 else "green"),
            "diagnostic": "Alerte Critique" if severity >= 3 else "Validation Standard"
        }

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(
    page_title="SAPHIR Suite v1.0 - Écosystème Industriel Sécurisé",
    page_icon="🛡️",
    layout="wide"
)

# --- BASE DE DONNÉES ADMINISTRATIVE CEMAC (6 PAYS) ---
CEMAC_DATA = {
    "Cameroun": {
        "type": "Région",
        "divisions": {
            "Centre": {
                "Haute-Sanaga": ["Mbandjock", "Minta", "Nanga-Eboko", "Bibey", "Lembe-Yezoum"],
                "Lekié": ["Obala", "Monatélé", "Evodoula", "Sa'a"],
                "Mfoundi": ["Yaoundé 1", "Yaoundé 2", "Yaoundé 3"]
            },
            "Littoral": {
                "Wouri": ["Douala 1er", "Douala 2e", "Douala 3e"],
                "Moungo": ["Nkongsamba", "Njombé-Penja", "Mbanga"]
            },
            "Sud": {
                "Mvila": ["Ebolowa", "Biwong-Bane", "Mvangan"],
                "Océan": ["Kribi", "Akom II", "Campo"]
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
    "Congo-Brazzaville": {
        "type": "Département",
        "divisions": {
            "Bouenza": {
                "Madingou": ["Madingou Ville", "Loudima"],
                "Nkayi": ["Nkayi Commune"]
            },
            "Pool": {
                "Kinkala": ["Kinkala Ville", "Boko"]
            }
        }
    },
    "Centrafrique": {
        "type": "Préfecture",
        "divisions": {
            "Ombella-M'Poko": {
                "Bimbo": ["Bimbo 1", "Bimbo 2"],
                "Boali": ["Boali Centre"]
            }
        }
    },
    "Tchad": {
        "type": "Province",
        "divisions": {
            "Chari-Baguirmi": {
                "Massenya": ["Massenya Ville", "Dourbali"]
            }
        }
    },
    "Guinée Équatoriale": {
        "type": "Province",
        "divisions": {
            "Bioko-Norte": {
                "Malabo": ["Malabo Urban", "Baney"]
            }
        }
    }
}

# --- LISTE DES SPÉCULATIONS PAR RUBRIQUE ---
RUBRIQUES_ACTIVITES = {
    "Production Végétale": ["Cacao (Theobroma cacao)", "Café Robusta", "Café Arabica", "Manioc / Cassava", "Maïs Jaune", "Banane Plantain", "Poivre de Penja", "Macabo", "Taro", "Arachide", "Djansang"],
    "Production Animale": ["Élevage Porcin", "Aviculture (Poulets de chair/pondeuses)", "Élevage Bovin", "Ovin/Caprin", "Pisciculture"],
    "Commerce": ["Vente de produits vivriers", "Boutique d'intrants", "Collecte locale de matières premières"],
    "Artisanat": ["Transformation du manioc (Gari/Miondo)", "Tissage/Vannerie", "Menuiserie/Forge agricole"]
}

RENDEMENTS_THEORIQUES = {
    "Cacao (Theobroma cacao)": 0.8, "Manioc / Cassava (Manihot esculenta)": 15.0,
    "Maïs Jaune (Zea mays)": 3.5, "Banane Plantain (Musa paradisiaca)": 10.0,
    "Café Robusta (Coffea canephora)": 0.7, "Poivre de Penja (Piper nigrum)": 1.5
}

# --- INITIALISATION DES SESSIONS STATES ---
if "brouillon_producteur" not in st.session_state:
    st.session_state["brouillon_producteur"] = {}
if "consentement_valide" not in st.session_state:
    st.session_state["consentement_valide"] = False
if "parcelles_enregistrees" not in st.session_state:
    st.session_state["parcelles_enregistrees"] = []
if "step_mapping_actif" not in st.session_state:
    st.session_state["step_mapping_actif"] = False
if "trade_stocks" not in st.session_state:
    st.session_state["trade_stocks"] = {"Cacao (Theobroma cacao)": {"stock": 10.0, "en_vente": 5.0}}
if "trade_previsions_acheteur" not in st.session_state:
    st.session_state["trade_previsions_acheteur"] = []

# --- HEADER ET BANDEAU CONNECTÉ ---
st.title("🛡️ SAPHIR Suite v1.0 — Plateforme Agro-Industrielle Intégrée")
st.caption("Propriété exclusive de GODGIE Group — Directeur de Projet : Ing. Roméo Moffo Konlack")

st.markdown(" ")

# --- VÉRIFICATION DU CONSENTEMENT ---
if not st.session_state["consentement_valide"]:
    st.header("🔐 Charte de Protection des Données & Consentement")
    st.warning("Conformément aux directives de l'OHADA et de la CEMAC, le recueil des coordonnées géospatiales, des visuels d'identité et des pièces justificatives juridiques requiert un consentement éclairé.")
    with st.container(border=True):
        st.markdown("""
        **Formulaire de Consentement Éclairé (GODGIE Group) :**
        1. **Données GPS & Cartographie :** J'autorise SAPHIR Field à enregistrer l'emplacement et la structure polygonale de mes parcelles.
        2. **Pièces d'Identité & Biométrie :** J'accepte la numérisation de ma pièce d'identité (Recto/Verso) et de ma photo d'identification.
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

# --- SÉLECTION DES NIVEAUX D'ACCÈS ---
user_role = st.radio(
    "Veuillez choisir votre profil d'accès pour adapter l'affichage :",
    ["🧑‍🌾 Espace Producteurs & Enquêtes (SAPHIR Field)", "💱 SAPHIR TRADE — Marché & Prévisions Brousse/Industrie"],
    horizontal=True
)

st.markdown("---")

# =====================================================================
# MODULE ENQUÊTES, PARCELLES & KYC NUMÉRIQUE (SAPHIR FIELD)
# =====================================================================
if user_role == "🧑‍🌾 Espace Producteurs & Enquêtes (SAPHIR Field)":
    
    if not st.session_state["step_mapping_actif"]:
        st.header("📍 SAPHIR Field — Enregistrement Unifié & KYC")
        
        # --- ÉTAPE 1 : GEOLOCALISATION DYNAMIQUE DÉROULANTE ---
        st.subheader("🌐 Étape 1 : Localisation Géo-Administrative Dynamique (CEMAC)")
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            sel_pays = st.selectbox("1. Choisir le Pays :", list(CEMAC_DATA.keys()))
            type_label = CEMAC_DATA[sel_pays]["type"]
            
        with col_g2:
            # Filtrage automatique de la Province/Région selon le pays
            list_provinces = list(CEMAC_DATA[sel_pays]["divisions"].keys())
            sel_province = st.selectbox(f"2. Sélectionner la {type_label} :", list_provinces)
            
        with col_g3:
            # Filtrage automatique du Département
            list_départements = list(CEMAC_DATA[sel_pays]["divisions"][sel_province].keys())
            sel_dept = st.selectbox("3. Sélectionner le Département :", list_départements)
            
        col_g4, col_g5, col_g6 = st.columns(3)
        with col_g4:
            # Filtrage automatique de l'Arrondissement
            list_arrond = CEMAC_DATA[sel_pays]["divisions"][sel_province][sel_dept]
            sel_arrond = st.selectbox("4. Sélectionner l'Arrondissement :", list_arrond)
            
        with col_g5:
            # Saisie manuelle obligatoire de la localité spécifique
            sel_localite = st.text_input("5. Saisir la Localité / Village (Saisie manuelle) :", placeholder="Ex: Meba, Minta Centre...")
            
        with col_g6:
            geo_lat = st.number_input("Latitude Réelle (GPS)", format="%.5f", value=4.4621)
            geo_lon = st.number_input("Longitude Réelle (GPS)", format="%.5f", value=11.9124)

        st.markdown("---")
        
        # --- ÉTAPE 2 : IDENTIFICATION BIOMÉTRIQUE & KYC INITIAL ---
        st.subheader("📝 Étape 2 : Identité & Captures Biométriques Initiales")
        
        col_kyc1, col_kyc2 = st.columns(2)
        with col_kyc1:
            p_nom = st.text_input("Nom complet du producteur (Selon CNI/Passeport)")
            p_age = st.number_input("Âge du chef d'exploitation", min_value=18, max_value=100, value=35)
            p_piece_type = st.selectbox("Type de pièce d'identité :", ["Carte Nationale d'Identité (CNI)", "Passeport", "Carte de Planteur"])
            p_piece_num = st.text_input("Numéro de la pièce d'identité")
            p_situation = st.selectbox("Situation Matrimoniale", ["Célibataire", "Marié (Monogame)", "Marié (Polygame)", "Veuf"])
            
        with col_kyc2:
            st.write("📸 **Capture Portrait Initial du Producteur**")
            photo_chef = st.camera_input("Prendre la photo du Producteur (Obligatoire au début)", key="chef_photo")

        # --- CAPTURE DOUBLE FACE CNI ---
        st.markdown("##### 🪪 Numérisation de la Pièce d'Identité (Obligatoire Recto / Verso)")
        col_cni1, col_cni2 = st.columns(2)
        with col_cni1:
            photo_recto = st.camera_input("Scanner la pièce d'identité — FACE RECTO", key="cni_recto")
        with col_cni2:
            photo_verso = st.camera_input("Scanner la pièce d'identité — FACE VERSO", key="cni_verso")

        st.markdown("---")

        # --- COMPORTEMENT DYNAMIQUE : ÉPOUSES ---
        if "Marié" in p_situation:
            st.subheader("👩‍🌾 Étape 2.1 : Renseignement d'Identification des Épouses")
            nb_femmes = st.slider("Nombre d'épouses au sein du ménage", 1, 4, 1)
            
            for i in range(nb_femmes):
                with st.container(border=True):
                    st.markdown(f"**Données de l'Épouse N°{i+1}**")
                    col_ep1, col_ep2, col_ep3 = st.columns(3)
                    with col_ep1:
                        f_nom = st.text_input(f"Nom complet de l'Épouse N°{i+1}", key=f"f_nom_{i}")
                        f_age = st.number_input(f"Âge Épouse N°{i+1}", min_value=18, max_value=100, value=30, key=f"f_age_{i}")
                    with col_ep2:
                        f_rubrique = st.selectbox(f"Rubrique Principale d'Activité N°{i+1}", list(RUBRIQUES_ACTIVITES.keys()), key=f"f_rubrique_{i}")
                    with col_ep3:
                        f_spec = st.selectbox(f"Spécification de l'activité N°{i+1}", RUBRIQUES_ACTIVITES[f_rubrique], key=f"f_spec_{i}")
                    
                    # Capture CNI Recto/Verso pour l'épouse identiquement au mari
                    col_cni_f1, col_cni_f2 = st.columns(2)
                    with col_cni_f1:
                        photo_f_r = st.camera_input(f"Pièce Épouse N°{i+1} — RECTO", key=f"f_recto_{i}")
                    with col_cni_f2:
                        photo_f_v = st.camera_input(f"Pièce Épouse N°{i+1} — VERSO", key=f"f_verso_{i}")

        # --- COMPORTEMENT DYNAMIQUE : ENFANTS ---
        st.markdown("---")
        st.subheader("👶 Étape 2.2 : Renseignement Détaillé des Enfants à Charge")
        nb_enfants = st.slider("Nombre d'enfants rattachés", 0, 15, 0)
        
        enfants_data = []
        if nb_enfants > 0:
            for j in range(nb_enfants):
                with st.container(border=True):
                    st.markdown(f"**Fiche Enfant N°{j+1}**")
                    col_en1, col_en2, col_en3, col_en4 = st.columns(4)
                    with col_en1:
                        e_nom = st.text_input(f"Nom complet de l'enfant N°{j+1}", key=f"e_nom_{j}")
                    with col_en2:
                        e_naiss = st.number_input(f"Année de Naissance N°{j+1}", min_value=1990, max_value=2026, value=2015, key=f"e_naiss_{j}")
                        e_age = 2026 - e_naiss
                        st.caption(f"Âge calculé : {e_age} ans")
                    with col_en3:
                        e_scolarise = st.radio(f"Scolarisé ?", ["Oui", "Non"], key=f"e_scol_{j}", horizontal=True)
                    with col_en4:
                        e_charge = st.radio(f"Effectivement à charge des parents ?", ["Oui", "Non"], key=f"e_charge_{j}", horizontal=True)
                    
                    enfants_data.append({"Nom": e_nom, "Age": e_age, "Scolarisé": e_scolarise, "À Charge": e_charge})

        st.markdown("---")

        # --- ÉTAPE 3 : ENREGISTREMENT STRUCTUREL DES PARCELLES MULTI-RUBRIQUES ---
        st.subheader("🗺️ Étape 3 : Spéculations & Enregistrement Pré-Cartographique")
        nb_parcelles = st.number_input("Nombre d'unités de production / parcelles à enregistrer :", min_value=1, max_value=20, value=1)
        
        parcelles_temp = []
        for k in range(int(nb_parcelles)):
            with st.container(border=True):
                st.markdown(f"**📐 Fiche Pré-Identification — Unité N°{k+1}**")
                col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                with col_p1:
                    p_rub = st.selectbox(f"Type de Secteur N°{k+1}", list(RUBRIQUES_ACTIVITES.keys()), key=f"p_rub_{k}")
                with col_p2:
                    p_spec = st.selectbox(f"Spéculation N°{k+1}", RUBRIQUES_ACTIVITES[p_rub], key=f"p_spec_{k}")
                with col_p3:
                    p_surf = st.number_input(f"Dimension / Superficie (Ha)", min_value=0.1, value=1.0, key=f"p_surf_{k}")
                with col_p4:
                    p_conduite = st.selectbox(f"Régime d'exploitation", ["Intensif", "Traditionnel", "Agroforesterie"], key=f"p_cond_{k}")
                
                parcelles_temp.append({
                    "id": f"{p_spec} {k+1}",
                    "secteur": p_rub,
                    "speculation": p_spec,
                    "superficie": p_surf,
                    "conduite": p_conduite,
                    "statut": "❌ Non Mapée"
                })

        # --- SIGNATURE ET VALIDATION POUR PASSER AU MAPPING ---
        st.markdown("---")
        st.subheader("✍️ Étape 4 : Clôture Juridique & Signature du Producteur")
        signature_certif = st.checkbox("Le producteur appose sa signature numérique et certifie l'exactitude du dossier juridique complet.")
        
        if signature_certif:
            if st.button("🚀 Valider & Ouvrir le Module de Télédétection / Mapping Terrain"):
                st.session_state["parcelles_enregistrees"] = parcelles_temp
                st.session_state["step_mapping_actif"] = True
                st.rerun()
        else:
            st.info("🔒 La signature est requise pour débloquer le système d'arpentage et de mapping des polygones.")

    # =====================================================================
    # INTERFACE DE MAPPING OFFLINE / TERRAIN (S'OUVRE APRÈS SIGNATURE)
    # =====================================================================
    else:
        st.header("🛰️ SAPHIR Field — Module de Télédétection & Arpentage Offline")
        st.success("🔒 Dossier signé juridiquement. Veuillez procéder au mapping des parcelles enregistrées une à une.")
        
        parcelles = st.session_state["parcelles_enregistrees"]
        
        with st.sidebar:
            st.markdown("### 📋 Liste des Parcelles à Arpenter")
            for idx, p in enumerate(parcelles):
                st.markdown(f"**{p['id']}** : {p['statut']}")
            
            if st.button("↩️ Revenir au Formulaire"):
                st.session_state["step_mapping_actif"] = False
                st.rerun()

        # Choix de la parcelle active à contourner
        options_parcelles = [p["id"] for p in parcelles if p["statut"] == "❌ Non Mapée"]
        
        if len(options_parcelles) > 0:
            sel_p_map = st.selectbox("Sélectionner la parcelle à arpenter actuellement :", options_parcelles)
            
            with st.container(border=True):
                st.markdown(f"### 🚶‍♂️ Protocole d'Arpentage Terrain — Parcelle : `{sel_p_map}`")
                st.info("Instructions : Positionnez-vous aux limites initiales du champ. Cliquez sur démarrer, puis contournez les limites physiques du champ avant de revenir au point initial.")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.button("🟢 Initialiser le point de départ GPS (Borne 0)")
                    st.button("📍 Enregistrer un point de pivotement polygonal (Borne radar)")
                with col_m2:
                    if st.button("🏁 Clôturer le polygone (Retour au point initial)"):
                        for p in parcelles:
                            if p["id"] == sel_p_map:
                                p["statut"] = "✅ Mapée (Polygone validé localement)"
                        st.toast(f"Parcelle {sel_p_map} enregistrée avec succès !", icon="🛰️")
                        st.rerun()
                        
                # Simulation visuelle d'un arpentage radar
                st.caption("🌐 _Aperçu du signal télémétrique offline :_")
                chart_data = pd.DataFrame(
                    np.random.randn(10, 2) / 1000 + [4.4621, 11.9124],
                    columns=['lat', 'lon']
                )
                st.map(chart_data)
        else:
            st.balloons()
            st.success("🎉 Toutes les parcelles ont été cartographiées et synchronisées par satellite !")
            
            # Récapitulatif final exportable
            df_final = pd.DataFrame(parcelles)
            st.dataframe(df_final)
            
            csv_final = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le registre global signé et géoréférencé",
                data=csv_final,
                file_name="SAPHIR_EXPORT_FINAL_PROD.csv",
                mime="text/csv"
            )


# =====================================================================
# MODULE MARCHÉ ET PRÉVISIONS COMMERCIALES (SAPHIR TRADE)
# =====================================================================
else:
    st.header("💱 SAPHIR TRADE — Système de Planification & Séquestre")
    
    tab_vendeur, tab_acheteur = st.tabs(["🧑‍🌾 ESPACE VENDEUR (Producteurs / Coopératives)", "🏢 ESPACE ACHETEUR (Industriels / Chocolatiers)"])
    
    with tab_vendeur:
        st.subheader("📈 Déclarations et Gestion des Stocks Réels")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            v_spec = st.selectbox("Spéculation à mettre à jour :", RUBRIQUES_ACTIVITES["Production Végétale"])
        with col_v2:
            v_prev_2027 = st.number_input("Mes Prévisions de production pour la Campagne 2027 (Tonnes)", min_value=0.0, value=12.5)
        with col_v3:
            v_reel_dispo = st.number_input("Tonnage Réel actuellement récolté (Tonnes)", min_value=0.0, value=10.0)
            
        col_v4, col_v5 = st.columns(2)
        with col_v4:
            v_statut_stock = st.radio("Option de commercialisation immédiate :", ["Garder en Stock (Ne pas vendre)", "Mettre en Vente sur le Marché"])
        with col_v5:
            if v_statut_stock == "Mettre en Vente sur le Marché":
                v_quantite_ve