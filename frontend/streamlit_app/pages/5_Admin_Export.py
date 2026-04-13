import pandas as pd
import streamlit as st

from core.api_tickets import api_get_comments, api_get_journal, api_get_tickets
from core.app_config_service import get_pages_config, get_subtypes_config
from core.auth import require_backoffice_access
from core.styles import apply_global_styles, render_header

st.set_page_config(
    page_title="Administration — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_backoffice_access()
apply_global_styles()
render_header()

st.subheader("Administration")


@st.cache_data(ttl=30)
def load_tickets_df() -> pd.DataFrame:
    return pd.DataFrame(api_get_tickets())


@st.cache_data(ttl=30)
def load_comments_df(ticket_ids: tuple[int, ...]) -> pd.DataFrame:
    rows = []
    for ticket_id in ticket_ids:
        try:
            comments = api_get_comments(ticket_id)
        except RuntimeError:
            continue

        for item in comments:
            item = dict(item)
            item["ticket_id"] = ticket_id
            rows.append(item)

    return pd.DataFrame(rows)


@st.cache_data(ttl=30)
def load_journal_df(ticket_ids: tuple[int, ...]) -> pd.DataFrame:
    rows = []
    for ticket_id in ticket_ids:
        try:
            journal_entries = api_get_journal(ticket_id)
        except RuntimeError:
            continue

        for item in journal_entries:
            item = dict(item)
            item["ticket_id"] = ticket_id
            rows.append(item)

    return pd.DataFrame(rows)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    if df.empty:
        return b""
    return df.to_csv(index=False).encode("utf-8-sig")


try:
    tickets_df = load_tickets_df()
except RuntimeError as e:
    st.error(f"Impossible de charger les données : {e}")
    st.stop()

if tickets_df.empty:
    st.info("Aucun ticket disponible.")
    st.stop()

if "ticket_maitre_id" in tickets_df.columns:
    tickets_df["statut_affiche"] = tickets_df["statut"]
    tickets_df.loc[tickets_df["ticket_maitre_id"].notna(), "statut_affiche"] = "Doublon"
else:
    tickets_df["statut_affiche"] = tickets_df.get("statut", "")

if "created_at" in tickets_df.columns:
    tickets_df["created_at"] = pd.to_datetime(tickets_df["created_at"], errors="coerce")

st.caption(
    "Cette version admin n'utilise plus SQLite local. "
    "Les exports sont construits depuis l'API backend."
)

tab_db, tab_param = st.tabs(["Données", "Paramétrage"])

with tab_db:
    source = st.selectbox("Source", ["tickets", "commentaires", "journal"])

    if source == "tickets":
        df = tickets_df.copy()
    else:
        ticket_ids = tuple(int(x) for x in tickets_df["id"].dropna().tolist())
        if source == "commentaires":
            df = load_comments_df(ticket_ids)
        else:
            df = load_journal_df(ticket_ids)

    if df.empty:
        st.info("Aucune donnée disponible pour cette source.")
    else:
        filtres = st.columns(3)

        with filtres[0]:
            ticket_filter = st.text_input("Ticket ID") if "ticket_id" in df.columns else ""

        with filtres[1]:
            auteur_filter = st.text_input("Auteur") if "auteur" in df.columns else ""

        with filtres[2]:
            text_filter = st.text_input("Recherche texte")

        filtered_df = df.copy()

        if ticket_filter and "ticket_id" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["ticket_id"].astype(str) == ticket_filter.strip()
            ]

        if auteur_filter and "auteur" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["auteur"].astype(str).str.contains(
                    auteur_filter.strip(),
                    case=False,
                    na=False,
                )
            ]

        if text_filter:
            mask = pd.Series(False, index=filtered_df.index)
            for col in filtered_df.columns:
                mask = mask | filtered_df[col].astype(str).str.contains(
                    text_filter,
                    case=False,
                    na=False,
                )
            filtered_df = filtered_df[mask]

        selected_columns = st.multiselect(
            "Colonnes à afficher",
            list(filtered_df.columns),
            default=list(filtered_df.columns[: min(8, len(filtered_df.columns))]),
        )

        displayed_df = filtered_df[selected_columns] if selected_columns else filtered_df

        st.dataframe(displayed_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Exporter en CSV",
            data=to_csv_bytes(filtered_df),
            file_name=f"{source}_export.csv",
            mime="text/csv",
        )

with tab_param:
    subtab_ref, subtab_nav = st.tabs(["Référentiels", "Navigation"])

    with subtab_ref:
        st.markdown("### Sous-types disponibles")
        st.caption(
            "Lecture seule tant que les endpoints d'édition backend "
            "ne sont pas implémentés."
        )
        subtypes_df = get_subtypes_config()

        if subtypes_df.empty:
            st.info("Aucun sous-type disponible.")
        else:
            st.dataframe(subtypes_df, use_container_width=True, hide_index=True)

    with subtab_nav:
        st.markdown("### Configuration des pages")
        st.caption(
            "Lecture seule tant que les endpoints d'édition backend "
            "ne sont pas implémentés."
        )
        pages_df = get_pages_config()

        if pages_df.empty:
            st.info("Aucune configuration disponible.")
        else:
            st.dataframe(pages_df, use_container_width=True, hide_index=True)