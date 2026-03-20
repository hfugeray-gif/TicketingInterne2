import os
import sqlite3
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = "tickets_demo.db"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

STATUTS = ["Ouvert", "En cours", "Clôturé", "Doublon"]
PRIORITES = ["Basse", "Normale", "Haute"]
TYPES = ["Infra", "Numérique"]
ROLES = [
    "Utilisateur",
    "Dispatcheur DIO",
    "Dispatcheur DSN",
    "Technicien",
    "Admin",
    "Supervision",
]

st.set_page_config(
    page_title="Ticketing interne — Démo MVP",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_PATH = "Script/BEAM_LOGO_DEF_NOIR.png"

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        header {
            background: transparent !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
            height: 3rem;
        }

        .stApp {
            background: linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
        }

        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 1.2rem;
            max-width: 1200px;
        }

        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.35) !important;
            border-right: 1px solid #d9e2f2;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid #d9e2f2;
            border-radius: 16px;
            padding: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        }

        div.stButton > button {
            border-radius: 12px;
            border: none;
            background: #0f4c81;
            color: white;
            font-weight: 600;
            padding: 0.6rem 1rem;
        }

        div.stButton > button:hover {
            background: #0c3d68;
            color: white;
        }

        div.stButton > button:focus:not(:active) {
            color: white !important;
            border: none !important;
            box-shadow: 0 0 0 0.2rem rgba(15, 76, 129, 0.2) !important;
        }

        div[data-testid="stFileUploader"] section,
        div[data-testid="stTextInputRootElement"],
        div[data-testid="stTextAreaRootElement"],
        div[data-testid="stNumberInputRootElement"],
        div[data-testid="stDateInputRootElement"] {
            border-radius: 12px;
            background: transparent !important;
        }

        div[data-testid="stTextInputRootElement"] input,
        div[data-testid="stTextAreaRootElement"] textarea,
        div[data-testid="stNumberInputRootElement"] input {
            background: rgba(255, 255, 255, 0.92) !important;
            border: 1px solid #d9e2f2 !important;
            border-radius: 12px !important;
        }

        div[data-testid="stTextInputRootElement"] input:focus,
        div[data-testid="stTextAreaRootElement"] textarea:focus,
        div[data-testid="stNumberInputRootElement"] input:focus {
            border: 1px solid #0f4c81 !important;
            box-shadow: 0 0 0 0.15rem rgba(15, 76, 129, 0.12) !important;
        }

        div[data-testid="stTextAreaRootElement"] textarea {
            min-height: 120px;
        }

        div[data-baseweb="select"] {
            background: transparent !important;
            border: none !important;
        }

        div[data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.72) !important;
            border: 1px solid #d9e2f2 !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }

        div[data-baseweb="select"] > div:hover {
            background: rgba(255, 255, 255, 0.86) !important;
        }

        label, .stSelectbox label, .stTextInput label, .stTextArea label, .stRadio label {
            background: transparent !important;
            color: #486581 !important;
            font-weight: 500;
        }

        .top-banner {
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 10px 0 10px 0;
            margin-bottom: 18px;
            box-shadow: none;
        }

        .top-banner h1 {
            margin: 0;
            color: #12344d;
            font-size: 2rem;
        }

        .top-banner p {
            margin: 6px 0 0 0;
            color: #486581;
        }

        div[data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.55);
            border-radius: 14px;
            border: 1px solid #d9e2f2;
            overflow: hidden;
        }

        div[data-testid="stTabs"] button {
            border-radius: 10px 10px 0 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if os.path.exists(LOGO_PATH):
    c_logo, c_title = st.columns([1, 5])
    with c_logo:
        st.image(LOGO_PATH, width=110)
    with c_title:
        st.markdown(
            """
            <div class="top-banner">
                <h1>Ticketing interne — Démo MVP</h1>
                <p>Prototype Python / Streamlit personnalisé aux couleurs de l'entreprise</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="top-banner">
            <h1>Ticketing interne — Démo MVP</h1>
            <p>Prototype Python / Streamlit personnalisé aux couleurs de l'entreprise</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

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
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_action(ticket_id, action, details, auteur):
    conn = get_conn()
    conn.execute(
        "INSERT INTO journal (ticket_id, action, details, auteur, created_at) VALUES (?, ?, ?, ?, ?)",
        (ticket_id, action, details, auteur, now_iso()),
    )
    conn.commit()
    conn.close()


def create_ticket(titre, typage, commentaire, demandeur, photo_file=None):
    photo_path = None
    if photo_file is not None:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_file.name}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            f.write(photo_file.getbuffer())
        photo_path = str(filepath)

    conn = get_conn()
    cur = conn.cursor()
    ts = now_iso()
    cur.execute(
        """
        INSERT INTO tickets (
            titre, typage, commentaire, photo_path, demandeur, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (titre, typage, commentaire, photo_path, demandeur, ts, ts),
    )
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    log_action(ticket_id, "Création", f"Ticket créé ({typage})", demandeur)
    return ticket_id


def add_comment(ticket_id, auteur, contenu):
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
    log_action(ticket_id, "Commentaire", contenu[:120], auteur)


def update_ticket(ticket_id, auteur, **fields):
    if not fields:
        return

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    before = cur.fetchone()

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
    conn.close()

    if changed:
        log_action(ticket_id, "Mise à jour", " | ".join(changed), auteur)


def get_tickets():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_ticket(ticket_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = cur.fetchone()
    conn.close()
    return ticket


def get_comments(ticket_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT auteur, contenu, created_at FROM commentaires WHERE ticket_id = ? ORDER BY created_at ASC",
        conn,
        params=(ticket_id,),
    )
    conn.close()
    return df


def get_logs(ticket_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT action, details, auteur, created_at FROM journal WHERE ticket_id = ? ORDER BY created_at DESC",
        conn,
        params=(ticket_id,),
    )
    conn.close()
    return df


def suggest_duplicates(titre, typage):
    df = get_tickets()
    if df.empty:
        return pd.DataFrame()

    recent_limit = datetime.now() - timedelta(days=30)
    df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df[(df["typage"] == typage) & (df["created_dt"] >= recent_limit)]
    if df.empty:
        return pd.DataFrame()

    def score(row):
        text = row["titre"] or ""
        ratio = SequenceMatcher(None, titre.lower(), text.lower()).ratio()
        keyword_overlap = len(set(titre.lower().split()) & set(text.lower().split()))
        return round((ratio * 0.8) + min(keyword_overlap / 10, 0.2), 3)

    df["score_similarite"] = df.apply(score, axis=1)
    df = df[df["score_similarite"] >= 0.35].sort_values("score_similarite", ascending=False)
    return df[["id", "titre", "statut", "created_at", "score_similarite"]].head(5)


def compute_dashboard(df):
    metrics = {}
    metrics["total"] = len(df)
    metrics["infra"] = int((df["typage"] == "Infra").sum()) if not df.empty else 0
    metrics["numerique"] = int((df["typage"] == "Numérique").sum()) if not df.empty else 0
    metrics["doublons"] = int((df["statut"] == "Doublon").sum()) if not df.empty else 0

    if not df.empty:
        created = pd.to_datetime(df["created_at"], errors="coerce")
        closed = pd.to_datetime(df["closed_at"], errors="coerce")
        delta = (closed - created).dt.total_seconds() / 3600
        metrics["temps_moyen_h"] = round(delta.dropna().mean(), 1) if delta.dropna().shape[0] else None

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
    return df.to_csv(index=False).encode("utf-8-sig")


def seed_demo_data():
    df = get_tickets()
    if not df.empty:
        return

    t1 = create_ticket("Imprimante du 2e étage en panne", "Infra", "Impossible d'imprimer depuis ce matin", "alice")
    t2 = create_ticket("Erreur connexion ERP", "Numérique", "Message d'erreur à l'ouverture", "bruno")
    t3 = create_ticket("Wifi instable salle de réunion", "Infra", "Déconnexions fréquentes", "carla")

    update_ticket(t1, "dio", priorite="Normale", dispatcheur="dio", assigne_a="tech_infra_1", statut="En cours")
    update_ticket(t2, "dsn", priorite="Haute", dispatcheur="dsn", assigne_a="tech_app_1", statut="En cours")
    update_ticket(t3, "dio", priorite="Basse", dispatcheur="dio", assigne_a="tech_infra_2")
    add_comment(t1, "tech_infra_1", "Vérification du bac papier et du spooler en cours")
    add_comment(t2, "tech_app_1", "Incident reproduit, analyse des logs applicatifs")


init_db()
seed_demo_data()

with st.sidebar:
    st.header("Contexte démo")
    role = st.selectbox("Rôle simulé", ROLES)
    current_user = st.text_input("Nom / identifiant", value="demo_user")
    st.markdown("---")
    st.write("Workflow : Ouvert → En cours → Clôturé (+ Doublon)")
    st.write("Typage : Infra / Numérique")
    st.write("Dispatch manuel : DIO / DSN")

onglet1, onglet2, onglet3, onglet4 = st.tabs([
    "Créer un ticket",
    "File de tickets",
    "Pilotage",
    "Admin / Export",
])

with onglet1:
    st.subheader("Création rapide")
    titre = st.text_input("Titre *")
    typage = st.radio("Typage *", TYPES, horizontal=True)
    commentaire = st.text_area("Commentaire")

    photo_mode = st.radio("Mode photo", ["Prendre une photo", "Téléverser une image"], horizontal=True)

    if "show_camera" not in st.session_state:
        st.session_state.show_camera = False

    if photo_mode == "Prendre une photo":
        if not st.session_state.show_camera:
            if st.button("📸 Ouvrir la caméra"):
                st.session_state.show_camera = True
        if st.session_state.show_camera:
            photo = st.camera_input("Prendre une photo")
        else:
            photo = None
    else:
        st.session_state.show_camera = False
        photo = st.file_uploader("Photo", type=["png", "jpg", "jpeg"])

    if titre:
        suggestions = suggest_duplicates(titre, typage)
        if not suggestions.empty:
            st.warning("Tickets potentiellement similaires détectés")
            st.dataframe(suggestions, use_container_width=True)

    if st.button("Créer le ticket", type="primary"):
        if not titre.strip():
            st.error("Le titre est obligatoire.")
        else:
            ticket_id = create_ticket(titre.strip(), typage, commentaire.strip(), current_user, photo)
            st.success(f"Ticket #{ticket_id} créé avec succès.")
            st.info("Notification simulée : demandeur notifié à la création.")
            st.session_state.show_camera = False

with onglet2:
    st.subheader("Vue opérationnelle")
    df = get_tickets()

    if "selected_ticket_id" not in st.session_state:
        st.session_state.selected_ticket_id = None

    if df.empty:
        st.info("Aucun ticket pour le moment.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtre_statut = st.selectbox("Statut", ["Tous"] + STATUTS)
        with col2:
            filtre_type = st.selectbox("Type", ["Tous"] + TYPES)
        with col3:
            filtre_priorite = st.selectbox("Priorité", ["Toutes"] + PRIORITES)
        with col4:
            filtre_texte = st.text_input("Recherche")

        filtered = df.copy()
        if filtre_statut != "Tous":
            filtered = filtered[filtered["statut"] == filtre_statut]
        if filtre_type != "Tous":
            filtered = filtered[filtered["typage"] == filtre_type]
        if filtre_priorite != "Toutes":
            filtered = filtered[filtered["priorite"] == filtre_priorite]
        if filtre_texte.strip():
            mask = (
                filtered["titre"].fillna("").str.contains(filtre_texte, case=False)
                | filtered["commentaire"].fillna("").str.contains(filtre_texte, case=False)
            )
            filtered = filtered[mask]

        st.markdown("### Tickets")
        left_panel, right_panel = st.columns([1.1, 1.7], gap="large")

        with left_panel:
            st.caption(f"{len(filtered)} ticket(s) trouvé(s)")

            if filtered.empty:
                st.info("Aucun ticket ne correspond aux filtres.")
            else:
                for _, row in filtered.iterrows():
                    is_selected = st.session_state.selected_ticket_id == int(row["id"])
                    statut_color = {
                        "Ouvert": "#d97706",
                        "En cours": "#0f4c81",
                        "Clôturé": "#2d6a4f",
                        "Doublon": "#7c3aed",
                    }.get(row["statut"], "#486581")

                    st.markdown(
                        f"""
                        <div style="
                            background: rgba(255,255,255,0.78);
                            border: 1px solid {'#0f4c81' if is_selected else '#d9e2f2'};
                            border-left: 5px solid {statut_color};
                            border-radius: 14px;
                            padding: 12px 14px;
                            margin-bottom: 10px;
                            box-shadow: {'0 8px 20px rgba(15,76,129,0.12)' if is_selected else 'none'};
                        ">
                            <div style="font-weight: 700; color: #12344d; font-size: 1rem; margin-bottom: 4px;">
                                #{int(row['id'])} — {row['titre']}
                            </div>
                            <div style="color: #486581; font-size: 0.92rem; margin-bottom: 6px;">
                                {row['typage']} · {row['statut']} · {row['priorite'] if pd.notna(row['priorite']) and row['priorite'] else 'Sans priorité'}
                            </div>
                            <div style="color: #6b7c93; font-size: 0.85rem;">
                                Demandeur : {row['demandeur']} · Assigné : {row['assigne_a'] if pd.notna(row['assigne_a']) and row['assigne_a'] else '-'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Voir le ticket" if not is_selected else "Ticket affiché",
                        key=f"open_ticket_{int(row['id'])}",
                        use_container_width=True,
                        disabled=is_selected,
                    ):
                        st.session_state.selected_ticket_id = int(row["id"])
                        st.rerun()

                if st.session_state.selected_ticket_id is None and not filtered.empty:
                    st.session_state.selected_ticket_id = int(filtered.iloc[0]["id"])
                    st.rerun()

        with right_panel:
            selected_ticket_id = st.session_state.selected_ticket_id
            if selected_ticket_id is None or selected_ticket_id not in filtered["id"].tolist():
                st.info("Sélectionne un ticket à gauche pour afficher son détail.")
            else:
                ticket = get_ticket(selected_ticket_id)

                if ticket:
                    st.markdown("### Détail du ticket")
                    left, right = st.columns([2, 1])
                    with left:
                        st.write(f"**Titre** : {ticket['titre']}")
                        st.write(f"**Type** : {ticket['typage']}")
                        st.write(f"**Statut** : {ticket['statut']}")
                        st.write(f"**Priorité** : {ticket['priorite'] or '-'}")
                        st.write(f"**Demandeur** : {ticket['demandeur']}")
                        st.write(f"**Commentaire initial** : {ticket['commentaire'] or '-'}")
                        st.write(f"**Créé le** : {ticket['created_at']}")
                        if ticket["motif_resolution"]:
                            st.write(f"**Motif de résolution** : {ticket['motif_resolution']}")
                        if ticket["ticket_maitre_id"]:
                            st.write(f"**Ticket maître** : #{ticket['ticket_maitre_id']}")
                    with right:
                        if ticket["photo_path"] and os.path.exists(ticket["photo_path"]):
                            st.image(ticket["photo_path"], caption="Photo jointe")

                    st.markdown("### Actions")
                    a1, a2 = st.columns(2)
                    with a1:
                        new_statut = st.selectbox("Nouveau statut", STATUTS, index=STATUTS.index(ticket["statut"]))
                        new_priorite = st.selectbox(
                            "Priorité",
                            [""] + PRIORITES,
                            index=([""] + PRIORITES).index(ticket["priorite"] if ticket["priorite"] in PRIORITES else ""),
                        )
                        assigne_a = st.text_input("Assigner à", value=ticket["assigne_a"] or "")
                    with a2:
                        dispatcheur = st.text_input("Dispatcheur", value=ticket["dispatcheur"] or "")
                        ticket_maitre_id = st.text_input("Ticket maître (si doublon)", value=ticket["ticket_maitre_id"] or "")
                        motif_resolution = st.text_input("Motif de résolution", value=ticket["motif_resolution"] or "")

                    if st.button("Enregistrer les changements"):
                        payload = {
                            "statut": new_statut,
                            "priorite": new_priorite or None,
                            "assigne_a": assigne_a or None,
                            "dispatcheur": dispatcheur or None,
                            "ticket_maitre_id": int(ticket_maitre_id) if str(ticket_maitre_id).strip().isdigit() else None,
                            "motif_resolution": motif_resolution or None,
                        }
                        if new_statut == "Clôturé":
                            if not motif_resolution.strip():
                                st.error("Le motif de résolution est obligatoire pour clôturer.")
                            else:
                                payload["closed_at"] = now_iso()
                                update_ticket(selected_ticket_id, current_user, **payload)
                                st.success("Ticket clôturé et mis à jour.")
                                st.info("Notification simulée : demandeur notifié à la clôture.")
                                st.rerun()
                        else:
                            update_ticket(selected_ticket_id, current_user, **payload)
                            st.success("Ticket mis à jour.")
                            if assigne_a:
                                st.info("Notification simulée : preneur notifié à l'attribution.")
                            st.rerun()

                    st.markdown("### Commentaires")
                    comments_df = get_comments(selected_ticket_id)
                    if comments_df.empty:
                        st.caption("Aucun commentaire.")
                    else:
                        for _, row in comments_df.iterrows():
                            with st.container(border=True):
                                st.write(f"**{row['auteur']}** — {row['created_at']}")
                                st.write(row['contenu'])

                    new_comment = st.text_area("Ajouter un commentaire", key=f"comment_{selected_ticket_id}")
                    if st.button("Publier le commentaire"):
                        if new_comment.strip():
                            add_comment(selected_ticket_id, current_user, new_comment.strip())
                            st.success("Commentaire ajouté.")
                            st.rerun()

                    st.markdown("### Journalisation")
                    logs_df = get_logs(selected_ticket_id)
                    st.dataframe(logs_df, use_container_width=True, hide_index=True)

with onglet3:
    st.subheader("Tableau de bord minimal")
    df = get_tickets()
    metrics = compute_dashboard(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tickets", metrics["total"])
    c2.metric("Infra", metrics["infra"])
    c3.metric("Numérique", metrics["numerique"])
    c4.metric("Doublons", metrics["doublons"])
    c5.metric("% > 7 jours", metrics["pct_en_cours_7j"])

    if metrics["temps_moyen_h"] is not None:
        st.metric("Temps moyen de résolution (h)", metrics["temps_moyen_h"])

    if not df.empty:
        st.markdown("### Répartition par type")
        st.bar_chart(df["typage"].value_counts())

        st.markdown("### Répartition par statut")
        st.bar_chart(df["statut"].value_counts())

        st.markdown("### Tickets par mois")
        df_copy = df.copy()
        df_copy["mois"] = pd.to_datetime(df_copy["created_at"], errors="coerce").dt.to_period("M").astype(str)
        monthly = df_copy.groupby(["mois", "typage"]).size().unstack(fill_value=0)
        st.line_chart(monthly)

        st.markdown("### Top récurrences (mots du titre)")
        stopwords = {"de", "du", "la", "le", "les", "des", "et", "en", "pour", "sur", "dans", "a", "au"}
        words = []
        for titre_item in df_copy["titre"].fillna(""):
            for word in titre_item.lower().replace("/", " ").replace("-", " ").split():
                cleaned = word.strip(" ,.;:!?()[]{}'\"")
                if len(cleaned) > 3 and cleaned not in stopwords:
                    words.append(cleaned)
        if words:
            top_words = pd.Series(words).value_counts().head(5)
            st.dataframe(top_words.rename_axis("mot").reset_index(name="occurrences"), hide_index=True)

with onglet4:
    st.subheader("Administration légère")
    df = get_tickets()
    st.download_button(
        "Exporter les tickets en CSV",
        data=export_csv(df),
        file_name="tickets_export.csv",
        mime="text/csv",
    )

    st.markdown("### Périmètre démo")
    st.write("- Authentification simulée par sélection de rôle")
    st.write("- Notifications simulées à l'écran")
    st.write("- Base SQLite locale")
    st.write("- Anti-doublon basé sur similarité simple + récence")
    st.write("- Responsive correct pour une démo web, pas une app mobile native")

    if st.button("Réinitialiser la base de démo"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        for file in UPLOAD_DIR.glob("*"):
            try:
                file.unlink()
            except OSError:
                pass
        st.success("Base supprimée. Relancez l'application.")

st.markdown("---")
st.caption("MVP de démonstration — à industrialiser avant usage réel (authentification, RGPD, SaaS, notifications email, hébergement UE)")
