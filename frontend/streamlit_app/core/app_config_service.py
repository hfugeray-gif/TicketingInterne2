from core.api_config import (
    get_active_subtypes_by_type,
    get_pages_config,
    get_subtypes_config,
)

__all__ = [
    "get_pages_config",
    "get_pages_config_map",
    "get_subtypes_config",
    "get_active_subtypes_by_type",
]


DEFAULT_PAGES = {
    "login": {
        "label": "Connexion",
        "icon": "🔐",
        "display_order": 1,
        "is_visible": True,
    },
    "home": {
        "label": "Accueil",
        "icon": "🏠",
        "display_order": 2,
        "is_visible": True,
    },
    "create_ticket": {
        "label": "Créer un ticket",
        "icon": "➕",
        "display_order": 3,
        "is_visible": True,
    },
    "my_tickets": {
        "label": "Mes tickets",
        "icon": "🎫",
        "display_order": 4,
        "is_visible": True,
    },
    "ticket_queue": {
        "label": "File de tickets",
        "icon": "📋",
        "display_order": 5,
        "is_visible": True,
    },
    "dashboard": {
        "label": "Pilotage",
        "icon": "📊",
        "display_order": 6,
        "is_visible": True,
    },
    "admin_export": {
        "label": "Admin / Export",
        "icon": "⚙️",
        "display_order": 7,
        "is_visible": True,
    },
    "profile": {
        "label": "Profil",
        "icon": "👤",
        "display_order": 8,
        "is_visible": True,
    },
}


def get_pages_config_map() -> dict:
    try:
        df = get_pages_config()
    except Exception:
        return DEFAULT_PAGES.copy()

    if df.empty:
        return DEFAULT_PAGES.copy()

    result = DEFAULT_PAGES.copy()

    for _, row in df.iterrows():
        page_key = str(row["page_key"])
        result[page_key] = {
            "label": row.get("label", result.get(page_key, {}).get("label", "")),
            "icon": row.get("icon", result.get(page_key, {}).get("icon", "")),
            "display_order": int(
                row.get(
                    "display_order",
                    result.get(page_key, {}).get("display_order", 999),
                )
            ),
            "is_visible": bool(
                row.get(
                    "is_visible",
                    result.get(page_key, {}).get("is_visible", True),
                )
            ),
        }

    return result

