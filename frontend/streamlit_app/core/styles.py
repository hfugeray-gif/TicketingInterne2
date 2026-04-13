import os
import streamlit as st
import base64
from core.config import HEADER_BANNER_PATH, LOGO_MENU_PATH


def apply_global_styles():
    """
    Applique le style global de l'application.

    Règles de maintenance :
    - les styles globaux définissent les composants partagés
    - les ajustements très spécifiques à une seule page doivent rester dans la page concernée
    - éviter d'ajouter ici des rustines locales
    """
    st.markdown(
        """
        <style>
            :root {
                --primary: #004034;
                --primary-light: rgba(0, 64, 52, 0.08);
                --primary-border: rgba(0, 64, 52, 0.16);

                --text-main: #12344d;
                --text-muted: #5f6c7b;

                --border-soft: #d9e2f2;
                --bg-app-top: #f7f9fc;
                --bg-app-bottom: #eef3f9;

                --btn-bg: #111111;
                --btn-bg-hover: #000000;

                --disabled-bg: #e5e7eb;
                --disabled-text: #6b7280;
                --disabled-border: #d1d5db;
            }

            /* -----------------------------
               Eléments Streamlit natifs
            ------------------------------ */
            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }

            [data-testid="stHeader"] {
                background: rgba(247, 249, 252, 0.96) !important;
                backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--border-soft) !important;
                height: 3.2rem;
            }

            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"] {
                background: transparent !important;
            }

            /* -----------------------------
               Fond et layout global
            ------------------------------ */
            .stApp {
                background: linear-gradient(180deg, var(--bg-app-top) 0%, var(--bg-app-bottom) 100%);
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 120px;
                padding-left: 2.5rem;
                padding-right: 2.5rem;
                max-width: 100% !important;
            }

            /* -----------------------------
               Sidebar
            ------------------------------ */
            section[data-testid="stSidebar"] {
                display: none !important;
            }

            /* NE PAS cacher les boutons de header :
            ils portent la navigation du haut */
            button[kind="header"] {
                display: inline-flex !important;
            }

            /* -----------------------------
               Métriques / dataframes
            ------------------------------ */
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.85);
                border: 1px solid var(--border-soft);
                border-radius: 16px;
                padding: 12px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
            }

            div[data-testid="stDataFrame"] {
                background: rgba(255, 255, 255, 0.55);
                border-radius: 14px;
                border: 1px solid var(--border-soft);
                overflow: hidden;
            }

            /* -----------------------------
               Boutons
            ------------------------------ */
            div.stButton > button {
                border: none !important;
                border-radius: 10px !important;
                background: var(--btn-bg) !important;
                color: white !important;
                font-weight: 600 !important;
                padding: 0.55rem 1rem !important;
                box-shadow: none !important;
                transition: background 0.2s ease, box-shadow 0.2s ease !important;
                -webkit-text-fill-color: white !important;
            }

            div.stButton > button * {
                color: white !important;
                -webkit-text-fill-color: white !important;
            }

            div.stButton > button:hover {
                background: var(--btn-bg-hover) !important;
            }

            div.stButton > button:hover * {
                color: white !important;
                -webkit-text-fill-color: white !important;
            }

            div.stButton > button:focus,
            div.stButton > button:focus:not(:active) {
                border: none !important;
                box-shadow: 0 0 0 0.2rem rgba(0, 0, 0, 0.15) !important;
            }

            div.stButton > button:active {
                background: var(--btn-bg-hover) !important;
            }

            div.stButton > button:disabled {
                background: var(--disabled-bg) !important;
                color: var(--disabled-text) !important;
                border: 1px solid var(--disabled-border) !important;
                box-shadow: none !important;
                cursor: default !important;
                opacity: 1 !important;
                -webkit-text-fill-color: var(--disabled-text) !important;
            }

            div.stButton > button:disabled * {
                color: var(--disabled-text) !important;
                -webkit-text-fill-color: var(--disabled-text) !important;
            }

            /* -----------------------------
               Inputs / champs
            ------------------------------ */
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
                border: 1px solid var(--border-soft) !important;
                border-radius: 12px !important;
                color: var(--text-main) !important;
            }

            div[data-testid="stTextInputRootElement"] input:focus,
            div[data-testid="stTextAreaRootElement"] textarea:focus,
            div[data-testid="stNumberInputRootElement"] input:focus {
                border: 1px solid var(--primary) !important;
                box-shadow: 0 0 0 0.15rem rgba(0, 64, 52, 0.12) !important;
            }

            div[data-testid="stTextAreaRootElement"] textarea {
                min-height: 120px;
            }

            /* -----------------------------
               Selectbox
            ------------------------------ */
            div[data-baseweb="select"] {
                background: transparent !important;
                border: none !important;
            }

            div[data-baseweb="select"] > div {
                background: rgba(255, 255, 255, 0.72) !important;
                border: 1px solid var(--border-soft) !important;
                border-radius: 12px !important;
                box-shadow: none !important;
            }

            div[data-baseweb="select"] > div:hover {
                background: rgba(255, 255, 255, 0.86) !important;
            }

            div[data-baseweb="select"]:focus-within > div {
                border: 1px solid var(--primary) !important;
                box-shadow: 0 0 0 0.15rem rgba(0, 64, 52, 0.12) !important;
            }

            /* -----------------------------
               Labels
            ------------------------------ */
            label,
            .stSelectbox label,
            .stTextInput label,
            .stTextArea label,
            .stRadio label {
                background: transparent !important;
                color: var(--text-muted) !important;
                font-weight: 500;
            }

            /* -----------------------------
               Onglets
            ------------------------------ */
            div[data-testid="stTabs"] button {
                border-radius: 10px 10px 0 0 !important;
                color: var(--text-main) !important;
                border-bottom: 2px solid transparent !important;
                box-shadow: none !important;
                background: transparent !important;
            }

            div[data-testid="stTabs"] button::before,
            div[data-testid="stTabs"] button::after {
                content: none !important;
            }

            div[data-testid="stTabs"] button[aria-selected="true"] {
                color: var(--primary) !important;
                border-bottom: 3px solid var(--primary) !important;
                box-shadow: none !important;
            }

            div[data-testid="stTabs"] button:hover {
                color: var(--primary) !important;
            }

            div[data-testid="stTabs"] [data-baseweb="tab-border"] {
                background: transparent !important;
            }

            /* -----------------------------
               Badges / tags / accents
            ------------------------------ */
            .nav-card-tag,
            .role-badge,
            .app-header-badge,
            .mini-badge {
                color: var(--primary) !important;
                background: var(--primary-light) !important;
                border: 1px solid var(--primary-border) !important;
            }

            .nav-card-text,
            .home-welcome p,
            .kpi-label,
            .kpi-sub,
            .chart-title,
            .pilot-card p,
            .app-header-meta,
            .app-header-subtitle {
                color: var(--primary) !important;
            }

            a, a:visited {
                color: var(--primary);
            }

            /* -----------------------------
               Radio / checkbox
            ------------------------------ */
            div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div,
            div[data-testid="stCheckbox"] input:checked + div {
                border-color: var(--primary) !important;
            }

            /* -----------------------------
               Header bannière
            ------------------------------ */
            .app-header {
                margin-bottom: 28px;
            }

            .app-header-banner {
                width: 100%;
                display: block;
                border-radius: 22px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            }

            .app-header-banner img {
                width: 100%;
                height: auto;
                display: block;
                border-radius: 22px;
                max-height: 280px;
                object-fit: cover;
            }

            /* -----------------------------
               Scroll / overflow
            ------------------------------ */
            html, body, .stApp {
                height: auto !important;
                overflow: auto !important;
            }

            section.main {
                overflow: visible !important;
            }

            /* -----------------------------
               Responsive
            ------------------------------ */
            @media (max-width: 900px) {
                section[data-testid="stSidebar"] {
                    display: block !important;
                    background: rgba(247, 249, 252, 0.98) !important;
                    border-right: 1px solid var(--border-soft) !important;
                    backdrop-filter: none;
                }

                button[kind="header"] {
                    display: block !important;
                }

                .block-container {
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                    padding-top: 1.2rem !important;
                }

                .app-header {
                    margin-bottom: 20px;
                }

                .app-header-banner,
                .app-header-banner img {
                    border-radius: 18px;
                }
            }

            @media (max-width: 640px) {
                .app-header-banner,
                .app-header-banner img {
                    border-radius: 16px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_base64 = ""

    if os.path.exists(LOGO_MENU_PATH):
        logo_base64 = get_base64_image(LOGO_MENU_PATH)

    st.markdown(
        f"""
        <style>
            /* Logo dans la barre du haut */
            [data-testid="stHeader"] {{
                position: relative;
                padding-left: 52px !important;
            }}

            [data-testid="stHeader"]::before {{
                content: "";
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                width: 44px;
                height: 44px;
                background-image: url("data:image/png;base64,{logo_base64}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                z-index: 10;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_header():
    """
    Affiche une bannière unique comme header applicatif.
    """
    if not os.path.exists(HEADER_BANNER_PATH):
        return

    banner_base64 = get_base64_image(HEADER_BANNER_PATH)

    html = f"""
    <div class="app-header">
        <div class="app-header-banner">
            <img src="data:image/jpeg;base64,{banner_base64}" alt="Ticketing Beam">
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)