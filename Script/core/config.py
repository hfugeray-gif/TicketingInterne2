from pathlib import Path

# -----------------------------
# 📁 Gestion des chemins projet
# -----------------------------

# Dossier /Script
BASE_DIR = Path(__file__).resolve().parent.parent

# Racine du projet (au-dessus de /Script)
ROOT_DIR = BASE_DIR.parent

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

# -----------------------------
# 📊 Constantes métier
# -----------------------------

# Statuts possibles d’un ticket
STATUTS = ["Ouvert", "En cours", "Clôturé", "Doublon"]

# Niveaux de priorité
PRIORITES = ["Basse", "Normale", "Haute"]

# Types de tickets
TYPES = ["Infra", "Numérique"]

# Rôles simulés dans l’application
ROLES = [
    "Utilisateur",        # accès limité
    "Dispatcheur DIO",
    "Dispatcheur DSN",
    "Technicien",
    "Admin",
    "Supervision",
]