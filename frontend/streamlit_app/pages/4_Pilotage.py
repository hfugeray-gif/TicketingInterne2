import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_tickets import api_get_tickets
from core.auth import require_backoffice_access
from core.styles import apply_global_styles, render_header

st.set_page_config(
    page_title="Pilotage — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_backoffice_access()
apply_global_styles()
render_header()

st.subheader("Pilotage")


@st.cache_data(ttl=30)
def load_tickets_df() -> pd.DataFrame:
    tickets = api_get_tickets()
    df = pd.DataFrame(tickets)

    if df.empty:
        return df

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    if "updated_at" in df.columns:
        df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    df["is_duplicate_child"] = (
        df.get("ticket_maitre_id").notna()
        if "ticket_maitre_id" in df.columns
        else False
    )

    df["statut_affiche"] = df["statut"]
    df.loc[df["is_duplicate_child"], "statut_affiche"] = "Doublon"

    return df


try:
    df = load_tickets_df()
except RuntimeError as e:
    st.error(f"Impossible de charger les données : {e}")
    st.stop()

if df.empty:
    st.info("Aucun ticket à afficher.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tickets totaux", int(len(df)))
col2.metric("Ouverts", int((df["statut"] == "Ouvert").sum()))
col3.metric("En cours", int((df["statut"] == "En cours").sum()))
col4.metric("Doublons", int(df["is_duplicate_child"].sum()))

st.markdown("### Répartition par statut")
statut_counts = (
    df["statut_affiche"]
    .fillna("Inconnu")
    .value_counts()
    .rename_axis("statut")
    .reset_index(name="count")
)
fig_status = px.bar(statut_counts, x="statut", y="count")
st.plotly_chart(fig_status, use_container_width=True)

left, right = st.columns(2)

with left:
    st.markdown("### Répartition par type")
    type_counts = (
        df["typage"]
        .fillna("Non renseigné")
        .value_counts()
        .rename_axis("typage")
        .reset_index(name="count")
    )
    fig_type = px.pie(type_counts, names="typage", values="count")
    st.plotly_chart(fig_type, use_container_width=True)

with right:
    st.markdown("### Répartition par site")
    if "site" in df.columns:
        site_counts = (
            df["site"]
            .fillna("Non renseigné")
            .value_counts()
            .rename_axis("site")
            .reset_index(name="count")
        )
        fig_site = px.bar(site_counts, x="site", y="count")
        st.plotly_chart(fig_site, use_container_width=True)
    else:
        st.info("Le champ site n'est pas disponible dans les données API.")

if "created_at" in df.columns:
    st.markdown("### Tickets créés par jour")
    by_day = (
        df.dropna(subset=["created_at"])
        .assign(jour=lambda x: x["created_at"].dt.date)
        .groupby("jour", as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    if not by_day.empty:
        fig_day = px.line(by_day, x="jour", y="count", markers=True)
        st.plotly_chart(fig_day, use_container_width=True)

st.markdown("### Derniers tickets")
columns = [
    c
    for c in [
        "id",
        "titre",
        "typage",
        "site",
        "statut_affiche",
        "demandeur",
        "assigne_a",
        "created_at",
    ]
    if c in df.columns
]

sort_column = "created_at" if "created_at" in df.columns else "id"

st.dataframe(
    df.sort_values(sort_column, ascending=False, na_position="last")[columns],
    use_container_width=True,
    hide_index=True,
)