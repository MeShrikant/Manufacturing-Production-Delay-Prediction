import streamlit as st

NAVY, BLUE, GREY = "#0b2545", "#1f4e8c", "#eef1f5"
RISK_COLORS = {"Low": "#2e8b57", "Medium": "#e0a100", "High": "#c0392b"}


def inject_css():
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ background: {NAVY}; }}
    [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
    h1, h2, h3 {{ color: {NAVY}; }}
    div[data-testid="stMetric"] {{ background: {GREY}; border-left: 5px solid {BLUE}; padding: 12px 16px; border-radius: 6px; }}
    .risk-badge {{ display:inline-block; padding:6px 18px; border-radius:20px; color:#fff; font-weight:700; font-size:1.2rem; }}
    .banner {{ background:{NAVY}; color:#fff; padding:14px 20px; border-radius:6px; margin-bottom:12px; }}
    </style>""", unsafe_allow_html=True)


def banner(title: str, subtitle: str = ""):
    st.markdown(f'<div class="banner"><h2 style="color:#fff;margin:0">{title}</h2><div>{subtitle}</div></div>', unsafe_allow_html=True)


def risk_badge(risk: str):
    st.markdown(f'<span class="risk-badge" style="background:{RISK_COLORS[risk]}">{risk}</span>', unsafe_allow_html=True)
