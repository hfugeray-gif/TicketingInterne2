from difflib import SequenceMatcher

import pandas as pd
import streamlit as st

from core.api_tickets import api_create_ticket, api_get_tickets
from core.app_config_service import get_active_subtypes_by_type
from core.auth import ensure_logged_in, get_current_user
from core.config import SITES, TYPES
from core.styles import apply_global_styles, render_header

st.set_page_config(
    page_title="Créer un ticket — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_logged_in()
apply_global_styles()
render_header()

st.subheader("Création rapide")

if "create_titre" not in st.session_state:
    st.session_state.create_titre = ""

if "create_typage" not in st.session_state:
    st.session_state.create_typage = TYPES[0]

if "create_site" not in st.session_state:
    st.session_state.create_site = SITES[0]

if "create_subtype" not in st.session_state:
    st.session_state.create_subtype = ""

if "create_commentaire" not in st.session_state:
    st.session_state.create_commentaire = ""

if "reset_create_form" not in st.session_state:
    st.session_state.reset_create_form = False

if "create_success_message" not in st.session_state:
    st.session_state.create_success_message = None

if st.session_state.reset_create_form:
    st.session_state.create_titre = ""
    st.session_state.create_typage = TYPES[0]
    st.session_state.create_site = SITES[0]
    st.session_state.create_subtype = ""
    st.session_state.create_commentaire = ""
    st.session_state.reset_create_form = False

if st.session_state.create_success_message:
    st.success(st.session_state.create_success_message)
    st.session_state.create_success_message = None


def suggest_duplicates_api(titre: str, typage: str) -> pd.DataFrame:
    titre_normalise = titre.strip().lower()
    if not titre_normalise:
        return pd.DataFrame()

    try:
        tickets = api_get_tickets()
    except RuntimeError:
        return pd.DataFrame()

    matches = []
    for ticket in tickets:
        if ticket.get("typage") != typage:
            continue
        if ticket.get("statut") == "Clôturé":
            continue

        ratio = SequenceMatcher(
            None,
            titre_normalise,
            str(ticket.get("titre", "")).strip().lower(),
        ).ratio()

        if ratio >= 0.60:
            matches.append(
                {
                    "id": ticket.get("id"),
                    "titre": ticket.get("titre"),
                    "statut": ticket.get("statut"),
                    "site": ticket.get("site"),
                    "score": round(ratio, 2),
                }
            )

    if not matches:
        return pd.DataFrame()

    return pd.DataFrame(matches).sort_values(["score", "id"], ascending=[False, False])


titre = st.text_input("Titre *", key="create_titre")
typage = st.radio("Typage *", TYPES, horizontal=True, key="create_typage")
site = st.selectbox("Site *", SITES, key="create_site")

subtypes = get_active_subtypes_by_type(typage)
if subtypes:
    if st.session_state.create_subtype not in subtypes:
        st.session_state.create_subtype = subtypes[0]
    st.selectbox("Sous-type", subtypes, key="create_subtype")
else:
    st.session_state.create_subtype = ""

commentaire = st.text_area("Commentaire", key="create_commentaire")

st.file_uploader(
    "Photo",
    type=["png", "jpg", "jpeg"],
    help="Sur mobile, tu peux prendre une photo ou choisir une image existante.",
)

if titre:
    suggestions = suggest_duplicates_api(titre, typage)
    if not suggestions.empty:
        st.warning("Tickets potentiellement similaires détectés")
        st.dataframe(suggestions, use_container_width=True, hide_index=True)

if st.button("Créer le ticket", type="primary"):
    if not titre.strip():
        st.error("Le titre est obligatoire.")
    else:
        commentaire_payload = commentaire.strip()

        if st.session_state.create_subtype:
            prefix = f"Sous-type : {st.session_state.create_subtype}"
            commentaire_payload = (
                f"{prefix}\n\n{commentaire_payload}" if commentaire_payload else prefix
            )

        try:
            created_ticket = api_create_ticket(
                titre=titre.strip(),
                typage=typage,
                site=site,
                commentaire=commentaire_payload,
                demandeur=get_current_user(),
            )

            ticket_id = created_ticket["id"]
            st.session_state.create_success_message = (
                f"✅ Ticket #{ticket_id} créé avec succès."
            )
            st.session_state.reset_create_form = True
            st.rerun()

        except RuntimeError as e:
            st.error(str(e))