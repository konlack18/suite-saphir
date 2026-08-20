# SAPHIR Suite

**SAPHIR Suite** est une application Streamlit de démonstration pour l’enregistrement de parcelles, le suivi phytosanitaire, la génération d’alertes opérationnelles et le suivi d’un marché agricole dans la zone CEMAC.

## Fonctionnalités

| Module | Rôle principal |
| --- | --- |
| **SAPHIR Field** | Enregistrement KYC, relevé manuel de bornes GPS, cartographie et export CSV des parcelles. |
| **SAPHIR Core** | Simulation locale et reproductible d’analyse NDVI ainsi que calcul d’un score de risque. |
| **SAPHIR Pharma** | Génération et aperçu de messages d’alerte SMS ; aucun SMS réel n’est envoyé. |
| **SAPHIR Trade** | Déclaration de prévisions, stocks, offres et demandes dans un environnement de démonstration. |

> Les analyses Sentinel-2, les alertes SMS et les opérations commerciales sont des **simulations locales**. Cette version ne contacte ni service satellite, ni passerelle SMS, ni prestataire de paiement.

## Installation

Créez un environnement Python, puis installez les dépendances déclarées :

```bash
python -m venv .venv
source .venv/bin/activate  # Sous Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L’application s’ouvre ensuite dans le navigateur à l’adresse affichée par Streamlit, habituellement `http://localhost:8501`.

## Identité visuelle

Les logos officiels de la suite sont stockés dans `assets/brand/`. Le logo principal SAPHIR est affiché dans l’en-tête et dans la barre latérale.

## Données et confidentialité

Les données saisies sont conservées uniquement dans la session de navigateur en cours. Elles ne sont ni enregistrées dans une base distante ni transmises à une API par cette application de démonstration.

## Structure

```text
app.py              # Point d’entrée unique de l’application
requirements.txt    # Dépendances Python
assets/brand/       # Logos officiels SAPHIR et Groupe GODGIE
```
