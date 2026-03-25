import pandas as pd
import plotly.express as px
import streamlit as st

from core.auth import require_backoffice_access, get_current_role, get_current_user, logout
from core.styles import apply_global_styles, render_header
from core.tickets import get_tickets


# --------------------------------------------------
# ⚙️ Configuration générale de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Pilotage — Ticketing interne",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Vérifie que l'utilisateur est connecté ET autorisé à accéder au backoffice
require_backoffice_access()

# Applique le style global et l'en-tête
apply_global_styles()
render_header()


# --------------------------------------------------
# 🎨 Style complémentaire spécifique au pilotage
# --------------------------------------------------
st.markdown(
    """
    <style>
        .pilot-card {
            background: rgba(255,255,255,0.62);
            border: 1px solid #d9e2f2;
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 14px;
            backdrop-filter: blur(6px);
        }

        .pilot-card h3 {
            margin: 0 0 8px 0;
            color: #12344d;
            font-size: 1.05rem;
        }

        .pilot-card p {
            margin: 0;
            color: #486581;
        }

        .kpi-box {
            background: rgba(255,255,255,0.82);
            border: 1px solid #d9e2f2;
            border-radius: 18px;
            padding: 14px 16px;
            min-height: 110px;
            backdrop-filter: blur(6px);
            margin-bottom: 12px;
        }

        .kpi-label {
            color: #486581;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }

        .kpi-value {
            color: #12344d;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .kpi-sub {
            color: #6b7c93;
            font-size: 0.85rem;
            margin-top: 8px;
        }

        .chart-card {
            background: rgba(255,255,255,0.58);
            border: 1px solid #d9e2f2;
            border-radius: 18px;
            padding: 14px 16px 8px 16px;
            margin-bottom: 16px;
            backdrop-filter: blur(6px);
        }

        .chart-title {
            font-weight: 700;
            color: #12344d;
            margin-bottom: 8px;
            font-size: 1.05rem;
        }

        .alert-box {
            border-radius: 14px;
            padding: 12px 14px;
            margin-bottom: 10px;
            border: 1px solid;
            background: rgba(255,255,255,0.82);
        }

        .alert-high {
            border-color: #ef4444;
        }

        .alert-medium {
            border-color: #f59e0b;
        }

        .mini-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 6px;
        }

        .badge-open { background: rgba(217,119,6,0.12); color: #b45309; }
        .badge-progress { background: rgba(15,76,129,0.12); color: #0f4c81; }
        .badge-closed { background: rgba(45,106,79,0.12); color: #2d6a4f; }
        .badge-dup { background: rgba(124,58,237,0.12); color: #6d28d9; }
    </style>
    """,
    unsafe_allow_html=True,
)



# --------------------------------------------------
# 🎨 Couleurs de référence
# --------------------------------------------------
COLOR_PRIMARY = "#0f4c81"
COLOR_OPEN = "#d97706"
COLOR_PROGRESS = "#0f4c81"
COLOR_CLOSED = "#2d6a4f"
COLOR_DUP = "#6d28d9"
COLOR_TEXT = "#12344d"
COLOR_MUTED = "#486581"

STATUS_COLOR_MAP = {
    "Ouvert": COLOR_OPEN,
    "En cours": COLOR_PROGRESS,
    "Clôturé": COLOR_CLOSED,
    "Doublon": COLOR_DUP,
}

TYPE_COLOR_MAP = {
    "Infra": "#0f4c81",
    "Numérique": "#7c3aed",
}

PRIORITY_COLOR_MAP = {
    "Haute": "#dc2626",
    "Normale": "#0f4c81",
    "Basse": "#2d6a4f",
    "Non renseignée": "#94a3b8",
}


# --------------------------------------------------
# 🧰 Helpers graphiques Plotly
# --------------------------------------------------
def apply_plotly_layout(fig, height=340, show_legend=False):
    """
    Applique un style homogène à tous les graphiques Plotly.
    """
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=show_legend,
        font=dict(color=COLOR_TEXT),
        xaxis=dict(
            title=None,
            showgrid=False,
            zeroline=False,
            linecolor="rgba(0,0,0,0)",
            tickfont=dict(color=COLOR_MUTED),
        ),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(15,76,129,0.08)",
            zeroline=False,
            tickfont=dict(color=COLOR_MUTED),
        ),
    )
    return fig


def render_chart_card(title, fig):
    """
    Affiche un graphique dans une carte cohérente avec le design global.
    """
    with st.container():
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# 📥 Chargement des données
# --------------------------------------------------
st.subheader("Pilotage avancé")

df = get_tickets()

if df.empty:
    st.info("Aucun ticket disponible pour alimenter le pilotage.")
    st.stop()


# --------------------------------------------------
# 🧹 Préparation des données
# --------------------------------------------------
df = df.copy()
df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
df["updated_dt"] = pd.to_datetime(df["updated_at"], errors="coerce")
df["closed_dt"] = pd.to_datetime(df["closed_at"], errors="coerce")

today = pd.Timestamp.now()

# Âge du ticket en jours
df["age_days"] = (today - df["created_dt"]).dt.days

# Temps de résolution en heures
df["resolution_hours"] = (df["closed_dt"] - df["created_dt"]).dt.total_seconds() / 3600

# Backlog = tickets non clôturés
df["is_backlog"] = df["statut"].isin(["Ouvert", "En cours"])

# Tickets anciens
df["is_old_backlog"] = df["is_backlog"] & (df["age_days"] > 7)
df["is_very_old_backlog"] = df["is_backlog"] & (df["age_days"] > 14)

# Classes d'ancienneté
def age_bucket(days):
    if pd.isna(days):
        return "Inconnu"
    if days <= 2:
        return "0-2 jours"
    if days <= 7:
        return "3-7 jours"
    if days <= 14:
        return "8-14 jours"
    return "15+ jours"

df["age_bucket"] = df["age_days"].apply(age_bucket)

# Mois de création
df["mois"] = df["created_dt"].dt.to_period("M").astype(str)


# --------------------------------------------------
# 🔎 Filtres globaux
# --------------------------------------------------
st.markdown("### Filtres")

f1, f2, f3, f4 = st.columns(4)

with f1:
    filtre_type = st.selectbox(
        "Type",
        ["Tous"] + sorted(df["typage"].dropna().unique().tolist())
    )

with f2:
    filtre_statut = st.selectbox(
        "Statut",
        ["Tous", "Ouvert", "En cours", "Clôturé", "Doublon"]
    )

with f3:
    priorites = sorted([p for p in df["priorite"].dropna().unique().tolist() if p])
    filtre_priorite = st.selectbox("Priorité", ["Toutes"] + priorites)

with f4:
    filtre_mine = st.checkbox("Uniquement mes tickets")

filtered = df.copy()

if filtre_type != "Tous":
    filtered = filtered[filtered["typage"] == filtre_type]

if filtre_statut != "Tous":
    filtered = filtered[filtered["statut"] == filtre_statut]

if filtre_priorite != "Toutes":
    filtered = filtered[filtered["priorite"] == filtre_priorite]

if filtre_mine:
    current_user = get_current_user()
    filtered = filtered[
        (filtered["demandeur"].fillna("") == current_user)
        | (filtered["assigne_a"].fillna("") == current_user)
    ]

if filtered.empty:
    st.warning("Aucun ticket ne correspond aux filtres sélectionnés.")
    st.stop()


# --------------------------------------------------
# 🧮 KPI enrichis
# --------------------------------------------------
total_tickets = len(filtered)
backlog_count = int(filtered["is_backlog"].sum())
open_count = int((filtered["statut"] == "Ouvert").sum())
progress_count = int((filtered["statut"] == "En cours").sum())
closed_count = int((filtered["statut"] == "Clôturé").sum())
duplicate_count = int((filtered["statut"] == "Doublon").sum())

backlog_rate = round((backlog_count / total_tickets) * 100, 1) if total_tickets else 0
duplicate_rate = round((duplicate_count / total_tickets) * 100, 1) if total_tickets else 0

resolved_df = filtered[filtered["statut"] == "Clôturé"].copy()
mean_resolution_h = round(resolved_df["resolution_hours"].dropna().mean(), 1) if not resolved_df.empty else None
median_resolution_h = round(resolved_df["resolution_hours"].dropna().median(), 1) if not resolved_df.empty else None

old_backlog_count = int(filtered["is_old_backlog"].sum())
very_old_backlog_count = int(filtered["is_very_old_backlog"].sum())

unassigned_backlog = int(
    filtered[
        filtered["is_backlog"]
        & (filtered["assigne_a"].isna() | (filtered["assigne_a"].fillna("") == ""))
    ].shape[0]
)

high_priority_open = int(
    filtered[
        filtered["is_backlog"] & (filtered["priorite"] == "Haute")
    ].shape[0]
)

closure_rate = round((closed_count / total_tickets) * 100, 1) if total_tickets else 0


# --------------------------------------------------
# 🧭 Bandeau de synthèse
# --------------------------------------------------
st.markdown(
    f"""
    <div class="pilot-card">
        <h3>Vue synthétique</h3>
        <p>
            <span class="mini-badge badge-open">Ouverts : {open_count}</span>
            <span class="mini-badge badge-progress">En cours : {progress_count}</span>
            <span class="mini-badge badge-closed">Clôturés : {closed_count}</span>
            <span class="mini-badge badge-dup">Doublons : {duplicate_count}</span>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 📌 KPI principaux
# --------------------------------------------------
st.markdown("### Indicateurs clés")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">Volume total</div>
            <div class="kpi-value">{total_tickets}</div>
            <div class="kpi-sub">Tickets après filtres</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">Backlog</div>
            <div class="kpi-value">{backlog_count}</div>
            <div class="kpi-sub">{backlog_rate}% du portefeuille</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">Clôture</div>
            <div class="kpi-value">{closure_rate}%</div>
            <div class="kpi-sub">{closed_count} tickets clôturés</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">Doublons</div>
            <div class="kpi-value">{duplicate_count}</div>
            <div class="kpi-sub">{duplicate_rate}% du volume</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k5:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">Résolution moyenne</div>
            <div class="kpi-value">{mean_resolution_h if mean_resolution_h is not None else "-"}</div>
            <div class="kpi-sub">Heures</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k6:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">Résolution médiane</div>
            <div class="kpi-value">{median_resolution_h if median_resolution_h is not None else "-"}</div>
            <div class="kpi-sub">Heures</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# 🚨 Alertes
# --------------------------------------------------
st.markdown("### Alertes et points d’attention")

a1, a2 = st.columns(2)

with a1:
    if very_old_backlog_count > 0:
        st.markdown(
            f"""
            <div class="alert-box alert-high">
                <strong>{very_old_backlog_count} ticket(s)</strong> non clôturé(s) depuis plus de 14 jours.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("Aucun ticket non clôturé de plus de 14 jours.")

    if high_priority_open > 0:
        st.markdown(
            f"""
            <div class="alert-box alert-medium">
                <strong>{high_priority_open} ticket(s)</strong> à priorité haute sont encore ouverts / en cours.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("Aucun ticket haute priorité en attente.")

with a2:
    if unassigned_backlog > 0:
        st.markdown(
            f"""
            <div class="alert-box alert-medium">
                <strong>{unassigned_backlog} ticket(s)</strong> du backlog ne sont pas assignés.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("Tous les tickets en attente sont assignés.")

    if old_backlog_count > 0:
        st.info(f"{old_backlog_count} ticket(s) non clôturé(s) ont plus de 7 jours.")
    else:
        st.success("Aucun ticket du backlog de plus de 7 jours.")


# --------------------------------------------------
# 📊 Visualisations principales
# --------------------------------------------------
col_v1, col_v2 = st.columns(2)

with col_v1:
    status_counts = (
        filtered["statut"]
        .value_counts()
        .rename_axis("statut")
        .reset_index(name="tickets")
    )

    fig_status = px.bar(
        status_counts,
        x="statut",
        y="tickets",
        color="statut",
        color_discrete_map=STATUS_COLOR_MAP,
    )
    fig_status.update_traces(marker_line_width=0, opacity=0.95)
    apply_plotly_layout(fig_status, height=320, show_legend=False)
    render_chart_card("Répartition par statut", fig_status)

with col_v2:
    type_counts = (
        filtered["typage"]
        .value_counts()
        .rename_axis("typage")
        .reset_index(name="tickets")
    )

    fig_type = px.bar(
        type_counts,
        x="typage",
        y="tickets",
        color="typage",
        color_discrete_map=TYPE_COLOR_MAP,
    )
    fig_type.update_traces(marker_line_width=0, opacity=0.95)
    apply_plotly_layout(fig_type, height=320, show_legend=False)
    render_chart_card("Répartition par type", fig_type)


col_v3, col_v4 = st.columns(2)

with col_v3:
    backlog_age = (
        filtered[filtered["is_backlog"]]
        .groupby("age_bucket")
        .size()
        .reindex(["0-2 jours", "3-7 jours", "8-14 jours", "15+ jours"], fill_value=0)
        .rename_axis("anciennete")
        .reset_index(name="tickets")
    )

    fig_age = px.bar(
        backlog_age,
        x="anciennete",
        y="tickets",
        color="anciennete",
        color_discrete_sequence=["#cbd5e1", "#93c5fd", "#fbbf24", "#f87171"],
    )
    fig_age.update_traces(marker_line_width=0, opacity=0.95)
    apply_plotly_layout(fig_age, height=320, show_legend=False)
    render_chart_card("Backlog par ancienneté", fig_age)

with col_v4:
    priority_counts = (
        filtered["priorite"]
        .fillna("Non renseignée")
        .value_counts()
        .rename_axis("priorite")
        .reset_index(name="tickets")
    )

    fig_priority = px.bar(
        priority_counts,
        x="priorite",
        y="tickets",
        color="priorite",
        color_discrete_map=PRIORITY_COLOR_MAP,
    )
    fig_priority.update_traces(marker_line_width=0, opacity=0.95)
    apply_plotly_layout(fig_priority, height=320, show_legend=False)
    render_chart_card("Répartition par priorité", fig_priority)


# --------------------------------------------------
# 📈 Tendance mensuelle
# --------------------------------------------------
monthly_total = (
    filtered.groupby("mois")
    .size()
    .rename_axis("mois")
    .reset_index(name="tickets")
)

fig_monthly = px.line(
    monthly_total,
    x="mois",
    y="tickets",
    markers=True,
)
fig_monthly.update_traces(line=dict(color=COLOR_PRIMARY, width=3))
apply_plotly_layout(fig_monthly, height=340, show_legend=False)
render_chart_card("Tendance mensuelle", fig_monthly)

monthly_by_type = (
    filtered.groupby(["mois", "typage"])
    .size()
    .reset_index(name="tickets")
)

fig_monthly_type = px.line(
    monthly_by_type,
    x="mois",
    y="tickets",
    color="typage",
    markers=True,
    color_discrete_map=TYPE_COLOR_MAP,
)
apply_plotly_layout(fig_monthly_type, height=340, show_legend=True)
render_chart_card("Détail mensuel par type", fig_monthly_type)


# --------------------------------------------------
# 👥 Analyse acteurs
# --------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    demandeurs = (
        filtered["demandeur"]
        .fillna("Inconnu")
        .value_counts()
        .head(10)
        .rename_axis("demandeur")
        .reset_index(name="tickets")
    )

    fig_demandeurs = px.bar(
        demandeurs,
        x="tickets",
        y="demandeur",
        orientation="h",
    )
    fig_demandeurs.update_traces(marker_color=COLOR_PRIMARY, marker_line_width=0, opacity=0.9)
    apply_plotly_layout(fig_demandeurs, height=360, show_legend=False)
    fig_demandeurs.update_yaxes(categoryorder="total ascending")
    render_chart_card("Top demandeurs", fig_demandeurs)

with c2:
    assigne = (
        filtered["assigne_a"]
        .fillna("Non assigné")
        .value_counts()
        .head(10)
        .rename_axis("assigne_a")
        .reset_index(name="tickets")
    )

    fig_assigne = px.bar(
        assigne,
        x="tickets",
        y="assigne_a",
        orientation="h",
    )
    fig_assigne.update_traces(marker_color="#7c3aed", marker_line_width=0, opacity=0.9)
    apply_plotly_layout(fig_assigne, height=360, show_legend=False)
    fig_assigne.update_yaxes(categoryorder="total ascending")
    render_chart_card("Top assignations", fig_assigne)


# --------------------------------------------------
# 🧾 Qualité de traitement
# --------------------------------------------------
q1, q2 = st.columns(2)

with q1:
    quality_df = pd.DataFrame(
        {
            "Indicateur": [
                "Tickets non clôturés",
                "Tickets > 7 jours",
                "Tickets > 14 jours",
                "Tickets non assignés",
                "Tickets doublons",
            ],
            "Valeur": [
                backlog_count,
                old_backlog_count,
                very_old_backlog_count,
                unassigned_backlog,
                duplicate_count,
            ],
        }
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Qualité de traitement</div>', unsafe_allow_html=True)
    st.dataframe(quality_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with q2:
    resolution_by_type = (
        resolved_df.groupby("typage")["resolution_hours"]
        .mean()
        .round(1)
        .rename_axis("typage")
        .reset_index(name="heures")
    )

    if not resolution_by_type.empty:
        fig_resolution = px.bar(
            resolution_by_type,
            x="typage",
            y="heures",
            color="typage",
            color_discrete_map=TYPE_COLOR_MAP,
        )
        fig_resolution.update_traces(marker_line_width=0, opacity=0.95)
        apply_plotly_layout(fig_resolution, height=320, show_legend=False)
        render_chart_card("Résolution moyenne par type (h)", fig_resolution)
    else:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Résolution moyenne par type (h)</div>', unsafe_allow_html=True)
        st.caption("Pas assez de tickets clôturés pour calculer ce graphique.")
        st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# 🔁 Répétitivité des sujets
# --------------------------------------------------
st.markdown("### Top récurrences (mots du titre)")

stopwords = {
    "de", "du", "la", "le", "les", "des", "et", "en", "pour", "sur",
    "dans", "a", "au", "une", "un", "avec", "plus", "pas", "est"
}

words = []
for titre_item in filtered["titre"].fillna(""):
    for word in titre_item.lower().replace("/", " ").replace("-", " ").split():
        cleaned = word.strip(" ,.;:!?()[]{}'\"")
        if len(cleaned) > 3 and cleaned not in stopwords:
            words.append(cleaned)

if words:
    top_words = (
        pd.Series(words)
        .value_counts()
        .head(12)
        .rename_axis("mot")
        .reset_index(name="occurrences")
    )

    rw1, rw2 = st.columns([1.05, 1.95])

    with rw1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Mots récurrents</div>', unsafe_allow_html=True)
        st.dataframe(top_words, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with rw2:
        fig_words = px.bar(
            top_words,
            x="mot",
            y="occurrences",
        )
        fig_words.update_traces(marker_color=COLOR_PRIMARY, marker_line_width=0, opacity=0.92)
        apply_plotly_layout(fig_words, height=320, show_legend=False)
        render_chart_card("Occurrences des mots clés", fig_words)
else:
    st.caption("Pas assez de données textuelles pour calculer les récurrences.")


# --------------------------------------------------
# 📋 Vue détaillée
# --------------------------------------------------
st.markdown("### Vue détaillée")

detail_cols = [
    "id",
    "titre",
    "typage",
    "statut",
    "priorite",
    "demandeur",
    "assigne_a",
    "created_at",
    "updated_at",
    "age_days",
]

detail_df = filtered[detail_cols].sort_values(
    by=["statut", "created_at"],
    ascending=[True, False],
)

st.dataframe(detail_df, use_container_width=True, hide_index=True)