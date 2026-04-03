import streamlit as st

from core.auth import ensure_logged_in, get_current_user
from core.config import TYPES, SITES
from core.styles import apply_global_styles, render_header
from core.tickets import suggest_duplicates
from core.api_tickets import api_create_ticket

# --------------------------------------------------
# ⚙️ Configuration générale de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Créer un ticket — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Vérifie que l'utilisateur est bien passé par l'accueil
ensure_logged_in()

# Applique le style global et l'en-tête
apply_global_styles()
render_header()


# --------------------------------------------------
# 📝 Contenu principal : création de ticket
# --------------------------------------------------
st.subheader("Création rapide")

# --------------------------------------------------
# 🧠 Initialisation de l'état de session du formulaire
# --------------------------------------------------
if "create_titre" not in st.session_state:
    st.session_state.create_titre = ""

if "create_typage" not in st.session_state:
    st.session_state.create_typage = TYPES[0]

if "create_site" not in st.session_state:
    st.session_state.create_site = SITES[0]

if "create_commentaire" not in st.session_state:
    st.session_state.create_commentaire = ""

if "reset_create_form" not in st.session_state:
    st.session_state.reset_create_form = False

if "create_success_message" not in st.session_state:
    st.session_state.create_success_message = None

# --------------------------------------------------
# 🔄 Réinitialisation du formulaire au run suivant
# --------------------------------------------------
if st.session_state.reset_create_form:
    st.session_state.create_titre = ""
    st.session_state.create_typage = TYPES[0]
    st.session_state.create_site = SITES[0]
    st.session_state.create_commentaire = ""
    st.session_state.reset_create_form = False

# --------------------------------------------------
# ✅ Message de succès après création
# --------------------------------------------------
if st.session_state.create_success_message:
    st.success(st.session_state.create_success_message)
    st.session_state.create_success_message = None

# --------------------------------------------------
# 📋 Widgets du formulaire
# --------------------------------------------------
titre = st.text_input("Titre *", key="create_titre")
typage = st.radio("Typage *", TYPES, horizontal=True, key="create_typage")
site = st.selectbox("Site *", SITES, key="create_site")
commentaire = st.text_area("Commentaire", key="create_commentaire")

# --------------------------------------------------
# 📷 Ajout d'une image
# --------------------------------------------------
photo = st.file_uploader(
    "Photo",
    type=["png", "jpg", "jpeg"],
    help="Sur mobile, tu peux prendre une photo ou choisir une image existante.",
)

# --------------------------------------------------
# 🔎 Suggestion d'éventuels doublons
# --------------------------------------------------
if titre:
    suggestions = suggest_duplicates(titre, typage)
    if not suggestions.empty:
        st.warning("Tickets potentiellement similaires détectés")
        st.dataframe(suggestions, use_container_width=True)

# --------------------------------------------------
# ✅ Création du ticket
# --------------------------------------------------
if st.button("Créer le ticket", type="primary"):
    if not titre.strip():
        st.error("Le titre est obligatoire.")
    else:
        try:
            created_ticket = api_create_ticket(
                titre=titre.strip(),
                typage=typage,
                site=site,
                commentaire=commentaire.strip(),
                demandeur=get_current_user(),
            )

            ticket_id = created_ticket["id"]

            st.session_state.create_success_message = f"✅ Ticket #{ticket_id} créé avec succès."
            st.session_state.reset_create_form = True
            st.rerun()
        except RuntimeError as e:
            st.error(str(e))