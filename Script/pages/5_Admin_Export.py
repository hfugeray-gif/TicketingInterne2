import os
import streamlit as st

from core.auth import require_backoffice_access, get_current_role, get_current_user, logout
from core.config import DB_PATH, UPLOAD_DIR
from core.styles import apply_global_styles, render_header
from core.tickets import export_csv, get_tickets


# --------------------------------------------------
# ⚙️ Configuration générale de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Admin / Export — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Vérifie que l'utilisateur est connecté ET autorisé à accéder au backoffice
require_backoffice_access()

# Applique le style global et l'en-tête
apply_global_styles()
render_header()




# --------------------------------------------------
# 📌 Titre de la page
# --------------------------------------------------
st.subheader("Administration légère")


# --------------------------------------------------
# 📥 Chargement des tickets
# --------------------------------------------------
df = get_tickets()


# --------------------------------------------------
# 📤 Export CSV
# --------------------------------------------------
st.markdown("### Export des données")

st.download_button(
    "Exporter les tickets en CSV",
    data=export_csv(df),
    file_name="tickets_export.csv",
    mime="text/csv",
)


# --------------------------------------------------
# ℹ️ Périmètre de la démo
# --------------------------------------------------
st.markdown("### Périmètre démo")

st.write("- Authentification simulée par sélection de rôle")
st.write("- Notifications simulées à l'écran")
st.write("- Base SQLite locale")
st.write("- Anti-doublon basé sur similarité simple + récence")
st.write("- Responsive correct pour une démo web, pas une app mobile native")


# --------------------------------------------------
# 🧹 Réinitialisation complète de la démo
# --------------------------------------------------
st.markdown("### Réinitialisation")

st.warning(
    "Cette action supprime la base SQLite locale ainsi que les fichiers uploadés. "
    "Elle est utile pour remettre la démonstration à zéro."
)

if st.button("Réinitialiser la base de démo"):
    # Suppression de la base SQLite si elle existe
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Suppression des fichiers uploadés
    for file in UPLOAD_DIR.glob("*"):
        try:
            file.unlink()
        except OSError:
            pass

    st.success("Base supprimée. Relancez l'application.")