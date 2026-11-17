from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

REGIONS = ["Amérique du Nord", "Europe", "Japon", "Autres marchés"]
COLONNES = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]


@st.cache_data
def charger_donnees():
    """Charge le CSV placé à la racine du projet."""
    chemin = Path(__file__).resolve().parent.parent / "vgsales.csv"
    return pd.read_csv(chemin)


def afficher_carte(ventes):
    """Montre une carte interactive des trois zones géographiques définies."""
    carte = go.Figure(go.Scattergeo(
        lat=[39, 51, 36], lon=[-98, 15, 138],
        mode="markers+text",
        text=[f"{v:.2f} M" for v in ventes[:3]],
        textposition="top center",
        textfont=dict(size=14, color="#303030"),
        marker=dict(size=[14 + v ** 0.5 * 4 for v in ventes[:3]],
                    color="#555555", line=dict(width=2, color="white")),
        hovertext=[f"{r} : {v:.2f} millions" for r, v in zip(REGIONS[:3], ventes[:3])],
        hoverinfo="text",
    ))
    carte.update_geos(
        projection_type="natural earth", showland=True, landcolor="#E7E7E7",
        showcountries=True, countrycolor="white", showocean=True,
        oceancolor="#F9F9F9", showcoastlines=False, showframe=False,
    )
    carte.update_layout(
        height=350, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white", geo=dict(bgcolor="white"),
        annotations=[dict(x=0.97, y=0.05, xref="paper", yref="paper",
                          text=f"Autres marchés : {ventes[3]:.2f} M",
                          showarrow=False, bgcolor="white", bordercolor="#CCCCCC",
                          borderpad=7, xanchor="right")],
    )
    st.plotly_chart(carte, use_container_width=True,
                    config={"scrollZoom": True, "displayModeBar": False})


def afficher_graphique(ventes):
    """Affiche un graphique Matplotlib des quatre zones."""
    figure, axe = plt.subplots(figsize=(7, 2.7))
    barres = axe.bar(REGIONS, ventes,
                     color=["#333333", "#666666", "#999999", "#CCCCCC"])
    axe.bar_label(barres, fmt="%.2f", padding=3)
    axe.set_title("Ventes par région", fontsize=11)
    axe.set_ylabel("Millions d'unités")
    axe.set_xlabel("Région")
    axe.set_ylim(0, max(ventes) * 1.22 if max(ventes) else 1)
    axe.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)


def lancer_interface():
    """Construit la page Streamlit (sans exécuter de modèle)."""
    st.set_page_config(page_title="Ventes de jeux vidéo", page_icon="🎮", layout="wide")
    st.markdown("""
    <style>
      .stApp {background: #F7F7F7;}
      .block-container {max-width: 1250px; padding-top: 2rem;}
      div.stButton button, div.stFormSubmitButton button {
          background: #343434; color: white; border: 0;
      }
      div.stButton button:hover, div.stFormSubmitButton button:hover {
          background: #555555; color: white;
      }
    </style>
    """, unsafe_allow_html=True)

    st.title("Estimation des ventes de jeux vidéo")
    st.caption("Projet INF1007 · Ventes exprimées en millions d'exemplaires")

    try:
        jeux = charger_donnees()
    except FileNotFoundError:
        st.error("Fichier vgsales.csv introuvable à la racine du projet.")
        st.stop()

    gauche, droite = st.columns([1, 2], gap="large")
    with gauche:
        st.subheader("Caractéristiques du jeu")
        with st.form("jeu"):
            nom = st.text_input("Nom du jeu", placeholder="Ex. Mon nouveau jeu")
            plateforme = st.selectbox("Plateforme", sorted(jeux["Platform"].dropna().unique()))
            annee = st.number_input("Année de sortie", min_value=1980, max_value=2100, value=2026)
            genre = st.selectbox("Genre", sorted(jeux["Genre"].dropna().unique()))
            editeur = st.selectbox("Éditeur", sorted(jeux["Publisher"].dropna().unique()))
            envoyer = st.form_submit_button("Estimer les ventes", use_container_width=True)

        if envoyer:
            if not nom.strip():
                st.error("Veuillez saisir un nom de jeu.")
            else:
                st.info("Le formulaire est prêt. La fonction de prédiction reste à connecter.")
                # À connecter : predire(nom, plateforme, annee, genre, editeur)

        with st.expander("Historique des estimations"):
            st.caption("L'historique sera affiché ici lorsque la logique sera ajoutée.")

    with droite:
        st.subheader("Carte des ventes mondiales")
        st.caption("Données historiques du CSV — pas des prédictions")
        exemples = jeux.head(250)
        selection = st.selectbox(
            "Choisir un jeu existant",
            exemples.index,
            format_func=lambda i: f"{jeux.at[i, 'Name']} · {jeux.at[i, 'Platform']}",
        )
        ventes = [float(jeux.at[selection, colonne]) for colonne in COLONNES]
        for colonne, region, valeur in zip(st.columns(4), REGIONS, ventes):
            colonne.metric(region, f"{valeur:.2f} M")
        afficher_carte(ventes)
        st.caption("« Autres marchés » regroupe plusieurs territoires et n'a pas de point unique sur la carte.")
        afficher_graphique(ventes)

