import os
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import pandas as pd

from core.config import UPLOAD_DIR
from core.db import get_conn, now_iso

from core.notifications import (
    notify_dispatch_new_ticket,
    notify_technician_assignment,
    notify_user_closure,
    notify_new_comment,
    notify_user_ticket_merged,
    get_dispatch_email,
    get_tech_email,
    get_user_email,
)

from core.app_config_service import get_active_subtypes_by_type
from core.config import TYPES

def log_action(ticket_id, action, details, auteur):
    """
    Ajoute une entrée dans le journal des actions d'un ticket.

    Exemple d'actions :
    - Création
    - Mise à jour
    - Commentaire
    """
    conn = get_conn()
    conn.execute(
        "INSERT INTO journal (ticket_id, action, details, auteur, created_at) VALUES (?, ?, ?, ?, ?)",
        (ticket_id, action, details, auteur, now_iso()),
    )
    conn.commit()
    conn.close()

def normalize_ticket_classification(typage: str | None, sous_type: str | None) -> tuple[str | None, str | None]:
    """
    Garantit la cohérence entre type principal et sous-type.
    """
    if typage is None:
        return None, None

    if typage not in TYPES:
        raise ValueError(f"Type non autorisé : {typage}")

    if not sous_type:
        return typage, None

    allowed_subtypes = get_active_subtypes_by_type(typage)
    if sous_type not in allowed_subtypes:
        raise ValueError(
            f"Sous-type '{sous_type}' non autorisé pour le type '{typage}'."
        )

    return typage, sous_type

def create_ticket(titre, typage, site, commentaire, demandeur, photo_file=None, sous_type=None):
    """
    Crée un nouveau ticket.

    Si une image est fournie, elle est enregistrée dans le dossier uploads/
    puis son chemin est stocké dans la base.
    """
    photo_path = None

    # Sauvegarde de la photo si présente
    if photo_file is not None:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_file.name}"
        filepath = UPLOAD_DIR / filename

        with open(filepath, "wb") as f:
            f.write(photo_file.getbuffer())

        photo_path = str(filepath)

    # Insertion du ticket en base
    conn = get_conn()
    cur = conn.cursor()
    ts = now_iso()
    typage, sous_type = normalize_ticket_classification(typage, sous_type)

    cur.execute(
        """
        INSERT INTO tickets (
            titre, typage, site, sous_type, commentaire, photo_path, demandeur, created_at, updated_at
        ) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (titre, typage, site, sous_type, commentaire, photo_path, demandeur, ts, ts),
    )

    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Journalisation de la création
    log_action(ticket_id, "Création", f"Ticket créé ({typage} - {site})", demandeur)

    notify_dispatch_new_ticket(
        ticket_id=ticket_id,
        titre=titre,
        typage=typage,
        demandeur=demandeur,
    )

    return ticket_id


def add_comment(ticket_id, auteur, contenu):
    """
    Ajoute un commentaire à un ticket
    puis met à jour la date de dernière modification du ticket.
    """
    conn = get_conn()

    conn.execute(
        "INSERT INTO commentaires (ticket_id, auteur, contenu, created_at) VALUES (?, ?, ?, ?)",
        (ticket_id, auteur, contenu, now_iso()),
    )

    conn.execute(
        "UPDATE tickets SET updated_at = ? WHERE id = ?",
        (now_iso(), ticket_id),
    )

    conn.commit()
    conn.close()

    # Journalisation du commentaire
    log_action(ticket_id, "Commentaire", contenu[:120], auteur)


def add_comment_with_notification(ticket_id, auteur, contenu):
    """
    Ajoute un commentaire à un ticket, met à jour le ticket
    et envoie une notification email au bon destinataire.

    Règles :
    - si l'auteur est le demandeur :
        - notifier le technicien assigné si présent
        - sinon notifier le dispatcheur du type
    - sinon :
        - notifier l'utilisateur demandeur
    """
    add_comment(ticket_id, auteur, contenu)

    ticket = get_ticket(ticket_id)
    if not ticket:
        return False

    destinataire = None

    # Cas 1 : commentaire du demandeur
    if auteur == ticket["demandeur"]:
        if ticket["assigne_a"]:
            destinataire = get_tech_email(ticket["assigne_a"])
        else:
            destinataire = get_dispatch_email(ticket["typage"])

    # Cas 2 : commentaire support / backoffice
    else:
        destinataire = get_user_email(ticket["demandeur"])

    if not destinataire:
        return False

    return notify_new_comment(
        ticket_id=ticket_id,
        titre=ticket["titre"],
        auteur=auteur,
        destinataire_email=destinataire,
        contenu=contenu,
    )

def update_ticket(ticket_id, auteur, **fields):
    """
    Met à jour un ticket avec les champs passés en arguments nommés.
    Journalise précisément les changements effectués.
    Déclenche aussi les notifications email utiles.
    """
    if not fields:
        return

    conn = get_conn()
    cur = conn.cursor()

    # Lecture de l'état actuel du ticket
    cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    before = cur.fetchone()

    effective_type = fields.get("typage", before["typage"] if before else None)
    effective_subtype = fields.get("sous_type", before["sous_type"] if before else None)

    effective_type, effective_subtype = normalize_ticket_classification(
        effective_type,
        effective_subtype,
    )

    fields["typage"] = effective_type
    fields["sous_type"] = effective_subtype

    updates = []
    values = []
    changed = []

    for key, value in fields.items():
        updates.append(f"{key} = ?")
        values.append(value)

        old_value = before[key] if before and key in before.keys() else None
        if old_value != value:
            changed.append(f"{key}: {old_value} -> {value}")

    updates.append("updated_at = ?")
    values.append(now_iso())
    values.append(ticket_id)

    cur.execute(f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()

    # Relire le ticket après update
    cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    after = cur.fetchone()

    conn.close()

    if changed:
        log_action(ticket_id, "Mise à jour", " | ".join(changed), auteur)

    # --------------------------------------------------
    # Notifications email
    # --------------------------------------------------

    # 1. Ticket assigné à un technicien
    before_assigne = before["assigne_a"] if before else None
    after_assigne = after["assigne_a"] if after else None

    if after_assigne and before_assigne != after_assigne:
        notify_technician_assignment(
            ticket_id=ticket_id,
            titre=after["titre"],
            technicien=after_assigne,
            statut=after["statut"],
            priorite=after["priorite"],
        )

    # 2. Ticket clôturé
    before_statut = before["statut"] if before else None
    after_statut = after["statut"] if after else None

    if before_statut != "Clôturé" and after_statut == "Clôturé":
        notify_user_closure(
            ticket_id=ticket_id,
            titre=after["titre"],
            demandeur=after["demandeur"],
            motif_resolution=after["motif_resolution"],
        )
                # Clôture en cascade des tickets esclaves
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT *
            FROM tickets
            WHERE ticket_maitre_id = ?
              AND statut != 'Clôturé'
            """,
            (ticket_id,),
        )
        children = cur.fetchall()

        for child in children:
            cur.execute(
                """
                UPDATE tickets
                SET statut = 'Clôturé',
                    motif_resolution = ?,
                    closed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    f"Clôture automatique suite à la clôture du ticket maître #{ticket_id}",
                    now_iso(),
                    now_iso(),
                    child["id"],
                ),
            )

            log_action(
                child["id"],
                "Clôture automatique",
                f"Ticket enfant clôturé suite à la clôture du maître #{ticket_id}",
                auteur,
            )

            notify_user_closure(
                ticket_id=child["id"],
                titre=child["titre"],
                demandeur=child["demandeur"],
                motif_resolution=f"Clôture automatique suite à la clôture du ticket maître #{ticket_id}",
            )

        conn.commit()
        conn.close()


def get_tickets():
    """
    Retourne tous les tickets sous forme de DataFrame pandas,
    triés du plus récent au plus ancien.
    """
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_ticket(ticket_id):
    """
    Retourne un ticket unique par son identifiant.
    Le résultat est une ligne SQLite accessible par nom de colonne.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = cur.fetchone()
    conn.close()
    return ticket

def get_child_tickets(master_ticket_id):
    """
    Retourne les tickets esclaves rattachés à un ticket maître.
    """
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT *
        FROM tickets
        WHERE ticket_maitre_id = ?
        ORDER BY created_at DESC
        """,
        conn,
        params=(master_ticket_id,),
    )
    conn.close()
    return df

def merge_tickets_into_master(master_ticket_id: int, child_ticket_ids: list[int], auteur: str) -> int:
    """
    Rattache un ou plusieurs tickets esclaves à un ticket maître.
    Envoie une notification aux demandeurs des tickets fusionnés.
    Retourne le nombre de tickets fusionnés.
    """
    if not child_ticket_ids:
        return 0

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tickets WHERE id = ?", (master_ticket_id,))
    master = cur.fetchone()

    if not master:
        conn.close()
        raise ValueError("Ticket maître introuvable.")

    merged_count = 0

    for child_id in child_ticket_ids:
        if child_id == master_ticket_id:
            continue

        cur.execute("SELECT * FROM tickets WHERE id = ?", (child_id,))
        child = cur.fetchone()

        if not child:
            continue

        if child["ticket_maitre_id"] == master_ticket_id:
            continue

        # On rattache le ticket enfant au maître
        cur.execute(
            """
            UPDATE tickets
            SET ticket_maitre_id = ?, statut = ?, updated_at = ?
            WHERE id = ?
            """,
            (master_ticket_id, master["statut"], now_iso(), child_id),
        )

        merged_count += 1

        cur.execute(
            """
            INSERT INTO journal (ticket_id, action, details, auteur, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                child_id,
                "Fusion",
                f"Ticket fusionné vers le maître #{master_ticket_id}",
                auteur,
                now_iso(),
            ),
        )

        cur.execute(
            """
            INSERT INTO journal (ticket_id, action, details, auteur, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                master_ticket_id,
                "Fusion",
                f"Ticket esclave rattaché : #{child_id}",
                auteur,
                now_iso(),
            ),
        )

        notify_user_ticket_merged(
            child_ticket_id=child_id,
            master_ticket_id=master_ticket_id,
            master_title=master["titre"],
            demandeur=child["demandeur"],
        )

    conn.commit()
    conn.close()

    return merged_count

def get_comments(ticket_id):
    """
    Retourne les commentaires d'un ticket sous forme de DataFrame,
    du plus ancien au plus récent.
    """
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT auteur, contenu, created_at FROM commentaires WHERE ticket_id = ? ORDER BY created_at ASC",
        conn,
        params=(ticket_id,),
    )
    conn.close()
    return df


def get_logs(ticket_id):
    """
    Retourne l'historique (journal) d'un ticket sous forme de DataFrame,
    du plus récent au plus ancien.
    """
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT action, details, auteur, created_at FROM journal WHERE ticket_id = ? ORDER BY created_at DESC",
        conn,
        params=(ticket_id,),
    )
    conn.close()
    return df

def remove_ticket_from_master(child_ticket_id: int, auteur: str) -> bool:
    """
    Retire un ticket esclave de son ticket maître.
    Le ticket redevient autonome et repasse en statut Ouvert.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tickets WHERE id = ?", (child_ticket_id,))
    child = cur.fetchone()

    if not child:
        conn.close()
        raise ValueError("Ticket introuvable.")

    if not child["ticket_maitre_id"]:
        conn.close()
        raise ValueError("Ce ticket n'est pas rattaché à un ticket maître.")

    master_ticket_id = child["ticket_maitre_id"]

    cur.execute(
        """
        UPDATE tickets
        SET ticket_maitre_id = NULL,
            statut = 'Ouvert',
            updated_at = ?
        WHERE id = ?
        """,
        (now_iso(), child_ticket_id),
    )

    cur.execute(
        """
        INSERT INTO journal (ticket_id, action, details, auteur, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            child_ticket_id,
            "Sortie de doublon",
            f"Ticket retiré du maître #{master_ticket_id}",
            auteur,
            now_iso(),
        ),
    )

    cur.execute(
        """
        INSERT INTO journal (ticket_id, action, details, auteur, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            master_ticket_id,
            "Sortie de doublon",
            f"Ticket esclave retiré : #{child_ticket_id}",
            auteur,
            now_iso(),
        ),
    )

    conn.commit()
    conn.close()

    return True

def suggest_duplicates(titre, typage):
    """
    Propose des tickets potentiellement similaires pour éviter les doublons.

    La logique combine :
    - une similarité textuelle sur le titre
    - un léger bonus si certains mots-clés se recoupent
    - un filtre sur les 30 derniers jours
    - un filtre sur le même type de ticket
    """
    df = get_tickets()
    df = df[df["statut"] != "Clôturé"]

    if df.empty:
        return pd.DataFrame()

    # On ne compare qu'avec les tickets récents
    recent_limit = datetime.now() - timedelta(days=30)
    df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")

    df = df[(df["typage"] == typage) & (df["created_dt"] >= recent_limit)]

    if df.empty:
        return pd.DataFrame()

    def score(row):
        """
        Calcule un score de similarité entre le nouveau titre
        et le titre d'un ticket existant.
        """
        text = row["titre"] or ""
        ratio = SequenceMatcher(None, titre.lower(), text.lower()).ratio()
        keyword_overlap = len(set(titre.lower().split()) & set(text.lower().split()))

        # Pondération :
        # - 80% similarité globale
        # - 20% recouvrement de mots-clés max
        return round((ratio * 0.8) + min(keyword_overlap / 10, 0.2), 3)

    df["score_similarite"] = df.apply(score, axis=1)

    df = df[df["score_similarite"] >= 0.6].sort_values("score_similarite", ascending=False)

    return df[["id", "titre", "statut", "created_at", "score_similarite"]].head(5)


def compute_dashboard(df):
    """
    Calcule les indicateurs simples du tableau de bord.

    Indicateurs produits :
    - nombre total de tickets
    - volume Infra / Numérique
    - nombre de doublons
    - temps moyen de résolution (heures)
    - % de tickets ouverts / en cours depuis plus de 7 jours
    """
    metrics = {}

    metrics["total"] = len(df)
    metrics["infra"] = int((df["typage"] == "Infra").sum()) if not df.empty else 0
    metrics["numerique"] = int((df["typage"] == "Numérique").sum()) if not df.empty else 0
    metrics["doublons"] = int((df["statut"] == "Doublon").sum()) if not df.empty else 0

    if not df.empty:
        created = pd.to_datetime(df["created_at"], errors="coerce")
        closed = pd.to_datetime(df["closed_at"], errors="coerce")

        # Temps de résolution en heures
        delta = (closed - created).dt.total_seconds() / 3600
        metrics["temps_moyen_h"] = round(delta.dropna().mean(), 1) if delta.dropna().shape[0] else None

        # Tickets ouverts ou en cours vieux de plus de 7 jours
        open_long = df[df["statut"].isin(["Ouvert", "En cours"])].copy()

        if not open_long.empty:
            open_long["created_dt"] = pd.to_datetime(open_long["created_at"], errors="coerce")
            over_7 = (datetime.now() - open_long["created_dt"]).dt.days > 7
            metrics["pct_en_cours_7j"] = round((over_7.sum() / len(open_long)) * 100, 1)
        else:
            metrics["pct_en_cours_7j"] = 0.0
    else:
        metrics["temps_moyen_h"] = None
        metrics["pct_en_cours_7j"] = 0.0

    return metrics


def export_csv(df):
    """
    Convertit un DataFrame en CSV encodé en UTF-8 BOM,
    pratique pour une ouverture propre dans Excel.
    """
    return df.to_csv(index=False).encode("utf-8-sig")

def archive_closed_tickets(days: int = 7) -> int:
    """
    Archive les tickets clôturés depuis plus de `days` jours,
    ainsi que leurs commentaires.
    La journalisation reste dans la table active `journal`.
    Retourne le nombre de tickets archivés.
    """
    conn = get_conn()
    cur = conn.cursor()

    threshold = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    archived_at = now_iso()

    # 1. Sélection des tickets à archiver
    cur.execute(
        """
        SELECT *
        FROM tickets
        WHERE statut = 'Clôturé'
          AND closed_at IS NOT NULL
          AND closed_at < ?
        """,
        (threshold,),
    )
    tickets_to_archive = cur.fetchall()

    if not tickets_to_archive:
        conn.close()
        return 0

    ticket_ids = [row["id"] for row in tickets_to_archive]

    # 2. Copier les tickets dans tickets_archive
    for row in tickets_to_archive:
        cur.execute(
            """
            INSERT OR REPLACE INTO tickets_archive (
                id, titre, typage, sous_type, commentaire, photo_path,
                statut, priorite, demandeur, dispatcheur, assigne_a,
                motif_resolution, ticket_maitre_id,
                created_at, updated_at, closed_at, archived_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["titre"],
                row["typage"],
                row["sous_type"],
                row["commentaire"],
                row["photo_path"],
                row["statut"],
                row["priorite"],
                row["demandeur"],
                row["dispatcheur"],
                row["assigne_a"],
                row["motif_resolution"],
                row["ticket_maitre_id"],
                row["created_at"],
                row["updated_at"],
                row["closed_at"],
                archived_at,
            ),
        )

    # 3. Copier les commentaires liés dans commentaires_archive
    placeholders = ",".join(["?"] * len(ticket_ids))
    cur.execute(
        f"""
        SELECT *
        FROM commentaires
        WHERE ticket_id IN ({placeholders})
        """,
        ticket_ids,
    )
    comments_to_archive = cur.fetchall()

    for row in comments_to_archive:
        cur.execute(
            """
            INSERT OR REPLACE INTO commentaires_archive (
                id, ticket_id, auteur, contenu, created_at, archived_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["ticket_id"],
                row["auteur"],
                row["contenu"],
                row["created_at"],
                archived_at,
            ),
        )

    # 4. Supprimer les commentaires actifs archivés
    cur.execute(
        f"DELETE FROM commentaires WHERE ticket_id IN ({placeholders})",
        ticket_ids,
    )

    # 5. Supprimer les tickets actifs archivés
    cur.execute(
        f"DELETE FROM tickets WHERE id IN ({placeholders})",
        ticket_ids,
    )

    conn.commit()
    conn.close()

    return len(ticket_ids)

def seed_demo_data():
    """
    Insère quelques tickets de démonstration si la base est vide.

    Cela permet d'avoir immédiatement du contenu pour la démo
    sans saisie manuelle initiale.
    """
    df = get_tickets()

    # Si la base contient déjà des tickets, on ne rajoute rien
    if not df.empty:
        return

    # Création de tickets de démonstration
    t1 = create_ticket(
        "Imprimante du 2e étage en panne",
        "Infra",
        "Siège",
        "Impossible d'imprimer depuis ce matin",
        "alice",
    )
    t2 = create_ticket(
        "Erreur connexion ERP",
        "Numérique",
        "Siège",
        "Message d'erreur à l'ouverture",
        "bruno",
    )
    t3 = create_ticket(
        "Wifi instable salle de réunion",
        "Infra",
        "Siège",
        "Déconnexions fréquentes",
        "carla",
    )

    # Mise à jour de certains tickets pour simuler une vraie vie applicative
    update_ticket(t1, "dio", priorite="Normale", dispatcheur="dio", assigne_a="tech_infra_1", statut="En cours")
    update_ticket(t2, "dsn", priorite="Haute", dispatcheur="dsn", assigne_a="tech_app_1", statut="En cours")
    update_ticket(t3, "dio", priorite="Basse", dispatcheur="dio", assigne_a="tech_infra_2")

    # Ajout de commentaires de démonstration
    add_comment(t1, "tech_infra_1", "Vérification du bac papier et du spooler en cours")
    add_comment(t2, "tech_app_1", "Incident reproduit, analyse des logs applicatifs")