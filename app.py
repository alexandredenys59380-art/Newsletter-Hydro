import streamlit as st
import pandas as pd
from datetime import date
from database import init_db, get_articles
from collector import collect_all

st.set_page_config(page_title="EDF Hydro Watch", page_icon="💧", layout="wide")
init_db()

st.title("💧 EDF Hydro Watch")
st.caption("Veille automatisée des actualités, publications et signaux concernant EDF Hydro.")

with st.sidebar:
    st.header("Collecte")
    if st.button("Lancer une collecte maintenant", use_container_width=True):
        with st.spinner("Recherche des nouvelles publications..."):
            count = collect_all()
        st.success(f"Collecte terminée : {count} nouvelle(s) publication(s).")
    st.divider()
    st.header("Filtres")
    search = st.text_input("Mot-clé", placeholder="ex. turbine, barrage, investissement")
    categories = [
        "Toutes", "Projets & investissements", "Maintenance & travaux",
        "Production & exploitation", "Environnement & biodiversité",
        "Réglementation & marché", "Entreprise & ressources humaines", "Autres"
    ]
    category = st.selectbox("Thématique", categories)
    start_date = st.date_input("Publié depuis", value=date(2020, 1, 1))

df = get_articles()
if df.empty:
    st.info("Aucune publication enregistrée. Lance une collecte depuis le menu à gauche.")
    st.stop()

df["published"] = pd.to_datetime(df["published"], errors="coerce").dt.date
filtered = df[df["published"].isna() | (df["published"] >= start_date)]
if search:
    mask = (
        filtered["title"].fillna("").str.contains(search, case=False) |
        filtered["summary"].fillna("").str.contains(search, case=False) |
        filtered["source"].fillna("").str.contains(search, case=False)
    )
    filtered = filtered[mask]
if category != "Toutes":
    filtered = filtered[filtered["category"] == category]

c1, c2, c3 = st.columns(3)
c1.metric("Publications archivées", len(df))
c2.metric("Résultats filtrés", len(filtered))
c3.metric("Sources suivies", df["source"].nunique())

st.subheader("Dernières publications")
for _, row in filtered.sort_values("published", ascending=False, na_position="last").iterrows():
    with st.container(border=True):
        left, right = st.columns([5, 1])
        with left:
            st.markdown(f"**{row['title']}**")
            st.caption(f"{row['source']} · {row['published'] or 'Date inconnue'} · {row['category']}")
            if row["summary"]:
                st.write(row["summary"][:700] + ("…" if len(row["summary"]) > 700 else ""))
            st.markdown(f"[Ouvrir la publication]({row['url']})")
        with right:
            st.write(" ")
            st.download_button(
                "Exporter cette fiche",
                data=(f"Titre: {row['title']}\nSource: {row['source']}\nDate: {row['published']}\nURL: {row['url']}\n\n{row['summary']}"),
                file_name="publication-edf-hydro.txt",
                mime="text/plain",
                key=f"download-{row['id']}"
            )

st.divider()
st.download_button(
    "Exporter les résultats en CSV",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="veille-edf-hydro.csv",
    mime="text/csv"
)
