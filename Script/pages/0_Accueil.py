import streamlit as st

from core.auth import ensure_logged_in, get_current_role, get_current_user, logout
from core.styles import apply_global_styles, render_header


# --------------------------------------------------
# ⚙️ Configuration de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Accueil — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# 🔐 Vérification session
# --------------------------------------------------
ensure_logged_in()

# --------------------------------------------------
# 🎨 Habillage global
# --------------------------------------------------
apply_global_styles()
render_header()

# --------------------------------------------------
# 🎨 Styles spécifiques à la home
# --------------------------------------------------
st.markdown(
    """
    <style>
        .home-welcome {
            background: rgba(255,255,255,0.62);
            border: 1px solid #d9e2f2;
            border-radius: 18px;
            padding: 20px 22px;
            margin-bottom: 22px;
            backdrop-filter: blur(6px);
        }

        .home-welcome h2 {
            margin: 0 0 8px 0;
            color: #12344d;
            font-size: 1.8rem;
        }

        .home-welcome p {
            margin: 0;
            color: #486581;
            font-size: 1rem;
        }

        .role-badge {
            display: inline-block;
            margin-top: 12px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(15,76,129,0.08);
            color: #0f4c81;
            border: 1px solid rgba(15,76,129,0.12);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .section-title {
            margin-top: 10px;
            margin-bottom: 14px;
            color: #12344d;
            font-size: 1.25rem;
            font-weight: 800;
        }

        .nav-card {
            background: rgba(255,255,255,0.78);
            border: 1px solid #d9e2f2;
            border-radius: 18px;
            padding: 18px 18px 14px 18px;
            min-height: 185px;
            box-shadow: 0 8px 22px rgba(15,76,129,0.06);
            margin-bottom: 10px;
        }

        .nav-card-title {
            color: #12344d;
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .nav-card-text {
            color: #486581;
            font-size: 0.95rem;
            line-height: 1.45;
            min-height: 58px;
            margin-bottom: 14px;
        }

        .nav-card-tag {
            display: inline-block;
            font-size: 0.76rem;
            font-weight: 700;
            color: #0f4c81;
            background: rgba(15,76,129,0.08);
            border: 1px solid rgba(15,76,129,0.10);
            border-radius: 999px;
            padding: 4px 9px;
            margin-bottom: 10px;
        }

        .demo-box {
            background: rgba(255,255,255,0.55);
            border: 1px solid #d9e2f2;
            border-radius: 16px;
            padding: 16px 18px;
            margin-top: 10px;
        }

        .demo-box strong {
            color: #12344d;
        }

        @media (max-width: 900px) {
            .nav-card {
                min-height: auto;
            }

            .nav-card-text {
                min-height: auto;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 👤 Contexte utilisateur
# --------------------------------------------------
role = get_current_role()
current_user = get_current_user()


# --------------------------------------------------
# 🏠 Bandeau de bienvenue
# --------------------------------------------------
st.markdown(
    f"""
    <div class="home-welcome">
        <h2>Bienvenue dans le portail support</h2>
        <p>
            Accède rapidement aux parcours disponibles selon ton profil
            et démarre la démonstration depuis un point d’entrée clair.
        </p>
        <div class="role-badge">Connecté en tant que : {role} — {current_user}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Accès rapides</div>', unsafe_allow_html=True)


# --------------------------------------------------
# 🧭 Helpers navigation
# --------------------------------------------------
def go_to(page_key: str):
    st.session_state.pending_page_key = page_key
    st.rerun()


def render_nav_card(title: str, text: str, page_key: str, tag: str):
    st.markdown(
        f"""
        <div class="nav-card">
            <div class="nav-card-tag">{tag}</div>
            <div class="nav-card-title">{title}</div>
            <div class="nav-card-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Accéder à {title}", key=f"btn_{page_key}", use_container_width=True):
        go_to(page_key)


# --------------------------------------------------
# 🗂️ Définition des cartes selon rôle
# --------------------------------------------------
cards = [
    {
        "title": "Créer un ticket",
        "text": "Déclarer un incident ou une demande interne en quelques étapes.",
        "page_key": "create_ticket",
        "tag": "Action",
        "roles": ["Utilisateur", "Dispatcheur DIO", "Dispatcheur DSN", "Technicien", "Admin", "Supervision"],
    },
    {
        "title": "Mes tickets",
        "text": "Consulter les demandes liées à ton profil, suivre leur statut et commenter.",
        "page_key": "my_tickets",
        "tag": "Suivi",
        "roles": ["Utilisateur", "Dispatcheur DIO", "Dispatcheur DSN", "Technicien", "Admin", "Supervision"],
    },
    {
        "title": "File de tickets",
        "text": "Traiter, affecter et mettre à jour les tickets dans la vue opérationnelle.",
        "page_key": "ticket_queue",
        "tag": "Opérationnel",
        "roles": ["Dispatcheur DIO", "Dispatcheur DSN", "Technicien", "Admin", "Supervision"],
    },
    {
        "title": "Pilotage",
        "text": "Suivre les KPI, le backlog, les tendances et les points d’attention.",
        "page_key": "pilotage",
        "tag": "Vision",
        "roles": ["Admin", "Supervision"],
    },
    {
        "title": "Administration / Export",
        "text": "Exporter les données de démo et administrer l’environnement simulé.",
        "page_key": "admin_export",
        "tag": "Admin",
        "roles": ["Admin"],
    },
]

visible_cards = [card for card in cards if role in card["roles"]]

# --------------------------------------------------
# 🧱 Affichage en grille
# --------------------------------------------------
if not visible_cards:
    st.warning("Aucun accès rapide n’est défini pour ce rôle.")
else:
    for i in range(0, len(visible_cards), 3):
        row_cards = visible_cards[i:i+3]
        cols = st.columns(len(row_cards))

        for col, card in zip(cols, row_cards):
            with col:
                render_nav_card(
                    title=card["title"],
                    text=card["text"],
                    page_key=card["page_key"],
                    tag=card["tag"],
                )

# --------------------------------------------------
# ℹ️ Bloc de contexte
# --------------------------------------------------
st.markdown(
    """
    <div class="demo-box">
        <strong>Périmètre de cette démonstration</strong><br>
        L’authentification reste simulée, mais le parcours applicatif reproduit
        le comportement attendu d’un portail interne : connexion, accueil,
        accès ciblés selon le rôle, puis navigation vers les pages métier.
    </div>
    """,
    unsafe_allow_html=True,
)