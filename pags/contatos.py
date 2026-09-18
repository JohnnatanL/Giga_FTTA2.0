import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from controller.hidden import hidden
from stylo.tema import aplicar_tema, CSS_CONTATOS

st.set_page_config(
    page_title="Contatos",
    page_icon="📇",
    layout="wide",
)
hidden()
aplicar_tema("contatos", animar=False)

PERFIS_PERMITIDOS = ["admin", "planejamento", "gestao"]
ARQUIVO_HTML = Path(__file__).resolve().parent.parent / "dados" / "contatos_condominios.html"

# Barreira extra: mesmo que alguém chegue na página, só perfis permitidos veem os dados
if st.session_state.get("role") not in PERFIS_PERMITIDOS:
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


@st.cache_data(show_spinner=False)
def carregar_html(caminho: str, modificado: float) -> str:
    # 'modificado' entra na chave do cache: ao trocar o arquivo, a página recarrega sozinha
    html = Path(caminho).read_text(encoding="utf-8")
    # Aplica a paleta do portal sem alterar o arquivo original
    if "</head>" in html:
        html = html.replace("</head>", CSS_CONTATOS + "</head>", 1)
    return html


if not ARQUIVO_HTML.exists():
    st.warning("Arquivo de contatos não encontrado em dados/contatos_condominios.html.")
    st.stop()

html = carregar_html(str(ARQUIVO_HTML), ARQUIVO_HTML.stat().st_mtime)

# Remove o espaçamento padrão do Streamlit para a página ocupar a tela toda
st.markdown(
    """
    <style>
        [data-testid="stMainBlockContainer"]{padding-top: 1rem; padding-bottom: 0; padding-left: 1rem; padding-right: 1rem; max-width:none}
    </style>
    """,
    unsafe_allow_html=True,
)

if hasattr(st, "iframe"):
    st.iframe(html, height=1100)
else:
    components.html(html, height=1100, scrolling=True)
