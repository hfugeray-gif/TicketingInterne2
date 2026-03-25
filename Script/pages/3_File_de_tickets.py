import os
import streamlit as st
import pandas as pd

from core.auth import require_backoffice_access, get_current_role, get_current_user, logout
from core.config import PRIORITES, STATUTS, TYPES
from core.styles import apply_global_styles, render_header
from core.tickets import (
    add_comment,
    get_comments,
    get_logs,
    get_ticket,
    get_tickets,
    update_ticket,
)
from core.db import now_iso


# --------------------------------------------------
# ⚙️ Configuration générale de la page
# --------------------------------------------------
st.set_page_config(
    page_title="File de tickets — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Vérifie que l'utilisateur est connecté ET autorisé à accéder au backoffice
require_backoffice_access()

# Applique le style global et l'en-tête
apply_global_styles()
render_header()

# --------------------------------------------------
# 🎨 Ajustements CSS spécifiques à cette page
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Tabs de cette page */
    div[data-testid="stTabs"] button[role="tab"] {
        border-bottom: 2px solid transparent !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    div[data-testid="stTabs"] button[role="tab"]::before,
    div[data-testid="stTabs"] button[role="tab"]::after {
        content: none !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #004034 !important;
        border-bottom: 3px solid #004034 !important;
        box-shadow: none !important;
    }

    div[data-testid="stTabs"] button[role="tab"]:hover {
        color: #004034 !important;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-border"],
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Boutons de la file : noir direct */
    div.stButton > button:not(:disabled) {
        background: #111111 !important;
        background-image: none !important;
        color: white !important;
        border: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 0.55rem 1rem !important;
        margin-top: -6px !important;
        margin-bottom: 18px !important;
        box-shadow: none !important;
        opacity: 1 !important;
        -webkit-text-fill-color: white !important;
    }

    div.stButton > button:not(:disabled) * {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    div.stButton > button:not(:disabled):hover {
        background: #000000 !important;
        background-image: none !important;
        color: white !important;
    }

    div.stButton > button:not(:disabled):hover * {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    div.stButton > button:not(:disabled):focus,
    div.stButton > button:not(:disabled):focus:not(:active) {
        background: #111111 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 0 0 0.2rem rgba(0, 0, 0, 0.15) !important;
        -webkit-text-fill-color: white !important;
    }

    div.stButton > button:not(:disabled):active {
        background: #000000 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Etat passif pour le ticket sélectionné */
    .ticket-selected-state {
        width: 100%;
        background: #e5e7eb;
        color: #6b7280;
        border: 1px solid #d1d5db;
        border-radius: 0 0 12px 12px;
        text-align: center;
        padding: 10px 12px;
        margin-top: -6px;
        margin-bottom: 18px;
        font-weight: 600;
        box-sizing: border-box;
    }
    </style>
    """,
    unsafe_allow_html=True,
)




# --------------------------------------------------
# 📌 Titre de la page
# --------------------------------------------------
st.subheader("Vue opérationnelle")


# --------------------------------------------------
# 🧠 Initialisation de l'état de session
# --------------------------------------------------
if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None


# --------------------------------------------------
# 📥 Chargement des tickets
# --------------------------------------------------
df = get_tickets()

if df.empty:
    st.info("Aucun ticket pour le moment.")
    st.stop()


# --------------------------------------------------
# 🔎 Filtres opérationnels
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    filtre_type = st.selectbox("Type", ["Tous"] + TYPES)

with col2:
    filtre_priorite = st.selectbox("Priorité", ["Toutes"] + PRIORITES)

with col3:
    filtre_texte = st.text_input("Recherche")

with col4:
    only_mine = st.checkbox("Mes tickets uniquement")


filtered = df.copy()

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

if only_mine:
    current_user = get_current_user()
    filtered = filtered[
        (filtered["demandeur"].fillna("") == current_user)
        | (filtered["assigne_a"].fillna("") == current_user)
    ]


# --------------------------------------------------
# 🧭 Sélection automatique d'un ticket
# --------------------------------------------------
if st.session_state.selected_ticket_id is None and not filtered.empty:
    st.session_state.selected_ticket_id = int(filtered.iloc[0]["id"])

available_ids = filtered["id"].tolist()
if available_ids and st.session_state.selected_ticket_id not in available_ids:
    st.session_state.selected_ticket_id = int(available_ids[0])


# --------------------------------------------------
# 🧱 Mise en page : liste à gauche / détail à droite
# --------------------------------------------------
left_panel, right_panel = st.columns([1.05, 1.75], gap="large")


# --------------------------------------------------
# 📋 Colonne de gauche : onglets de tickets
# --------------------------------------------------
with left_panel:
    st.markdown("### Tickets")

    section_map = {
        "Ouvert": filtered[filtered["statut"] == "Ouvert"],
        "En cours": filtered[filtered["statut"] == "En cours"],
        "Clôturé": filtered[filtered["statut"] == "Clôturé"],
    }

    tab_open, tab_progress, tab_closed = st.tabs(["Ouverts", "En cours", "Clôturés"])

    def render_ticket_list(section_df, accent_color):
        """
        Affiche une liste de tickets sous forme de cartes,
        avec une action d'ouverture.
        Le ticket sélectionné est remonté en tête de liste.
        """
        if section_df.empty:
            st.caption("Aucun ticket dans cette section.")
            return

        section_df = section_df.copy()
        section_df["is_selected"] = (
            section_df["id"].astype(int) == int(st.session_state.selected_ticket_id)
        )
        section_df = section_df.sort_values(
            by=["is_selected", "created_at"],
            ascending=[False, False],
        ).drop(columns=["is_selected"])

        for _, row in section_df.iterrows():
            is_selected = st.session_state.selected_ticket_id == int(row["id"])

            st.markdown(
                f"""
                <div style="
                    background: rgba(255,255,255,0.78);
                    border: 1px solid {'#0f4c81' if is_selected else '#d9e2f2'};
                    border-left: 5px solid {accent_color};
                    border-radius: 14px;
                    padding: 12px 14px;
                    margin-bottom: 6px;
                    box-shadow: {'0 8px 20px rgba(15,76,129,0.12)' if is_selected else 'none'};
                ">
                    <div style="font-weight: 700; color: #12344d; font-size: 1rem; margin-bottom: 4px;">
                        #{int(row['id'])} — {row['titre']}
                    </div>
                    <div style="color: #486581; font-size: 0.92rem; margin-bottom: 6px;">
                        {row['typage']} · {row['priorite'] if pd.notna(row['priorite']) and row['priorite'] else 'Sans priorité'}
                    </div>
                    <div style="color: #6b7c93; font-size: 0.85rem;">
                        Demandeur : {row['demandeur']} · Assigné : {row['assigne_a'] if pd.notna(row['assigne_a']) and row['assigne_a'] else '-'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if is_selected:
                st.markdown(
                    '<div class="ticket-selected-state">Sélectionné</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(
                    "Ouvrir",
                    key=f"open_ticket_{accent_color}_{int(row['id'])}",
                    use_container_width=True,
                ):
                    st.session_state.selected_ticket_id = int(row["id"])
                    st.rerun()

    with tab_open:
        render_ticket_list(section_map["Ouvert"], "#004034")

    with tab_progress:
        render_ticket_list(section_map["En cours"], "#004034")

    with tab_closed:
        render_ticket_list(section_map["Clôturé"], "#004034")


# --------------------------------------------------
# 📄 Colonne de droite : détail + actions
# --------------------------------------------------
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
                new_statut = st.selectbox(
                    "Nouveau statut",
                    STATUTS,
                    index=STATUTS.index(ticket["statut"]),
                )

                new_priorite = st.selectbox(
                    "Priorité",
                    [""] + PRIORITES,
                    index=([""] + PRIORITES).index(
                        ticket["priorite"] if ticket["priorite"] in PRIORITES else ""
                    ),
                )

                assigne_a = st.text_input("Assigner à", value=ticket["assigne_a"] or "")

            with a2:
                dispatcheur = st.text_input("Dispatcheur", value=ticket["dispatcheur"] or "")
                ticket_maitre_id = st.text_input(
                    "Ticket maître (si doublon)",
                    value=ticket["ticket_maitre_id"] or "",
                )
                motif_resolution = st.text_input(
                    "Motif de résolution",
                    value=ticket["motif_resolution"] or "",
                )

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
                        update_ticket(selected_ticket_id, get_current_user(), **payload)
                        st.success("Ticket clôturé et mis à jour.")
                        st.info("Notification simulée : demandeur notifié à la clôture.")
                        st.rerun()
                else:
                    update_ticket(selected_ticket_id, get_current_user(), **payload)
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
                        st.write(row["contenu"])

            new_comment = st.text_area(
                "Ajouter un commentaire",
                key=f"comment_{selected_ticket_id}",
            )

            if st.button("Publier le commentaire"):
                if new_comment.strip():
                    add_comment(selected_ticket_id, get_current_user(), new_comment.strip())
                    st.success("Commentaire ajouté.")
                    st.rerun()

            st.markdown("### Journalisation")

            logs_df = get_logs(selected_ticket_id)
            st.dataframe(logs_df, use_container_width=True, hide_index=True)