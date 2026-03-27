import streamlit as st

from core.db import init_db
from core.styles import apply_global_styles
from core.tickets import seed_demo_data
from core.app_config_service import get_pages_config_map

# --------------------------------------------------
# ⚙️ Configuration générale de l'application
# --------------------------------------------------
st.set_page_config(
    page_title="Ticketing interne — Démo MVP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# 🗄️ Initialisation technique
# --------------------------------------------------
init_db()
seed_demo_data()

# --------------------------------------------------
# 🎨 Style global
# --------------------------------------------------
apply_global_styles()

# --------------------------------------------------
# 🧠 Initialisation session
# --------------------------------------------------
if "role" not in st.session_state:
    st.session_state.role = ""

if "current_user" not in st.session_state:
    st.session_state.current_user = "demo_user"

if "pending_page_key" not in st.session_state:
    st.session_state.pending_page_key = None

is_logged_in = bool(st.session_state.role)
is_simple_user = st.session_state.role == "Utilisateur"
is_backoffice = is_logged_in and not is_simple_user

pages_config = get_pages_config_map()

def cfg(page_key, default_label, default_icon, default_visible=True):
    page_cfg = pages_config.get(page_key, {})
    return {
        "label": page_cfg.get("label", default_label),
        "icon": page_cfg.get("icon", default_icon),
        "is_visible": bool(page_cfg.get("is_visible", default_visible)),
    }

# --------------------------------------------------
# 📄 Déclaration des pages
# --------------------------------------------------
page_login = st.Page(
    "pages/00_Login.py",
    title="Connexion",
    icon="🔐",
    default=True,
    visibility="visible",
)

home_cfg = cfg("home", "Accueil", "🏠", True)

page_home = st.Page(
    "pages/0_Accueil.py",
    title=home_cfg["label"],
    icon=home_cfg["icon"],
    visibility="visible" if (is_logged_in and home_cfg["is_visible"]) else "hidden",
)

page_create = st.Page(
    "pages/1_Creer_un_ticket.py",
    title="Créer un ticket",
    icon="➕",
    visibility="visible" if is_logged_in else "hidden",
)

page_my_tickets = st.Page(
    "pages/2_Mes_tickets.py",
    title="Mes tickets",
    icon="🎫",
    visibility="visible" if is_logged_in else "hidden",
)

page_queue = st.Page(
    "pages/3_File_de_tickets.py",
    title="File de tickets",
    icon="📋",
    visibility="visible" if is_backoffice else "hidden",
)

page_dashboard = st.Page(
    "pages/4_Pilotage.py",
    title="Pilotage",
    icon="📊",
    visibility="visible" if is_backoffice else "hidden",
)

page_admin = st.Page(
    "pages/5_Admin_Export.py",
    title="Admin / Export",
    icon="⚙️",
    visibility="visible" if is_backoffice else "hidden",
)

page_profile = st.Page(
    "pages/6_Profil.py",
    title="Profil",
    icon="👤",
    visibility="visible" if is_logged_in else "hidden",
)
# --------------------------------------------------
# 🗂️ Référentiel des pages par clé logique
# --------------------------------------------------
page_registry = {
    "login": page_login,
    "home": page_home,
    "create_ticket": page_create,
    "my_tickets": page_my_tickets,
    "ticket_queue": page_queue,
    "dashboard": page_dashboard,
    "admin_export": page_admin,
    "profile": page_profile,
}

# --------------------------------------------------
# 🧭 Navigation
# --------------------------------------------------
pages = {
    "": [page_login, page_home],
    "Espace utilisateur": [
        page_create,
        page_my_tickets,
        page_profile,
    ],
    "Opérationnel": [
        page_queue,
    ],
    "Pilotage & administration": [
        page_dashboard,
        page_admin,
    ],
}

pg = st.navigation(pages, position="top")

# --------------------------------------------------
# 🔀 Redirection différée
# --------------------------------------------------
if st.session_state.pending_page_key:
    target_key = st.session_state.pending_page_key
    st.session_state.pending_page_key = None

    if target_key in page_registry:
        st.switch_page(page_registry[target_key])

# --------------------------------------------------
# ▶️ Exécution de la page sélectionnée
# --------------------------------------------------
pg.run()