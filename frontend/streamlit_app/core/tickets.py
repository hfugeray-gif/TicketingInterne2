"""
Couche transitoire de compatibilité.

But:
- éviter de casser les imports historiques
- permettre de remettre l'app en route
- préparer une migration progressive vers l'API/backend
"""

from difflib import SequenceMatcher

import pandas as pd

from core.api_tickets import api_get_comments, api_get_journal, api_get_tickets


def seed_demo_data():
    return None


def archive_closed_tickets(days: int = 7):
    return None


def get_tickets() -> pd.DataFrame:
    try:
        data = api_get_tickets()
    except Exception:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if df.empty:
        return df

    if "ticket_maitre_id" in df.columns:
        df["is_duplicate_child"] = df["ticket_maitre_id"].notna()
    else:
        df["is_duplicate_child"] = False

    if "statut" in df.columns:
        df["statut_affiche"] = df["statut"]
        df.loc[df["is_duplicate_child"], "statut_affiche"] = "Doublon"

    return df


def suggest_duplicates(titre: str, typage: str) -> pd.DataFrame:
    titre_normalise = titre.strip().lower()
    if not titre_normalise:
        return pd.DataFrame()

    df = get_tickets()
    if df.empty:
        return df

    if "titre" not in df.columns or "typage" not in df.columns:
        return pd.DataFrame()

    if "statut" in df.columns:
        df = df[df["statut"] != "Clôturé"]

    df = df[df["typage"] == typage].copy()
    if df.empty:
        return df

    df["score"] = df["titre"].astype(str).apply(
        lambda x: SequenceMatcher(None, titre_normalise, x.strip().lower()).ratio()
    )

    df = df[df["score"] >= 0.60].copy()
    if df.empty:
        return df

    cols = [c for c in ["id", "titre", "statut", "site", "score"] if c in df.columns]
    return df.sort_values(["score", "id"], ascending=[False, False])[cols]


def export_csv(df: pd.DataFrame) -> bytes:
    if df is None or df.empty:
        return b""
    return df.to_csv(index=False).encode("utf-8-sig")


def get_comments_dataframe(ticket_ids: list[int] | None = None) -> pd.DataFrame:
    rows = []
    tickets_df = get_tickets()

    if tickets_df.empty or "id" not in tickets_df.columns:
        return pd.DataFrame()

    ids = ticket_ids if ticket_ids else tickets_df["id"].dropna().astype(int).tolist()

    for ticket_id in ids:
        try:
            comments = api_get_comments(int(ticket_id))
        except Exception:
            continue

        for item in comments:
            row = dict(item)
            row["ticket_id"] = int(ticket_id)
            rows.append(row)

    return pd.DataFrame(rows)


def get_journal_dataframe(ticket_ids: list[int] | None = None) -> pd.DataFrame:
    rows = []
    tickets_df = get_tickets()

    if tickets_df.empty or "id" not in tickets_df.columns:
        return pd.DataFrame()

    ids = ticket_ids if ticket_ids else tickets_df["id"].dropna().astype(int).tolist()

    for ticket_id in ids:
        try:
            entries = api_get_journal(int(ticket_id))
        except Exception:
            continue

        for item in entries:
            row = dict(item)
            row["ticket_id"] = int(ticket_id)
            rows.append(row)

    return pd.DataFrame(rows)