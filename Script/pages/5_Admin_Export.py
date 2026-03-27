import os
import streamlit as st

from core.auth import require_backoffice_access
from core.config import DB_PATH, UPLOAD_DIR, TYPES
from core.styles import apply_global_styles, render_header
from core.tickets import export_csv
from core.admin_query_service import ALLOWED_TABLES, run_select_query
from core.app_config_service import (
    get_subtypes_config,
    add_subtype,
    update_subtype,
    delete_subtype,
    get_pages_config,
    update_page_config,
)


# --------------------------------------------------
# ⚙️ Configuration générale
# --------------------------------------------------
st.set_page_config(
    page_title="Admin / Export — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_backoffice_access()
apply_global_styles()
render_header()

st.markdown(
    """
    <style>
    /* Boutons spécifiques à la page admin :
       form_submit_button + download_button + button standard */
    div.stFormSubmitButton > button,
    div.stDownloadButton > button,
    div.stButton > button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    div.stFormSubmitButton > button *,
    div.stDownloadButton > button *,
    div.stButton > button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    div.stFormSubmitButton > button:hover,
    div.stDownloadButton > button:hover,
    div.stButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    div.stFormSubmitButton > button:hover *,
    div.stDownloadButton > button:hover *,
    div.stButton > button:hover * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    div.stFormSubmitButton > button:focus,
    div.stDownloadButton > button:focus,
    div.stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(0,0,0,0.15) !important;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.subheader("Administration")

tab_db, tab_param = st.tabs(["Base de données", "Paramétrage"])


# ==================================================
# ONGLET 1 — BASE DE DONNÉES
# ==================================================
with tab_db:
    st.markdown("### Consultation de la base")
    st.write("Interrogation en lecture seule, sans SQL en front.")

    table = st.selectbox("Table source", list(ALLOWED_TABLES.keys()))
    available_columns = ALLOWED_TABLES[table]

    selected_columns = st.multiselect(
        "Colonnes à afficher",
        available_columns,
        default=available_columns[: min(6, len(available_columns))],
    )

    st.markdown("#### Filtres")

    filters = {}
    col1, col2, col3 = st.columns(3)

    with col1:
        if table == "tickets":
            filters["statut"] = st.multiselect(
                "Statut",
                ["Ouvert", "En cours", "Clôturé", "Doublon"],
            )
            filters["typage"] = st.multiselect("Type", TYPES)
            filters["priorite"] = st.multiselect(
                "Priorité",
                ["Basse", "Normale", "Haute"],
            )
        elif table == "commentaires":
            filters["auteur"] = st.text_input("Auteur")
        elif table == "journal":
            filters["action"] = st.text_input("Action")

    with col2:
        if table == "tickets":
            filters["demandeur"] = st.text_input("Demandeur")
            filters["assigne_a"] = st.text_input("Assigné à")
            filters["dispatcheur"] = st.text_input("Dispatcheur")
        else:
            filters["ticket_id"] = st.text_input("Ticket ID")

    with col3:
        filters["search_text"] = st.text_input("Texte contient")
        filters["date_from"] = st.text_input("Date min (YYYY-MM-DD)")
        filters["date_to"] = st.text_input("Date max (YYYY-MM-DD)")

    st.markdown("#### Tri et limite")
    t1, t2, t3 = st.columns([2, 1, 1])

    with t1:
        order_by = st.selectbox("Trier par", [""] + available_columns)

    with t2:
        order_dir = st.radio("Sens", ["DESC", "ASC"], horizontal=True)

    with t3:
        limit = st.number_input("Limite", min_value=10, max_value=1000, value=100, step=10)

    if st.button("Lancer la requête", type="primary", key="run_admin_query"):
        try:
            df = run_select_query(
                table=table,
                selected_columns=selected_columns,
                filters=filters,
                order_by=order_by or None,
                order_dir=order_dir,
                limit=limit,
            )

            st.markdown("#### Résultats")
            st.dataframe(df, use_container_width=True, hide_index=True)

            if df.empty:
                st.info("Aucun résultat.")
            else:
                st.download_button(
                    "Exporter en CSV",
                    data=export_csv(df),
                    file_name=f"{table}_export.csv",
                    mime="text/csv",
                    key="download_admin_query_csv",
                )

        except Exception as e:
            st.error(f"Erreur lors de l'exécution : {e}")

    st.markdown("---")
    st.markdown("### Réinitialisation")
    st.warning(
        "Cette action supprime la base SQLite locale ainsi que les fichiers uploadés."
    )

    if st.button("Réinitialiser la base de démo", key="reset_demo_db"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        for file in UPLOAD_DIR.glob("*"):
            try:
                file.unlink()
            except OSError:
                pass

        st.success("Base supprimée. Relance l'application.")


# ==================================================
# ONGLET 2 — PARAMÉTRAGE
# ==================================================
with tab_param:
    st.markdown("### Paramétrage applicatif")

    subtab_ref, subtab_nav = st.tabs(["Référentiels", "Navigation"])

    # ----------------------------------------------
    # Sous-onglet Référentiels
    # ----------------------------------------------
    with subtab_ref:
        st.markdown("#### Gestion des sous-types")

        with st.form("add_subtype_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_type_parent = st.selectbox("Type parent", TYPES)
            with c2:
                new_subtype_label = st.text_input("Libellé du sous-type")
            with c3:
                new_display_order = st.number_input("Ordre", min_value=1, value=1, step=1)

            submitted_add_subtype = st.form_submit_button("Ajouter le sous-type")

            if submitted_add_subtype:
                if not new_subtype_label.strip():
                    st.error("Le libellé est obligatoire.")
                else:
                    add_subtype(
                        type_parent=new_type_parent,
                        label=new_subtype_label.strip(),
                        display_order=int(new_display_order),
                    )
                    st.success("Sous-type ajouté.")
                    st.rerun()

        st.markdown("#### Sous-types existants")
        subtypes_df = get_subtypes_config()

        if subtypes_df.empty:
            st.info("Aucun sous-type configuré.")
        else:
            for _, row in subtypes_df.iterrows():
                with st.expander(f"{row['type_parent']} — {row['label']}"):
                    e1, e2, e3 = st.columns([2, 1, 1])

                    with e1:
                        edit_label = st.text_input(
                            "Libellé",
                            value=row["label"],
                            key=f"subtype_label_{row['id']}",
                        )

                    with e2:
                        edit_order = st.number_input(
                            "Ordre",
                            min_value=1,
                            value=int(row["display_order"]),
                            step=1,
                            key=f"subtype_order_{row['id']}",
                        )

                    with e3:
                        edit_active = st.checkbox(
                            "Actif",
                            value=bool(row["is_active"]),
                            key=f"subtype_active_{row['id']}",
                        )

                    a1, a2 = st.columns(2)

                    with a1:
                        if st.button("Enregistrer", key=f"save_subtype_{row['id']}", use_container_width=True):
                            update_subtype(
                                subtype_id=int(row["id"]),
                                label=edit_label.strip(),
                                display_order=int(edit_order),
                                is_active=edit_active,
                            )
                            st.success("Sous-type mis à jour.")
                            st.rerun()

                    with a2:
                        if st.button("Supprimer", key=f"delete_subtype_{row['id']}", use_container_width=True):
                            delete_subtype(int(row["id"]))
                            st.success("Sous-type supprimé.")
                            st.rerun()

    # ----------------------------------------------
    # Sous-onglet Navigation
    # ----------------------------------------------
    with subtab_nav:
        st.markdown("#### Gestion des pages")

        pages_df = get_pages_config()

        if pages_df.empty:
            st.info("Aucune page configurée.")
        else:
            st.caption(
                "Les changements enregistrés ici nécessitent que `app.py` lise la table "
                "`app_pages_config` pour piloter l’ordre et la visibilité."
            )

            for _, row in pages_df.iterrows():
                with st.expander(f"{row['page_key']} — {row['label']}"):
                    n1, n2, n3 = st.columns([2, 1, 1])

                    with n1:
                        page_label = st.text_input(
                            "Libellé",
                            value=row["label"],
                            key=f"page_label_{row['id']}",
                        )

                    with n2:
                        page_icon = st.text_input(
                            "Icône",
                            value=row["icon"] or "",
                            key=f"page_icon_{row['id']}",
                        )

                    with n3:
                        page_order = st.number_input(
                            "Ordre",
                            min_value=1,
                            value=int(row["display_order"]),
                            step=1,
                            key=f"page_order_{row['id']}",
                        )

                    page_visible = st.checkbox(
                        "Visible",
                        value=bool(row["is_visible"]),
                        key=f"page_visible_{row['id']}",
                    )

                    if st.button("Enregistrer la page", key=f"save_page_{row['id']}", use_container_width=True):
                        update_page_config(
                            page_id=int(row["id"]),
                            label=page_label.strip(),
                            icon=page_icon.strip(),
                            display_order=int(page_order),
                            is_visible=page_visible,
                        )
                        st.success("Page mise à jour.")
                        st.rerun()