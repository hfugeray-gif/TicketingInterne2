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

def subtype_exists(type_parent: str, label: str, exclude_id: int | None = None) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        SELECT COUNT(*) AS cnt
        FROM app_subtypes
        WHERE type_parent = ?
          AND LOWER(TRIM(label)) = LOWER(TRIM(?))
    """
    params = [type_parent, label]

    if exclude_id is not None:
        sql += " AND id <> ?"
        params.append(exclude_id)

    cur.execute(sql, params)
    row = cur.fetchone()
    conn.close()
    return row["cnt"] > 0

def add_subtype(type_parent: str, label: str, display_order: int = 0):
    clean_label = label.strip()

    if not clean_label:
        raise ValueError("Le libellé du sous-type est obligatoire.")

    if subtype_exists(type_parent, clean_label):
        raise ValueError("Ce sous-type existe déjà pour ce type.")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO app_subtypes (type_parent, label, display_order, is_active)
        VALUES (?, ?, ?, 1)
        """,
        (type_parent, clean_label, display_order),
    )
    conn.commit()
    conn.close()


def update_subtype(subtype_id: int, label: str, display_order: int, is_active: bool):
    clean_label = label.strip()

    if not clean_label:
        raise ValueError("Le libellé du sous-type est obligatoire.")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT type_parent FROM app_subtypes WHERE id = ?", (subtype_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise ValueError("Sous-type introuvable.")

    type_parent = row["type_parent"]

    if subtype_exists(type_parent, clean_label, exclude_id=subtype_id):
        conn.close()
        raise ValueError("Un sous-type identique existe déjà pour ce type.")

    cur.execute(
        """
        UPDATE app_subtypes
        SET label = ?, display_order = ?, is_active = ?
        WHERE id = ?
        """,
        (clean_label, display_order, 1 if is_active else 0, subtype_id),
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