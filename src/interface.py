import os

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st

from src import historique
from src.exceptions import DonneeInvalideError
from src.predicteur import Modele
from src.variables import VariableCategorielle

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_HISTORIQUE = os.path.join(RACINE, "historique.csv")
REGIONS = ["Amérique du Nord", "Europe", "Japon", "Autres marchés"]
LIBELLES = {"Platform": "Plateforme", "Year": "Année de sortie",
            "Genre": "Genre", "Publisher": "Éditeur"}


@st.cache_resource
def charger_modele() -> Modele:
    return Modele(os.path.join(RACINE, "modeles"))


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
        hovertext=[f"{r} : {v:.2f} millions"
                   for r, v in zip(REGIONS[:3], ventes[:3])],
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
                          showarrow=False, bgcolor="white",
                          bordercolor="#CCCCCC", borderpad=7,
                          xanchor="right")],
    )
    st.plotly_chart(carte, use_container_width=True,
                    config={"scrollZoom": True, "displayModeBar": False})


def afficher_graphique(ventes):
    """Affiche un graphique Matplotlib des quatre zones."""
    figure, axe = plt.subplots(figsize=(7, 2.7))
    barres = axe.bar(REGIONS, ventes,
                     color=["#333333", "#666666", "#999999", "#CCCCCC"])
    axe.bar_label(barres, fmt="%.2f", padding=3)
    axe.set_title("Ventes estimées par région", fontsize=11)
    axe.set_ylabel("Millions d'unités")
    axe.set_xlabel("Région")
    axe.set_ylim(0, max(ventes) * 1.22 if max(ventes) else 1)
    axe.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)


def lancer_interface():
    """Construit la page Streamlit."""
    st.set_page_config(page_title="Ventes de jeux vidéo", page_icon="🎮",
                       layout="wide")
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
        modele = charger_modele()
    except DonneeInvalideError as erreur:
        st.error(f"{erreur}. Lancez d'abord : python -m src.entrainement")
        st.stop()

    gauche, droite = st.columns([1, 2], gap="large")
    with gauche:
        st.subheader("Caractéristiques du jeu")
        with st.form("jeu"):
            nom = st.text_input("Nom du jeu", placeholder="Ex. Mon nouveau jeu")
            saisies = {}
            for variable in modele.variables:
                libelle = LIBELLES.get(variable.nom, variable.nom)
                if isinstance(variable, VariableCategorielle):
                    saisies[variable.nom] = st.selectbox(libelle,
                                                         variable.valeurs)
                else:
                    saisies[variable.nom] = st.text_input(
                        libelle,
                        placeholder=f"Entre {variable.minimum:g} "
                                    f"et {variable.maximum:g}")
            envoyer = st.form_submit_button("Estimer les ventes",
                                            use_container_width=True)

        if envoyer:
            if not nom.strip():
                st.error("Veuillez saisir un nom de jeu.")
            else:
                try:
                    resultat = modele.predire(saisies)
                    historique.ajouter(CHEMIN_HISTORIQUE, nom.strip(),
                                       saisies, resultat)
                    st.session_state["dernier"] = (nom.strip(), resultat)
                except DonneeInvalideError as erreur:
                    st.error(str(erreur))

        with st.expander("Historique des estimations"):
            lignes = historique.lire(CHEMIN_HISTORIQUE)
            if lignes:
                st.dataframe(lignes, use_container_width=True)
            else:
                st.caption("Aucune estimation pour l'instant.")

    with droite:
        st.subheader("Résultat de l'estimation")
        if "dernier" not in st.session_state:
            st.info("Remplissez le formulaire puis cliquez sur « Estimer ».")
        else:
            nom_jeu, resultat = st.session_state["dernier"]
            ventes = list(resultat.values())
            st.write(f"**Jeu analysé :** {nom_jeu}")
            for colonne, region, valeur in zip(st.columns(4), REGIONS, ventes):
                colonne.metric(region, f"{valeur:.2f} M")
            afficher_carte(ventes)
            afficher_graphique(ventes)
        metrique = modele.metrique
        st.caption(
            "Outil pédagogique : estimation moyenne selon plateforme, genre "
            "et éditeur. Il sous-estime les très gros succès "
            f"(R² = {metrique['valeur']:.2f} contre {metrique['reference']:.2f} "
            "pour la référence).")