import sqlite3
from datetime import datetime

from core.config import DB_PATH


def get_conn():
    """
    Ouvre une connexion vers la base SQLite.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    return conn


def init_db():
    """
    Initialise les tables nécessaires si elles n'existent pas encore.
    """
    conn = get_conn()
    cur = conn.cursor()

    # --------------------------------------------------
    # Tickets
    # --------------------------------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            typage TEXT NOT NULL,
            site TEXT,
            sous_type TEXT,
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

    # Compatibilité si la base existe déjà sans sous_type
    cur.execute("PRAGMA table_info(tickets)")
    ticket_cols = [row[1] for row in cur.fetchall()]
    if "sous_type" not in ticket_cols:
        cur.execute("ALTER TABLE tickets ADD COLUMN sous_type TEXT")

    if "site" not in ticket_cols:
        cur.execute("ALTER TABLE tickets ADD COLUMN site TEXT")

    # --------------------------------------------------
    # Commentaires
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Journal
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Archives : tickets
    # --------------------------------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets_archive (
            id INTEGER PRIMARY KEY,
            titre TEXT NOT NULL,
            typage TEXT NOT NULL,
            sous_type TEXT,
            commentaire TEXT,
            photo_path TEXT,
            statut TEXT NOT NULL,
            priorite TEXT,
            demandeur TEXT NOT NULL,
            dispatcheur TEXT,
            assigne_a TEXT,
            motif_resolution TEXT,
            ticket_maitre_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            closed_at TEXT,
            archived_at TEXT NOT NULL
        )
        """
    )

    # --------------------------------------------------
    # Archives : commentaires
    # --------------------------------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS commentaires_archive (
            id INTEGER PRIMARY KEY,
            ticket_id INTEGER NOT NULL,
            auteur TEXT NOT NULL,
            contenu TEXT NOT NULL,
            created_at TEXT NOT NULL,
            archived_at TEXT NOT NULL
        )
        """
    )

    # --------------------------------------------------
    # Paramétrage : sous-types
    # --------------------------------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_subtypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_parent TEXT NOT NULL,
            label TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    # --------------------------------------------------
    # Paramétrage : pages
    # --------------------------------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_pages_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_key TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL,
            icon TEXT,
            display_order INTEGER NOT NULL DEFAULT 0,
            is_visible INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    conn.commit()

    # --------------------------------------------------
    # Seeds de paramétrage si vide
    # --------------------------------------------------
    cur.execute("SELECT COUNT(*) FROM app_subtypes")
    if cur.fetchone()[0] == 0:
        subtypes_seed = [
            ("Infra", "Plomberie", 1, 1),
            ("Infra", "Électricité", 2, 1),
            ("Infra", "Climatisation", 3, 1),
            ("Infra", "Mobilier", 4, 1),
            ("Infra", "Serrurerie", 5, 1),
            ("Infra", "Autre infra", 6, 1),
            ("Numérique", "Logiciel", 1, 1),
            ("Numérique", "Réseau", 2, 1),
            ("Numérique", "Matériel", 3, 1),
            ("Numérique", "ERP", 4, 1),
            ("Numérique", "Messagerie", 5, 1),
            ("Numérique", "Téléphonie", 6, 1),
            ("Numérique", "Autre numérique", 7, 1),
        ]
        cur.executemany(
            """
            INSERT INTO app_subtypes (type_parent, label, display_order, is_active)
            VALUES (?, ?, ?, ?)
            """,
            subtypes_seed,
        )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM app_pages_config")
    if cur.fetchone()[0] == 0:
        pages_seed = [
            ("login", "Connexion", "🔐", 1, 1),
            ("home", "Accueil", "🏠", 2, 1),
            ("create_ticket", "Créer un ticket", "➕", 3, 1),
            ("my_tickets", "Mes tickets", "🎫", 4, 1),
            ("ticket_queue", "File de tickets", "📋", 5, 1),
            ("dashboard", "Pilotage", "📊", 6, 1),
            ("admin_export", "Admin / Export", "⚙️", 7, 1),
            ("profile", "Profil", "👤", 8, 1),
        ]
        cur.executemany(
            """
            INSERT INTO app_pages_config (page_key, label, icon, display_order, is_visible)
            VALUES (?, ?, ?, ?, ?)
            """,
            pages_seed,
        )
        conn.commit()

    conn.close()


def now_iso():
    """
    Retourne la date/heure actuelle au format texte homogène.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")