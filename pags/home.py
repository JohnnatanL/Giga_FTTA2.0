import streamlit as st
from controller.hidden import hidden
from stylo.tema import aplicar_tema, hero_fibra

st.set_page_config(
    page_title="Início · Portal Alto Valor",
    page_icon="🏠",
    layout="wide",
)
hidden()
aplicar_tema("home")

usuario = st.session_state.get("username", "")
primeiro_nome = usuario.split(".")[0].capitalize() if usuario else ""
role = st.session_state.get("role")

hero_fibra(
    titulo=f"Olá, {primeiro_nome}." if primeiro_nome else "Portal Alto Valor",
    subtitulo="Registre visitas, leads e plantões nos condomínios FTTA e acompanhe o desempenho da equipe.",
    rodape="Portal Alto Valor · FTTA",
    altura=300,
)

# Atalhos: mesmos destinos que o menu lateral libera para cada perfil (ver main.py)
ATALHOS = {
    "forms": ("pags/forms_consultor.py", "Registrar atividade", "Visita, ficha, lead e plantão", "📋"),
    "relat": ("pags/relat_gestor.py", "Ver relatórios", "Ações do mês e ficha do condomínio", "📊"),
    "contatos": ("pags/contatos.py", "Contatos de condomínios", "Síndicos, administradoras e filtros", "📇"),
    "gerenciar": ("pags/gerenciar.py", "Gerenciar", "Carteiras do mês e acessos da equipe", "⚙️"),
}
POR_PERFIL = {
    "admin": ["forms", "relat", "contatos", "gerenciar"],
    "planejamento": ["relat", "contatos", "gerenciar"],
    "gestao": ["forms", "relat", "contatos", "gerenciar"],
    "consultor": ["forms", "relat"],
}

st.write("")
st.subheader("Por onde começar")
chaves = POR_PERFIL.get(role, [])
cols = st.columns(len(chaves) or 1)
for col, chave in zip(cols, chaves):
    caminho, titulo, desc, icone = ATALHOS[chave]
    with col:
        with st.container(border=True):
            st.markdown(f"**{titulo}**  \n:gray[{desc}]")
            st.page_link(caminho, label="Abrir", icon=icone)
