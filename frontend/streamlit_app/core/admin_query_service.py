"""
Couche de compatibilité transitoire pour l'administration.

Anciennement, ce module exécutait des requêtes SQLite côté frontend.
Désormais, toutes les données doivent venir du backend API.
"""

import pandas as pd

from core.api_tickets import api_get_comments, api_get_journal, api_get_tickets


def get_tickets_dataframe() -> pd.DataFrame:
    try:
        return pd.DataFrame(api_get_tickets())
    except RuntimeError:
        return pd.DataFrame()


def get_comments_dataframe() -> pd.DataFrame:
    tickets_df = get_tickets_dataframe()
    if tickets_df.empty or "id" not in tickets_df.columns:
        return pd.DataFrame()

    rows = []
    for ticket_id in tickets_df["id"].dropna().tolist():
        try:
            comments = api_get_comments(int(ticket_id))
        except RuntimeError:
            continue

        for item in comments:
            row = dict(item)
            row["ticket_id"] = int(ticket_id)
            rows.append(row)

    return pd.DataFrame(rows)


def get_journal_dataframe() -> pd.DataFrame:
    tickets_df = get_tickets_dataframe()
    if tickets_df.empty or "id" not in tickets_df.columns:
        return pd.DataFrame()

    rows = []
    for ticket_id in tickets_df["id"].dropna().tolist():
        try:
            journal_entries = api_get_journal(int(ticket_id))
        except RuntimeError:
            continue

        for item in journal_entries:
            row = dict(item)
            row["ticket_id"] = int(ticket_id)
            rows.append(row)

    return pd.DataFrame(rows)