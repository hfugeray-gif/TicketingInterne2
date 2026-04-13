from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
# -----------------------------
# 📁 Gestion des chemins projet
# -----------------------------

# Dossier /Script
BASE_DIR = Path(__file__).resolve().parent.parent

# Racine du projet (au-dessus de /Script)
ROOT_DIR = BASE_DIR.parent

#URL de l'app
APP_BASE_URL = "http://localhost:8501"

# -----------------------------
# 🗄️ Base de données & uploads
# -----------------------------

# -----------------------------
# 🖼️ Assets (logo, etc.)
# -----------------------------

# Chemin vers le logo de l'application
HEADER_BANNER_PATH = BASE_DIR / "assets" / "header_banner.jpg"
LOGO_MENU_PATH = BASE_DIR / "assets" / "logo_menu.png"

# -----------------------------
# 📊 Constantes métier
# -----------------------------

# Statuts possibles d’un ticket
STATUTS = ["Ouvert", "En cours", "Clôturé"]

# Niveaux de priorité
PRIORITES = ["Basse", "Normale", "Haute"]

# Types de tickets
TYPES = ["Infra", "Numérique"]

# Types de sites
SITES = ["Siège", "H14", "PEX", "P2A", "PDC", "3CM"]

# Rôles simulés dans l’application
ROLES = [
    "Utilisateur",        # accès limité
    "Dispatcheur DIO",
    "Dispatcheur DSN",
    "Technicien",
    "Admin",
    "Supervision",
]

# --------------------------------------------------
# 📧 Configuration email
# --------------------------------------------------
SMTP_HOST = "10.55.5.4"
SMTP_PORT = 25
SMTP_FROM = "h.fugeray@beam.fr"

# Serveur de test sans auth
SMTP_USE_TLS = False
SMTP_USE_AUTH = False

DEMO_EMAIL = "h.fugeray@beam.fr"

DISPATCH_EMAILS = {
    "Infra": DEMO_EMAIL,
    "Numérique": DEMO_EMAIL,
}

TECH_EMAILS = {
    "tech_infra_1": DEMO_EMAIL,
    "tech_infra_2": DEMO_EMAIL,
    "tech_app_1": DEMO_EMAIL,
    "demo_user": DEMO_EMAIL,
}



