import sqlite3
from datetime import datetime

from core.config import DB_PATH


def get_conn():
    """
    Ouvre une connexion vers la base SQLite.

    check_same_thread=False permet d'utiliser la connexion
    dans le contexte Streamlit sans blocage lié aux threads.
    row_factory=sqlite3.Row permet d'accéder aux colonnes
    par leur nom (ex: row["titre"]).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialise les tables nécessaires si elles n'existent pas encore.

    Tables créées :
    - tickets : ticket principal
    - commentaires : commentaires liés aux tickets
    - journal : historique des actions sur les tickets
    """
    conn = get_conn()
    cur = conn.cursor()

    # Table principale des tickets
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            typage TEXT NOT NULL,
            commentaire TEXT,
            photo_path TEXT,
            statut TEXT NOT NULL DEFAULT 'Ouvert',
            priorite TEXT,
            demandeur TEXT NOT NULL,
            dispatcheur TEXT,
            assigne_a TEXT,
            motif_resolution TEXT,
            ticket_maitre_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            closed_at TEXT
        )
        """
    )

    # Table des commentaires associés à un ticket
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS commentaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            auteur TEXT NOT NULL,
            contenu TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id)
        )
        """
    )

    # Table de journalisation des actions
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            auteur TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id)
        )
        """
    )

    conn.commit()
    conn.close()


def now_iso():
    """
    Retourne la date/heure actuelle au format texte homogène.

    Exemple :
    2026-03-23 14:35:10
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")