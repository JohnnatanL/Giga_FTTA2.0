import streamlit as st
from controller.hidden import hidden
from stylo.tema import aplicar_tema, cabecalho
from views.carteira import render_carteira, PERFIS_CARTEIRA
from views.usuarios import render_usuarios, PERFIS_USUARIOS

st.set_page_config(
    page_title="Gerenciar",
    page_icon="⚙️",
    layout="wide",
)
hidden()
aplicar_tema("gerenciar")

role = st.session_state.get("role")
if role not in PERFIS_CARTEIRA:
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()

cabecalho("Gerenciar", "Carteiras dos vendedores no mês atual e acessos da equipe.")

# Gestão só vê a carteira; admin e planejamento também gerenciam usuários
abas = ["Carteira"] + (["Usuários"] if role in PERFIS_USUARIOS else [])
aba = st.pills("Área", abas, default="Carteira", label_visibility="collapsed", key="gerenciar_aba")

if aba == "Usuários":
    render_usuarios()
else:
    render_carteira()
