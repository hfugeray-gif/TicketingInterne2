import streamlit as st

from core.auth import logout
from core.config import ROLES
from core.styles import apply_global_styles, render_header



# --------------------------------------------------
# 🎨 Habillage global
# --------------------------------------------------
apply_global_styles()
render_header()

# --------------------------------------------------
# 🧠 Initialisation de la session simulée
# --------------------------------------------------
if "role" not in st.session_state:
    st.session_state.role = ""

if "current_user" not in st.session_state:
    st.session_state.current_user = "demo_user"

# --------------------------------------------------
# 🏠 Contenu de la page d'accueil
# --------------------------------------------------
st.markdown("## Accueil")
st.write(
    "Choisis un profil simulé pour entrer dans l'application "
    "et tester les différents parcours."
)

# --------------------------------------------------
# 🧾 Formulaire de simulation de profil
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    default_role_index = (
        ROLES.index(st.session_state.role)
        if st.session_state.role in ROLES
        else 0
    )

    selected_role = st.selectbox(
        "Rôle simulé",
        ROLES,
        index=default_role_index,
    )

with col2:
    selected_user = st.text_input(
        "Nom / identifiant",
        value=st.session_state.current_user,
    )

# --------------------------------------------------
# 🚪 Actions
# --------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    if st.button("Entrer dans l'application", type="primary", use_container_width=True):
        st.session_state.role = selected_role
        st.session_state.current_user = selected_user.strip() or "demo_user"

        # On stocke une clé logique, pas un chemin de fichier
        st.session_state.pending_page_key = "home"
        st.rerun()

with col_b:
    if st.button("Réinitialiser la session simulée", use_container_width=True):
        logout()
        st.session_state.current_user = "demo_user"
        st.rerun()
# --------------------------------------------------
# ℹ️ Explication des profils
# --------------------------------------------------
st.markdown("---")
st.markdown("### Profils disponibles")

st.write(
    """
- **Utilisateur** : peut créer un ticket et consulter ses propres tickets.
- **Dispatcheur DIO / DSN** : accès à la file de tickets et au traitement.
- **Technicien** : accès au suivi opérationnel.
- **Admin** : accès complet.
- **Supervision** : accès aux vues de pilotage et supervision.
"""
)

st.info(
    "L'authentification est volontairement simulée pour cette démonstration. "
    "Une intégration SSO pourra être ajoutée ultérieurement."
)