SITES = [
    {"code": "SIEGE", "label": "Siège", "display_order": 1, "is_active": True},
    {"code": "H14", "label": "H14", "display_order": 2, "is_active": True},
    {"code": "PEX", "label": "PEX", "display_order": 3, "is_active": True},
    {"code": "P2A", "label": "P2A", "display_order": 4, "is_active": True},
    {"code": "PDC", "label": "PDC", "display_order": 5, "is_active": True},
    {"code": "3CM", "label": "3CM", "display_order": 6, "is_active": True},
]

SUBTYPES = {
    "Infra": [
        {"label": "Plomberie", "display_order": 1, "is_active": True},
        {"label": "Électricité", "display_order": 2, "is_active": True},
        {"label": "Climatisation", "display_order": 3, "is_active": True},
        {"label": "Mobilier", "display_order": 4, "is_active": True},
        {"label": "Serrurerie", "display_order": 5, "is_active": True},
        {"label": "Autre infra", "display_order": 6, "is_active": True},
    ],
    "Numérique": [
        {"label": "Logiciel", "display_order": 1, "is_active": True},
        {"label": "Réseau", "display_order": 2, "is_active": True},
        {"label": "Matériel", "display_order": 3, "is_active": True},
        {"label": "ERP", "display_order": 4, "is_active": True},
        {"label": "Messagerie", "display_order": 5, "is_active": True},
        {"label": "Téléphonie", "display_order": 6, "is_active": True},
        {"label": "Autre numérique", "display_order": 7, "is_active": True},
    ],
}

PAGES_CONFIG = [
    {"page_key": "login", "label": "Connexion", "icon": "🔐", "display_order": 1, "is_visible": True},
    {"page_key": "home", "label": "Accueil", "icon": "🏠", "display_order": 2, "is_visible": True},
    {"page_key": "create_ticket", "label": "Créer un ticket", "icon": "➕", "display_order": 3, "is_visible": True},
    {"page_key": "my_tickets", "label": "Mes tickets", "icon": "🎫", "display_order": 4, "is_visible": True},
    {"page_key": "ticket_queue", "label": "File de tickets", "icon": "📋", "display_order": 5, "is_visible": True},
    {"page_key": "dashboard", "label": "Pilotage", "icon": "📊", "display_order": 6, "is_visible": True},
    {"page_key": "admin_export", "label": "Admin / Export", "icon": "⚙️", "display_order": 7, "is_visible": True},
    {"page_key": "profile", "label": "Profil", "icon": "👤", "display_order": 8, "is_visible": True},
]


def get_sites():
    return sorted(SITES, key=lambda x: x["display_order"])


def get_subtypes(type_parent: str | None = None):
    if type_parent:
        return SUBTYPES.get(type_parent, [])
    return SUBTYPES


def get_pages_config():
    return sorted(PAGES_CONFIG, key=lambda x: x["display_order"])