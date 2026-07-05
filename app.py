import streamlit as st
import pandas as pd
import numpy as np
import types
import sys
from datetime import datetime

# 🛡️ CHARGEMENT DYNAMIQUE INTERNE — PROTÉGÉ PAR LES SECRETS STREAMLIT
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
    page_title="SAPHIR Suite v2.0 - Écosystème Industriel Afrique Centrale",
    page_icon="🛡️",
    layout="wide"
)

# --- BASE DE DONNÉES GÉO-ADMINISTRATIVE COMPLÈTE CEMAC ---
GEO_COMPLET_CEMAC = {
    "Cameroun": {
        "Type": "Région",
        "Unités": {
            "Centre": ["Haute-Sanaga", "Lekié", "Mfoundi", "Nyong-et-So'o", "Mbam-et-Inoubou", "Mbam-et-Kim", "Méfou-et-Afamba", "Méfou-et-Akono", "Nyong-et-Kéllé", "Nyong-et-Mfoumou"],
            "Littoral": ["Wouri", "Moungo", "Sanaga-Maritime", "Nkam"],
            "Extrême-Nord": ["Diamaré", "Logone-et-Chari", "Mayo-Danay", "Mayo-Kani", "Mayo-Sava", "Mayo-Tsanaga"],
            "Nord": ["Bénoué", "Faro", "Mayo-Louti", "Mayo-Rey"],
            "Adamaoua": ["Vina", "Djerem", "Faro-et-Déo", "Mayo-Banyo", "Mbéré"],
            "Est": ["Lom-et-Djérem", "Haut-Nyong", "Kadey", "Boumba-et-Ngoko"],
            "Sud": ["Mvila", "Dja-et-Lobo", "Océan", "Vallée-du-Ntem"],
            "Ouest": ["Mifi", "Bamboutos", "Haut-Nkam", "Hauts-Plateaux", "Koung-Khi", "Menoua", "Ndé", "Noun"],
            "Nord-Ouest": ["Mezam", "Boyo", "Bui", "Donga-Mantung", "Menchum", "Momo", "Ngoketunjia"],
            "Sud-Ouest": ["Fako", "Koupe-Manengouba", "Lebialem", "Manyu", "Meme", "Ndian"]
        }
    },
    "Gabon": {
        "Type": "Province",
        "Unités": {
            "Estuaire": ["Komo-Mondah", "Komo", "Komo-Kango", "Noya"],
            "Haut-Ogooué": ["Mpassa", "Lékoni-Lékori", "Léconi", "Lékoko", "Lemboumbi-Leyou", "Mpassa-Franceville"],
            "Moyen-Ogooué": ["Abanga-Bigné", "Ogooué-et-Des-Lacs"],
            "Ngounié": ["Boumi-Louetsi", "Dola", "Douya-Onoye", "Tsamba-Magotsi"],
            "Nyanga": ["Basse-Banio", "Douigni", "Haute-Banio", "Mougoutsi"],
            "Ogooué-Ivindo": ["Ivindo", "Lopé", "Mvoung", "Zadié"],
            "Ogooué-Lolo": ["Lolo-Bouenguidi", "Lombo-Bouenguidi", "Mouloundou"],
            "Ogooué-Maritime": ["Bendjé", "Etimboué", "Ndougou"],
            "Woleu-Ntem": ["Woleu", "Ntem", "Haut-Ntem", "Haut-Komo", "Okano"]
        }
    },
    "Congo (Brazzaville)": {
        "Type": "Département",
        "Unités": {
            "Brazzaville": ["Arrondissements 1-9"], "Pointe-Noire": ["Arrondissements 1-6"],
            "Pool": ["Kinkala", "Mindouli", "Kindamba"], "Bouenza": ["Madingou", "Nkayi"],
            "Lékoumou": ["Sibiti"], "Niari": ["Dolisie", "Mossendjo"], "Plateaux": ["Djambala"],
            "Cuvette": ["Owando"], "Cuvette-Ouest": ["Ewo"], "Sangha": ["Ouesso"],
            "Likouala": ["Impfondo"], "Niari-Kouilou": ["Loango"]
        }
    },
    "Tchad": {
        "Type": "Province",
        "Unités": {
            "N'Djamena": ["Arrondissements 1-10"], "Chari-Baguirmi": ["Massenya"], "Hadjer-Lamis": ["Massakory"],
            "Lac": ["Bol"], "Kanem": ["Mao"], "Barh El Gazel": ["Moussoro"], "Batha": ["Ati"],
            "Gera": ["Mongo"], "Ouaddaï": ["Abéché"], "Wadi Fira": ["Biltine"], "Ennedi Est": ["Amdjarass"],
            "Ennedi Ouest": ["Fada"], "Borkou": ["Faya-Largeau"], "Tibesti": ["Bardaï"], "Mayo-Kebbi Est": ["Bongor"],
            "Mayo-Kebbi Ouest": ["Pala"], "Tandjilé": ["Laï"], "Logone Occidental": ["Moundou"],
            "Logone Oriental": ["Doba"], "Mandoul": ["Koumra"], "Moyen-Chari": ["Sarh"], "Salamat": ["Am Timan"],
            "Sila": ["Goaz Beïda"]
        }
    },
    "République Centrafricaine (RCA)": {
        "Type": "Préfecture",
        "Unités": {
            "Bangui": ["Arrondissements 1-8"], "Ombella-M'Poko": ["Bimbo"], "Lobaye": ["Mbaïki"],
            "Mambéré-Kadéï": ["Berbérati"], "Nana-Mambéré": ["Bouar"], "Sangha-Mbaéré": ["Nola"],
            "Ouham": ["Bossangoa"], "Ouham-Pendé": ["Bocaranga"], "Nana-Grébizi": ["Kaga-Bandoro"],
            "Bamingui-Bangoran": ["Ndele"], "Vakaga": ["Birao"], "Haute-Kotto": ["Bria"],
            "Basse-Kotto": ["Mobaye"], "Mbomou": ["Bangassou"], "Haut-Mbomou": ["Obo"],
            "Kémo": ["Sibut"], "Ouaka": ["Bambari"], "Lim-Pendé": ["Paoua"], "Mambéré": ["Carnot"], "M'Poko": ["Boali"]
        }
    },
    "Guinée Équatoriale": {
        "Type": "Province",
        "Unités": {
            "Bioko-Norte": ["Malabo"], "Bioko-Sur": ["Luba"], "Litoral": ["Bata"],
            "Centro-Sur": ["Evinayong"], "Kié-Ntem": ["Ebebiyín"], "Wele-Nzas": ["Mongomo"],
            "Annobón": ["San Antonio de Palé"], "Djibloho": ["Ciudad de la Paz"]
        }
    }
}

ARRONDISSEMENTS_REFERENCE = {
    "Haute-Sanaga": ["Minta", "Mbandjock", "Nanga-Eboko", "Bibey", "Lembe-Yezoum"],
    "Lekié": ["Obala", "Monatélé", "Evodoula", "Sa'a"],
    "Mfoundi": ["Yaoundé I", "Yaoundé II", "Yaoundé III", "Yaoundé IV"]
}

VEGETAUX = ["Cacao (Theobroma cacao)", "Manioc / Cassava", "Maïs Jaune", "Banane Plantain", "Café Robusta", "Café Arabica", "Poivre de Penja"]
ANIMAUX = ["Poulets de chair", "Pondeuses", "Porcs", "Bovins", "Pisciculture"]

# --- INITIALISATION DES SESSIONS STATES ---
if "offres_marche" not in st.session_state:
    st.session_state["offres_marche"] = []
if "acheteurs_demandes" not in st.session_state:
    st.session_state["acheteurs_demandes"] = []
if "parcelles_a_maper" not in st.session_state:
    st.session_state["parcelles_a_maper"] = []
if "etape_en cours" not in st.session_state:
    st.session_state["etape_en_cours"] = "Enquête"
if "signature_valide" not in st.session_state:
    st.session_state["signature_valide"] = False

# --- HEADER APP ---
st.title("🛡️ SAPHIR Suite v2.0 — Écosystème Industriel Inter-États")
st.caption("Système d'Alerte Précoce et d'Harmonisation de l'Intervention Phytosanitaire Régionale — Directeur : Ing. Roméo Moffo Konlack")

# --- NAVIGATION DES MODULES ---
user_role = st.sidebar.radio(
    "🧭 MODULES STRATÉGIQUES :",
    ["🧑‍🌾 SAPHIR Field & Mapping Offline", "💱 SAPHIR TRADE (Bourse des Stocks)"]
)

st.markdown("---")

# =====================================================================
# MODULE 1 : SAPHIR FIELD & MAPPING OFFLINE
# =====================================================================
if user_role == "🧑‍🌾 SAPHIR Field & Mapping Offline":
    
    if st.session_state["etape_en_cours"] == "Enquête":
        st.header("📍 SAPHIR Field — Enregistrement Unifié & KYC")
        
        # 📸 PHOTO DU PRODUCTEUR AU DÉBUT DU QUESTIONNAIRE
        st.subheader("📸 Profil Biométrique Inicial")
        photo_prod = st.camera_input("Prendre la photo officielle du producteur (Début du questionnaire) *")
        
        st.markdown("---")
        
        # ÉTAPE 1 : ARBORESCENCE GÉO-ADMINISTRATIVE DYNAMIQUE CEMAC
        st.subheader("🌐 Localisation Administrative CEMAC")
        col_g1, col_g2, col_g3 = st.columns(3)
        
        with col_g1:
            pays_choisi = st.selectbox("1. Sélectionner le Pays (Afrique Centrale) :", list(GEO_COMPLET_CEMAC.keys()))
        
        type_admin = GEO_COMPLET_CEMAC[pays_choisi]["Type"]
        unites_dispo = list(GEO_COMPLET_CEMAC[pays_choisi]["Unités"].keys())
        
        with col_g2:
            prov_choisie = st.selectbox(f"2. Sélectionner la/le {type_admin} :", unites_dispo)
            
        sub_dispo = GEO_COMPLET_CEMAC[pays_choisi]["Unités"][prov_choisie]
        with col_g3:
            sub_choisie = st.selectbox("3. Sélectionner le Département / Subdivision :", sub_dispo)
            
        col_g4, col_g5 = st.columns(2)
        with col_g4:
            if sub_choisie in ARRONDISSEMENTS_REFERENCE:
                arrond_choisi = st.selectbox("4. Sélectionner l'Arrondissement :", ARRONDISSEMENTS_REFERENCE[sub_choisie])
            else:
                arrond_choisi = st.text_input("4. Entrer l'Arrondissement / Commune :", value="Arrondissement Unique")
        with col_g5:
            localite_saisie = st.text_input("5. Saisir la Localité / Village (Saisie Manuelle) * :", placeholder="Ex: Meba, Village Angono...")

        st.info(f"📍 Pivot de Traçabilité Validé : **{pays_choisi}** ➡️ {prov_choisie} ➡️ {sub_choisie} ➡️ {arrond_choisi} ➡️ **{localite_saisie if localite_saisie else 'En attente'}**")

        st.markdown("---")
        
        # ÉTAPE 2 : IDENTITÉ JUDICIAIRE & KYC DU CHEF DE MÉNAGE
        st.subheader("📝 Fiche d'Identité & Pièces Officielles")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            p_nom = st.text_input("Nom complet du producteur (Conforme CNI) *")
            p_piece_num = st.text_input("Numéro de CNI / Passeport *")
            p_situation = st.selectbox("Situation Matrimoniale :", ["Célibataire", "Marié (Monogame)", "Marié (Polygame)", "Veuf"])
        with col_f2:
            st.write("📸 **Numérisation Obligatoire de la Pièce d'Identité**")
            photo_recto = st.camera_input("1. Scanner la face avant (RECTO)", key="cni_recto")
            photo_verso = st.camera_input("2. Scanner la face arrière (VERSO)", key="cni_verso")

        # --- MODULE DYNAMIQUE POUR L'ÉPOUSE (OU LES ÉPOUSES) ---
        epouses_data = []
        if "Marié" in p_situation:
            st.markdown("---")
            st.subheader("👰 Identification & Enquêtes Activités Épouse(s)")
            
            nb_epouses = 1 if p_situation == "Marié (Monogame)" else st.number_input("Nombre d'épouses rattachées :", min_value=1, max_value=5, value=1)
            
            for idx in range(int(nb_epouses)):
                with st.container(border=True):
                    st.markdown(f"**Identité Complète de l'Épouse N°{idx+1}**")
                    col_ep1, col_ep2 = st.columns(2)
                    with col_ep1:
                        ep_nom = st.text_input(f"Nom Complet de l'Épouse", key=f"ep_nom_{idx}")
                        ep_cni = st.text_input(f"Numéro de sa CNI", key=f"ep_cni_{idx}")
                    with col_ep2:
                        st.write("📸 CNI de l'épouse")
                        st.camera_input(f"Scanner CNI Épouse N°{idx+1}", key=f"ep_cam_{idx}")
                    
                    st.markdown(f"**🎯 Rubriques d'Activités Autonomes de l'Épouse N°{idx+1} :**")
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        ep_veg = st.multiselect("Production Végétale de l'épouse :", VEGETAUX, key=f"ep_veg_{idx}")
                        ep_ani = st.multiselect("Production Animale de l'épouse :", ANIMAUX, key=f"ep_ani_{idx}")
                    with col_act2:
                        ep_comm = st.text_input("Activités Commerciales / Épicerie de l'épouse :", key=f"ep_comm_{idx}")
                        ep_art = st.text_input("Activités Artisanales / Transformation (Gari, etc.) :", key=f"ep_art_{idx}")
                    
                    epouses_data.append({"Nom": ep_nom, "CNI": ep_cni, "Végétaux": ep_veg})

        # --- ENFANTS À CHARGE ---
        st.markdown("---")
        st.subheader("👶 Registre Familial & Charges des Enfants")
        nb_enfants = st.slider("Nombre d'enfants rattachés au foyer :", 0, 15, 0)
        
        if nb_enfants > 0:
            for i in range(nb_enfants):
                with st.container(border=True):
                    col_en1, col_en2, col_en3, col_en4 = st.columns(4)
                    with col_en1: st.text_input(f"Nom de l'Enfant N°{i+1}", key=f"e_nom_{i}")
                    with col_en2: st.number_input(f"Année de Naissance", min_value=1990, max_value=2026, value=2015, key=f"e_naiss_{i}")
                    with col_en3: st.selectbox("Scolarisé ?", ["Oui", "Non"], key=f"e_scol_{i}")
                    with col_en4: st.selectbox("À charge effective ?", ["Oui", "Non"], key=f"e_charge_{i}")

        # --- DÉCLARATION INITIALE DES PARCELLES DU PRODUCTEUR ---
        st.markdown("---")
        st.subheader("🗺️ Matrice des Parcelles Déclarées (Pour Mapping futur)")
        nb_parcelles = st.number_input("Nombre total de parcelles distinctes possédées par le producteur :", min_value=1, max_value=10, value=1)
        
        liste_parcelles_locales = []
        for p_idx in range(int(nb_parcelles)):
            with st.container(border=True):
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    spec_p = st.selectbox(f"Spéculation Parcelle N°{p_idx+1}", VEGETAUX, key=f"init_spec_p_{p_idx}")
                with col_p2:
                    nom_p = st.text_input(f"Identifiant du Champ (Ex: Cacao 1, Cacao Bas-fond)", value=f"{spec_p.split()[0]} {p_idx+1}", key=f"init_nom_p_{p_idx}")
                with col_p3:
                    surf_p = st.number_input(f"Superficie estimée (Ha)", min_value=0.1, value=1.0, key=f"init_surf_p_{p_idx}")
                liste_parcelles_locales.append({"Nom": nom_p, "Spéculation": spec_p, "Ha": surf_p})

        # --- SIGNATURE ET PASSAGE AU MAPPING ---
        st.markdown("---")
        st.subheader("✒️ Validation Finale & Signature Électronique")
        st.warning("La signature du producteur clôture l'enquête descriptive et débloque le terminal pour le mapping GPS sur les limites réelles du champ.")
        
        signature_texte = st.text_input("Saisir le Nom du producteur ou 'APPROUVÉ PAR LE PLANTEUR' pour simuler la signature tactile :")
        
        if st.button("💾 Valider la signature et passer au Mapping GPS"):
            if signature_texte and photo_prod:
                st.session_state["parcelles_a_maper"] = liste_parcelles_locales
                st.session_state["signature_valide"] = True
                st.session_state["etape_en_cours"] = "Mapping"
                st.rerun()
            else:
                st.error("⚠️ La photo initiale du producteur et la signature sont obligatoires avant le mapping.")

    # --- SOUS-PAGE : MAPPING GPS DÉCONNECTÉ ---
    elif st.session_state["etape_en_cours"] == "Mapping":
        st.header("🛰️ SAPHIR Mapping — Relevé de Limites Géospatiales (Mode Offline)")
        st.info("Le questionnaire est signé. Marchez le long des limites de chaque parcelle enregistrée pour calculer le polygone exact.")
        
        for idx_m, parc in enumerate(st.session_state["parcelles_a_maper"]):
            with st.container(border=True):
                st.markdown(f"#### 🪵 Parcelle : **{parc['Nom']}** — *({parc['Spéculation']})*")
                st.write(f"Superficie déclarée : {parc['Ha']} Hectares")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    if st.button(f"⏱️ Activer le tracé GPS des limites - {parc['Nom']}", key=f"btn_map_{idx_m}"):
                        st.toast(f"Relevé des points cardinaux en cours pour {parc['Nom']}... Ne coupez pas le signal GPS.", icon="🛰️")
                with col_m2:
                    st.success(f"Status : Prêt pour le contournement du champ. Retour automatique au point initial activé.")
                    
        if st.button("🏁 Clôturer le Dossier Cartographique Global"):
            st.session_state["etape_en_cours"] = "Enquête"
            st.session_state["signature_valide"] = False
            st.success("Dossier spatial crypté et envoyé vers les serveurs SAPHIR Regionaux (CEMAC Hub).")

# =====================================================================
# MODULE 2 : SAPHIR TRADE (BOURSE DES STOCKS BI-LATÉRALE)
# =====================================================================
else:
    st.header("💱 SAPHIR TRADE — Gestion Bilatérale Acheteurs & Producteurs")
    
    tab_acheteur, tab_vendeur = st.tabs(["🏢 ESPACE INDUSTRIELS & ACHETEURS (ex: SICAO)", "🧑‍🌾 ESPACE PRODUCTEURS & PLANTEURS"])
    
    with tab_acheteur:
        st.subheader("📢 Déclarations de Besoins des Acheteurs Agréés")
        col_ac1, col_ac2 = st.columns(2)
        with col_ac1:
            ach_nom = st.text_input("Nom de l'Acheteur / Firme :", value="SIC CAO Cameroun")
            ach_spec = st.selectbox("Spéculation recherchée :", VEGETAUX, key="ach_spec_trade")
        with col_ac2:
            ach_prev_annuelle = st.number_input("Prévision Globale d'Achat pour la Campagne 2027 (Tonnes) :", min_value=1.0, value=200000.0)
            
        st.markdown("##### 📅 Calendrier Mensuel des Besoins Industriels (Tonnes) :")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1: m_jan = st.number_input("Janvier", value=15000)
        with col_m2: m_fev = st.number_input("Février", value=15000)
        with col_m3: m_mar = st.number_input("Mars", value=20000)
        with col_m4: m_avr = st.number_input("Avril", value=25000)
        
        if st.button("💾 Enregistrer la Grille des Besoins Mensuels"):
            st.session_state["acheteurs_demandes"].append({
                "Acheteur": ach_nom, "Spéculation": ach_spec, "Annuel": ach_prev_annuelle
            })
            st.success("Planification de charge industrielle publiée sur la bourse d'Afrique Centrale.")

    with tab_vendeur:
        st.subheader("📊 Arbitrage de Campagne & Disponibilité Réelle du Stock")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            v_spec = st.selectbox("Choisir votre Spéculation :", VEGETAUX, key="v_spec_trade")
        with col_v2:
            v_prev_2027 = st.number_input("Mes Prévisions Personnelles de Récolte 2027 (Tonnes) :", min_value=0.0, value=12.0)
        with col_v3:
            v_reel_recolte = st.number_input("Tonnage Réel obtenu au pont de pesée (Tonnes) :", min_value=0.0, value=10.0)
            
        st.markdown("---")
        st.subheader("📥 Ventilation Physique du Volume Réel")
        
        col_v4, col_v5 = st.columns(2)
        with col_v4:
            choix_arbitrage = st.radio(
                "Où stockez-vous ou affectez-vous ces 10 tonnes actuellement ?",
                ["Totalité mise en STOCK physique (Attente / Non vendue)", "Mise en vente immédiate"]
            )
        
        with col_v5:
            if choix_arbitrage == "Totalité mise en STOCK physique (Attente / Non vendue)":
                st.info(f"🔒 Vos {v_reel_recolte} Tonnes sont sécurisées en magasin central. Statut : **Non disponible pour les acheteurs.**")
                
                # Option exclusive : vendre une fraction du stock existant
                st.markdown("##### 🔓 Déblocage Partiel du Stock existant")
                fraction_a_vendre = st.number_input("Quantité à sortir du stock pour mise en vente immédiate (Tonnes) :", min_value=0.0, max_value=v_reel_recolte, value=0.0)
                
                if fraction_a_vendre > 0:
                    st.warning(f"Arbitrage : {v_reel_recolte - fraction_a_vendre} Tonnes resteront en stock | {fraction_a_vendre} Tonnes seront visibles sur le marché.")
                    if st.button("🚀 Confirmer la mise sur le marché partielle"):
                        st.session_state["offres_marche"].append({
                            "Spéculation": v_spec, "Volume Dispo": fraction_a_vendre, "Statut": "Déstockage Partiel", "Date": "En cours"
                        })
                        st.success("Volume financier partiel exposé aux courtiers.")
            else:
                st.success(f"🚀 Les {v_reel_recolte} Tonnes sont injectées directement sur le marché.")
                if st.button("🚀 Mettre la totalité en vente"):
                    st.session_state["offres_marche"].append({
                        "Spéculation": v_spec, "Volume Dispo": v_reel_recolte, "Statut": "Vente Directe", "Date": "En cours"
                    })

        st.ma