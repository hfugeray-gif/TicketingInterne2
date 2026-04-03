import os
import streamlit as st
import pandas as pd

from core.auth import ensure_logged_in, get_current_role, get_current_user, logout, can_access_backoffice
from core.config import PRIORITES, TYPES, SITES
from core.styles import apply_global_styles, render_header
from core.api_tickets import (
    api_add_comment,
    api_get_child_tickets,
    api_get_comments,
    api_get_journal,
    api_get_ticket,
    api_get_tickets,
)

# --------------------------------------------------
# ⚙️ Configuration générale de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Mes tickets — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Vérifie que l'utilisateur est bien passé par l'accueil
ensure_logged_in()

# Applique le style global et l'en-tête
apply_global_styles()
render_header()




# --------------------------------------------------
# 📌 Titre de la page
# --------------------------------------------------
st.subheader("Mes tickets")


# --------------------------------------------------
# 🧠 Initialisation de l'état de session
# --------------------------------------------------
# Cette clé permet de mémoriser le ticket actuellement sélectionné
# entre deux reruns Streamlit.
if "selected_my_ticket_id" not in st.session_state:
    st.session_state.selected_my_ticket_id = None


# --------------------------------------------------
# 📥 Chargement et filtrage des tickets utilisateur
# --------------------------------------------------
tickets_data = api_get_tickets()
df = pd.DataFrame(tickets_data) if tickets_data else pd.DataFrame()
current_user = get_current_user()

if not df.empty:
    # 1. Tickets directement liés à l'utilisateur
    user_df = df[
        (df["demandeur"].fillna("") == current_user)
        | (df["assigne_a"].fillna("") == current_user)
    ].copy()

    # 2. On récupère les IDs des tickets maîtres pour les tickets esclaves
    master_ids = (
        user_df["ticket_maitre_id"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    # 3. On retire les tickets esclaves de la liste utilisateur
    user_df = user_df[user_df["ticket_maitre_id"].isna()].copy()

    # 4. On ajoute les tickets maîtres correspondants
    if master_ids:
        master_df = df[df["id"].isin(master_ids)].copy()
        df = pd.concat([user_df, master_df], ignore_index=True)
        df = df.drop_duplicates(subset=["id"])
    else:
        df = user_df


# --------------------------------------------------
# ℹ️ Cas sans ticket
# --------------------------------------------------
if df.empty:
    st.info("Aucun ticket lié à cet utilisateur pour le moment.")
    st.stop()


# --------------------------------------------------
# 🔎 Filtres de consultation
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    filtre_type = st.selectbox("Type", ["Tous"] + TYPES)

with col2:
    filtre_priorite = st.selectbox("Priorité", ["Toutes"] + PRIORITES)

with col3:
    filtre_texte = st.text_input("Recherche")


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


# --------------------------------------------------
# 🧭 Sélection automatique d'un ticket si besoin
# --------------------------------------------------
# Si aucun ticket n'est sélectionné, on prend le premier ticket filtré.
if st.session_state.selected_my_ticket_id is None and not filtered.empty:
    st.session_state.selected_my_ticket_id = int(filtered.iloc[0]["id"])


# Si le ticket sélectionné n'est plus dans le filtre courant,
# on bascule sur le premier ticket disponible.
available_ids = filtered["id"].tolist()
if available_ids and st.session_state.selected_my_ticket_id not in available_ids:
    st.session_state.selected_my_ticket_id = int(available_ids[0])


# --------------------------------------------------
# 🧱 Mise en page : liste à gauche / détail à droite
# --------------------------------------------------
left_panel, right_panel = st.columns([1.05, 1.75], gap="large")


# --------------------------------------------------
# 📋 Colonne de gauche : liste des tickets
# --------------------------------------------------
with left_panel:
    st.markdown("### Tickets")

    if filtered.empty:
        st.info("Aucun ticket ne correspond aux filtres.")
    else:
        for _, row in filtered.iterrows():
            is_selected = st.session_state.selected_my_ticket_id == int(row["id"])

            # Couleur d'accent selon le statut
            accent_color = {
                "Ouvert": "#004034",
                "En cours": "#004034",
                "Clôturé": "#004034",
                "Doublon": "#004034",
            }.get(row["statut"], "#004034")

            # Carte visuelle du ticket
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
                        {row['typage']} · {row['site'] if pd.notna(row['site']) and row['site'] else '-'} · {row['statut']} · {row['priorite'] if pd.notna(row['priorite']) and row['priorite'] else 'Sans priorité'}
                    </div>
                    <div style="color: #6b7c93; font-size: 0.85rem;">
                        Demandeur : {row['demandeur']} · Assigné : {row['assigne_a'] if pd.notna(row['assigne_a']) and row['assigne_a'] else '-'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Action d'ouverture du détail
            if st.button(
                "Ouvrir" if not is_selected else "Sélectionné",
                key=f"open_my_ticket_{int(row['id'])}",
                use_container_width=True,
                disabled=is_selected,
            ):
                st.session_state.selected_my_ticket_id = int(row["id"])
                st.rerun()


# --------------------------------------------------
# 📄 Colonne de droite : détail du ticket sélectionné
# --------------------------------------------------
with right_panel:
    selected_ticket_id = st.session_state.selected_my_ticket_id

    if selected_ticket_id is None or selected_ticket_id not in filtered["id"].tolist():
        st.info("Sélectionne un ticket à gauche pour afficher son détail.")
    else:
        ticket = api_get_ticket(selected_ticket_id)

        if ticket:
            st.markdown("### Détail du ticket")

            left, right = st.columns([2, 1])

            with left:
                st.write(f"**Titre** : {ticket['titre']}")
                st.write(f"**Type** : {ticket['typage']}")
                st.write(f"**Site** : {ticket['site'] or '-'}")
                st.write(f"**Statut** : {ticket['statut']}")
                st.write(f"**Priorité** : {ticket['priorite'] or '-'}")
                st.write(f"**Demandeur** : {ticket['demandeur']}")
                st.write(f"**Assigné à** : {ticket['assigne_a'] or '-'}")
                st.write(f"**Commentaire initial** : {ticket['commentaire'] or '-'}")
                st.write(f"**Créé le** : {ticket['created_at']}")

                if ticket["motif_resolution"]:
                    st.write(f"**Motif de résolution** : {ticket['motif_resolution']}")

                if ticket["ticket_maitre_id"]:
                    st.write(f"**Ticket maître** : #{ticket['ticket_maitre_id']}")

            with right:
                photo_path = ticket.get("photo_path")

                if photo_path and os.path.exists(photo_path):
                    st.image(photo_path, caption="Photo jointe")

            # ------------------------------------------
            # 🔒 Zone d'information selon le profil
            # ------------------------------------------
            if can_access_backoffice():
                st.info(
                    "Tu disposes d'un profil interne. Le traitement complet des tickets "
                    "est disponible dans la page 'File de tickets'."
                )
            else:
                st.info(
                    "En profil Utilisateur, cette page permet la consultation et l'ajout "
                    "de commentaires sur tes tickets."
                )

            # ------------------------------------------
            # 💬 Commentaires
            # ------------------------------------------
            st.markdown("### Commentaires")

            comments_data = api_get_comments(selected_ticket_id)
            comments_df = pd.DataFrame(comments_data) if comments_data else pd.DataFrame()

            if comments_df.empty:
                st.caption("Aucun commentaire.")
            else:
                for _, row in comments_df.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row['auteur']}** — {row['created_at']}")
                        st.write(row["contenu"])

            comment_key = f"comment_my_ticket_{selected_ticket_id}"
            comment_reset_key = f"{comment_key}_reset"

            if st.session_state.get(comment_reset_key):
                st.session_state[comment_key] = ""
                st.session_state[comment_reset_key] = False

            new_comment = st.text_area(
                "Ajouter un commentaire",
                key=comment_key,
            )

            if st.button("Publier le commentaire"):
                if new_comment.strip():
                    try:
                        api_add_comment(
                            selected_ticket_id,
                            current_user,
                            new_comment.strip(),
                        )

                        st.session_state[comment_reset_key] = True
                        st.success("Commentaire ajouté.")
                        st.rerun()
                    except RuntimeError as e:
                        st.error(str(e))

            # ------------------------------------------
            # 🧾 Journalisation
            # ------------------------------------------
            st.markdown("### Journalisation")

            logs_data = api_get_journal(selected_ticket_id)
            logs_df = pd.DataFrame(logs_data) if logs_data else pd.DataFrame()
            st.dataframe(logs_df, use_container_width=True, hide_index=True)