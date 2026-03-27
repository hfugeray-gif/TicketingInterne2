import pandas as pd

from core.db import get_conn


# --------------------------------------------------
# Sous-types
# --------------------------------------------------
def get_subtypes_config() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT id, type_parent, label, display_order, is_active
        FROM app_subtypes
        ORDER BY type_parent, display_order, label
        """,
        conn,
    )
    conn.close()
    return df


def get_active_subtypes_by_type(type_parent: str) -> list[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT label
        FROM app_subtypes
        WHERE type_parent = ? AND is_active = 1
        ORDER BY display_order, label
        """,
        (type_parent,),
    )
    rows = cur.fetchall()
    conn.close()
    return [row["label"] for row in rows]


def add_subtype(type_parent: str, label: str, display_order: int = 0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO app_subtypes (type_parent, label, display_order, is_active)
        VALUES (?, ?, ?, 1)
        """,
        (type_parent, label, display_order),
    )
    conn.commit()
    conn.close()


def update_subtype(subtype_id: int, label: str, display_order: int, is_active: bool):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE app_subtypes
        SET label = ?, display_order = ?, is_active = ?
        WHERE id = ?
        """,
        (label, display_order, 1 if is_active else 0, subtype_id),
    )
    conn.commit()
    conn.close()


def delete_subtype(subtype_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM app_subtypes WHERE id = ?", (subtype_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------
# Pages / navigation
# --------------------------------------------------
def get_pages_config() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT id, page_key, label, icon, display_order, is_visible
        FROM app_pages_config
        ORDER BY display_order, label
        """,
        conn,
    )
    conn.close()
    return df


def update_page_config(page_id: int, label: str, icon: str, display_order: int, is_visible: bool):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE app_pages_config
        SET label = ?, icon = ?, display_order = ?, is_visible = ?
        WHERE id = ?
        """,
        (label, icon, display_order, 1 if is_visible else 0, page_id),
    )
    conn.commit()
    conn.close()


def get_pages_config_map() -> dict:
    """
    Retourne la config des pages sous forme de dictionnaire indexé par page_key.
    """
    df = get_pages_config()
    if df.empty:
        return {}

    result = {}
    for _, row in df.iterrows():
        result[row["page_key"]] = {
            "label": row["label"],
            "icon": row["icon"],
            "display_order": int(row["display_order"]),
            "is_visible": bool(row["is_visible"]),
        }
    return result