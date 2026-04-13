import streamlit as st

from core.app_config_service import get_pages_config_map
from core.styles import apply_global_styles

st.set_page_config(
    page_title="Ticketing interne — Démo MVP",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()

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


def cfg(page_key, default_label, default_icon, default_visible=True, default_order=999):
    page_cfg = pages_config.get(page_key, {})
    return {
        "label": page_cfg.get("label", default_label),
        "icon": page_cfg.get("icon", default_icon),
        "is_visible": bool(page_cfg.get("is_visible", default_visible)),
        "display_order": int(page_cfg.get("display_order", default_order)),
    }


login_cfg = cfg("login", "Connexion", "🔐", True, 1)
home_cfg = cfg("home", "Accueil", "🏠", True, 2)
create_cfg = cfg("create_ticket", "Créer un ticket", "➕", True, 3)
my_tickets_cfg = cfg("my_tickets", "Mes tickets", "🎫", True, 4)
queue_cfg = cfg("ticket_queue", "File de tickets", "📋", True, 5)
dashboard_cfg = cfg("dashboard", "Pilotage", "📊", True, 6)
admin_cfg = cfg("admin_export", "Admin / Export", "⚙️", True, 7)
profile_cfg = cfg("profile", "Profil", "👤", True, 8)

page_login = st.Page(
    "pages/00_Login.py",
    title=login_cfg["label"],
    icon=login_cfg["icon"],
    default=True,
    visibility="visible" if login_cfg["is_visible"] else "hidden",
)

page_home = st.Page(
    "pages/0_Accueil.py",
    title=home_cfg["label"],
    icon=home_cfg["icon"],
    visibility="visible" if (is_logged_in and home_cfg["is_visible"]) else "hidden",
)

page_create = st.Page(
    "pages/1_Creer_un_ticket.py",
    title=create_cfg["label"],
    icon=create_cfg["icon"],
    visibility="visible" if (is_logged_in and create_cfg["is_visible"]) else "hidden",
)

page_my_tickets = st.Page(
    "pages/2_Mes_tickets.py",
    title=my_tickets_cfg["label"],
    icon=my_tickets_cfg["icon"],
    visibility="visible" if (is_logged_in and my_tickets_cfg["is_visible"]) else "hidden",
)

page_queue = st.Page(
    "pages/3_File_de_tickets.py",
    title=queue_cfg["label"],
    icon=queue_cfg["icon"],
    visibility="visible" if (is_backoffice and queue_cfg["is_visible"]) else "hidden",
)

page_dashboard = st.Page(
    "pages/4_Pilotage.py",
    title=dashboard_cfg["label"],
    icon=dashboard_cfg["icon"],
    visibility="visible" if (is_backoffice and dashboard_cfg["is_visible"]) else "hidden",
)

page_admin = st.Page(
    "pages/5_Admin_Export.py",
    title=admin_cfg["label"],
    icon=admin_cfg["icon"],
    visibility="visible" if (is_backoffice and admin_cfg["is_visible"]) else "hidden",
)

page_profile = st.Page(
    "pages/6_Profil.py",
    title=profile_cfg["label"],
    icon=profile_cfg["icon"],
    visibility="visible" if (is_logged_in and profile_cfg["is_visible"]) else "hidden",
)

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

page_meta = {
    "login": {"page": page_login, "section": "", "order": login_cfg["display_order"]},
    "home": {"page": page_home, "section": "", "order": home_cfg["display_order"]},
    "create_ticket": {
        "page": page_create,
        "section": "Espace utilisateur",
        "order": create_cfg["display_order"],
    },
    "my_tickets": {
        "page": page_my_tickets,
        "section": "Espace utilisateur",
        "order": my_tickets_cfg["display_order"],
    },
    "profile": {
        "page": page_profile,
        "section": "Espace utilisateur",
        "order": profile_cfg["display_order"],
    },
    "ticket_queue": {
        "page": page_queue,
        "section": "Opérationnel",
        "order": queue_cfg["display_order"],
    },
    "dashboard": {
        "page": page_dashboard,
        "section": "Pilotage & administration",
        "order": dashboard_cfg["display_order"],
    },
    "admin_export": {
        "page": page_admin,
        "section": "Pilotage & administration",
        "order": admin_cfg["display_order"],
    },
}

sections_order = ["", "Espace utilisateur", "Opérationnel", "Pilotage & administration"]

pages = {}
for section in sections_order:
    section_pages = [
        meta["page"]
        for _, meta in sorted(page_meta.items(), key=lambda item: item[1]["order"])
        if meta["section"] == section
    ]
    pages[section] = section_pages

pg = st.navigation(pages, position="top")

if st.session_state.pending_page_key:
    target_key = st.session_state.pending_page_key
    st.session_state.pending_page_key = None

    if target_key in page_registry:
        st.switch_page(page_registry[target_key])

pg.run()

