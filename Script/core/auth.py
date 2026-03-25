import streamlit as st


def ensure_logged_in():
    """
    Vérifie qu'un rôle et un utilisateur simulés sont bien définis en session.
    """
    if "role" not in st.session_state or not st.session_state.role:
        st.session_state.pending_page_key = "login"
        st.rerun()

    if "current_user" not in st.session_state or not st.session_state.current_user:
        st.session_state.pending_page_key = "login"
        st.rerun()


def get_current_role():
    """Retourne le rôle simulé courant."""
    return st.session_state.get("role", "")


def get_current_user():
    """Retourne l'identifiant utilisateur simulé courant."""
    return st.session_state.get("current_user", "demo_user")


def is_simple_user():
    """
    Retourne True si le profil courant est un utilisateur standard.
    """
    return get_current_role() == "Utilisateur"


def can_access_backoffice():
    """
    Retourne True si le profil peut accéder aux pages backoffice.
    """
    return not is_simple_user()


def require_backoffice_access():
    """
    Bloque l'accès à une page si le profil n'a pas les droits backoffice.
    """
    ensure_logged_in()

    if not can_access_backoffice():
        st.warning("Accès réservé aux profils internes de traitement.")
        st.stop()


def logout():
    """
    Réinitialise la session utilisateur simulée.

    On conserve volontairement `pending_page_key` pour permettre
    une redirection propre vers l'accueil après logout.
    """
    keys_to_remove = [
        "role",
        "current_user",
        "selected_ticket_id",
        "selected_my_ticket_id",
        "create_titre",
        "create_typage",
        "create_commentaire",
        "reset_create_form",
    ]

    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]