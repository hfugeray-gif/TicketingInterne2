import streamlit as st

from core.auth import ensure_logged_in, get_current_role, get_current_user, logout
from core.styles import apply_global_styles, render_header
from core.api_client import api_get

me = api_get("/me")

# --------------------------------------------------
# ⚙️ Configuration de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Profil — Ticketing interne",
    layout="wide",
    initial_sidebar_state="collapsed",
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
# 🎨 Styles spécifiques
# --------------------------------------------------
st.markdown(
    """
    <style>
        .profile-card {
            background: rgba(255,255,255,0.82);
            border: 1px solid #d9e2f2;
            border-radius: 18px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 22px rgba(0,0,0,0.04);
        }

        .profile-card h2 {
            margin: 0 0 10px 0;
            color: #12344d;
            font-size: 1.5rem;
        }

        .profile-card p {
            margin: 0;
            color: #5f6c7b;
        }

        .profile-section-title {
            color: #12344d;
            font-size: 1.15rem;
            font-weight: 800;
            margin-bottom: 12px;
        }

        .profile-info-grid {
            display: grid;
            grid-template-columns: 220px 1fr;
            gap: 10px 16px;
        }

        .profile-label {
            color: #5f6c7b;
            font-weight: 600;
        }

        .profile-value {
            color: #12344d;
        }

        .profile-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(0, 64, 52, 0.08);
            color: #004034;
            border: 1px solid rgba(0, 64, 52, 0.16);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .profile-note {
            background: rgba(255,255,255,0.70);
            border: 1px solid #d9e2f2;
            border-radius: 16px;
            padding: 16px 18px;
            color: #5f6c7b;
        }

        @media (max-width: 800px) {
            .profile-info-grid {
                grid-template-columns: 1fr;
                gap: 8px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 👤 Données de profil simulées
# --------------------------------------------------
role = get_current_role()
current_user = get_current_user()

# Ces champs pourront être remplacés plus tard par le SSO
email = f"{current_user}@beam.local"
service = "Support interne"
entite = "Bordeaux Events And More"
mode_auth = "SSO simulé"
permissions = {
    "Utilisateur": "Création et consultation de ses tickets",
    "Dispatcheur DIO": "Création, consultation et traitement de la file",
    "Dispatcheur DSN": "Création, consultation et traitement de la file",
    "Technicien": "Suivi opérationnel et traitement",
    "Admin": "Accès complet à l’ensemble des vues",
    "Supervision": "Accès pilotage et supervision",
}.get(role, "Accès non défini")

# --------------------------------------------------
# 🧾 En-tête
# --------------------------------------------------
st.markdown(
    f"""
    <div class="profile-card">
        <h2>Profil utilisateur</h2>
        <p>Informations générales du compte connecté et périmètre d’accès actuel.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# ℹ️ Informations générales
# --------------------------------------------------
st.markdown('<div class="profile-section-title">Informations du profil</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="profile-card">
        <div class="profile-info-grid">
            <div class="profile-label">Identifiant</div>
            <div class="profile-value">{current_user}</div>

            <div class="profile-label">Rôle</div>
            <div class="profile-value"><span class="profile-badge">{role}</span></div>

            <div class="profile-label">Email</div>
            <div class="profile-value">{email}</div>

            <div class="profile-label">Service</div>
            <div class="profile-value">{service}</div>

            <div class="profile-label">Entité</div>
            <div class="profile-value">{entite}</div>

            <div class="profile-label">Mode d’authentification</div>
            <div class="profile-value">{mode_auth}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 🔐 Accès / permissions
# --------------------------------------------------
st.markdown('<div class="profile-section-title">Périmètre d’accès</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="profile-card">
        <div class="profile-info-grid">
            <div class="profile-label">Permissions actuelles</div>
            <div class="profile-value">{permissions}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 📝 Note SSO future
# --------------------------------------------------
st.markdown(
    """
    <div class="profile-note">
        Cette page est prévue pour recevoir ultérieurement les informations issues du SSO :
        nom complet, email réel, entité, service, groupe de sécurité, rôle métier, et autres
        attributs d’identité transmis par l’authentification d’entreprise.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("Revenir à l’accueil", use_container_width=True):
        st.session_state.pending_page_key = "home"
        st.rerun()

with col2:
    if st.button("Se déconnecter", use_container_width=True):
        logout()
        st.session_state.pending_page_key = "login"
        st.rerun()