import pandas as pd

from core.db import get_conn


ALLOWED_TABLES = {
    "tickets": [
        "id",
        "titre",
        "typage",
        "sous_type",
        "commentaire",
        "photo_path",
        "statut",
        "priorite",
        "demandeur",
        "dispatcheur",
        "assigne_a",
        "motif_resolution",
        "ticket_maitre_id",
        "created_at",
        "updated_at",
        "closed_at",
    ],
    "commentaires": [
        "id",
        "ticket_id",
        "auteur",
        "contenu",
        "created_at",
    ],
    "journal": [
        "id",
        "ticket_id",
        "action",
        "details",
        "auteur",
        "created_at",
    ],
}


def run_select_query(
    table: str,
    selected_columns: list[str],
    filters: dict,
    order_by: str | None,
    order_dir: str = "DESC",
    limit: int = 100,
) -> pd.DataFrame:
    if table not in ALLOWED_TABLES:
        raise ValueError("Table non autorisée.")

    allowed_columns = ALLOWED_TABLES[table]

    if not selected_columns:
        selected_columns = allowed_columns

    for col in selected_columns:
        if col not in allowed_columns:
            raise ValueError(f"Colonne non autorisée : {col}")

    if order_by and order_by not in allowed_columns:
        raise ValueError(f"Colonne de tri non autorisée : {order_by}")

    if order_dir not in ("ASC", "DESC"):
        order_dir = "DESC"

    sql = f"SELECT {', '.join(selected_columns)} FROM {table}"
    where_clauses = []
    params = []

    for key, value in filters.items():
        if key not in allowed_columns:
            continue

        if value is None or value == "" or value == []:
            continue

        if isinstance(value, list):
            placeholders = ",".join(["?"] * len(value))
            where_clauses.append(f"{key} IN ({placeholders})")
            params.extend(value)
        else:
            where_clauses.append(f"{key} = ?")
            params.append(value)

    search_text = filters.get("search_text")
    if search_text:
        text_cols = [c for c in ["titre", "commentaire", "contenu", "details"] if c in allowed_columns]
        if text_cols:
            sub = " OR ".join([f"{col} LIKE ?" for col in text_cols])
            where_clauses.append(f"({sub})")
            params.extend([f"%{search_text}%"] * len(text_cols))

    date_from = filters.get("date_from")
    date_to = filters.get("date_to")

    if date_from and "created_at" in allowed_columns:
        where_clauses.append("created_at >= ?")
        params.append(date_from)

    if date_to and "created_at" in allowed_columns:
        where_clauses.append("created_at <= ?")
        params.append(date_to)

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if order_by:
        sql += f" ORDER BY {order_by} {order_dir}"

    sql += " LIMIT ?"
    params.append(limit)

    conn = get_conn()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

    return df