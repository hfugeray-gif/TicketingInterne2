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

# Chemin vers la base SQLite
DB_PATH = ROOT_DIR / "tickets_demo.db"

# Dossier pour stocker les images uploadées
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)  # Créé automatiquement s’il n’existe pas

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



class Settings(BaseSettings):
    app_name: str = "Ticketing API"
    environment: str = "dev"
    debug: bool = True

    database_url: str = "sqlite:///./app.db"

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_use_tls: bool = False
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "ticketing@beam.local"

    app_base_url: str = "http://127.0.0.1:8501"
    emails_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
