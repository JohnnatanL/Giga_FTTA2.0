"""
O CRM (gigaftta) foi incorporado ao novo portal. Este app só avisa e leva para o endereço novo.
Qualquer caminho antigo (/forms_consultor, /relat_gestor...) cai aqui.
"""
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

NOVO = "https://dash.gigamais.workers.dev/"
SEGUNDOS = 5

st.set_page_config(page_title="Portal Alto Valor mudou de endereço", page_icon="➡️", layout="centered",
                   initial_sidebar_state="collapsed")

st.markdown("""<style>
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"]{display:none !important}
[data-testid="stMainBlockContainer"]{padding-top:12vh; max-width:560px}
.st-key-aviso{background:#fff; border:1px solid #DFE4F0; border-radius:22px; padding:32px 32px 26px;
  box-shadow:0 1px 2px rgba(11,21,66,.04), 0 12px 32px -18px rgba(11,21,66,.25)}
.st-key-aviso h1{font-size:1.7rem; letter-spacing:-.025em; margin:.6rem 0 .3rem; padding:0}
.st-key-aviso p{color:#56608C}
.st-key-aviso code{font-size:.9rem}
.st-key-aviso a, .st-key-aviso a p{color:#fff !important; font-weight:600}
</style>""", unsafe_allow_html=True)

with st.container(key="aviso"):
    logo = Path(__file__).parent / "assets" / "logo_alloha.png"
    if logo.exists():
        st.image(str(logo), width=140)
    st.markdown("# O Portal Alto Valor mudou de endereço")
    st.markdown("Forms, Relatórios, Contatos e Gerenciar agora ficam no novo portal, com o mesmo usuário e senha. "
                f"Atualize o seu atalho ou favorito para `{NOVO}`.")
    st.link_button("Ir para o novo portal", NOVO, type="primary", width="stretch")
    st.caption(f"Você será levado automaticamente em {SEGUNDOS} segundos.")

# leva a janela inteira (não só este bloco) para o endereço novo: o script vai para a página
# principal, porque o bloco do Streamlit roda numa moldura sem permissão de trocar de endereço
components.html(f"""<script>
(function(){{
  var url = "{NOVO}", P = window.parent;
  try {{
    if (P.__redirecionando) return; P.__redirecionando = true;
    var s = P.document.createElement('script');
    s.text = 'setTimeout(function(){{ window.location.replace(' + JSON.stringify(url) + '); }}, {SEGUNDOS * 1000});';
    P.document.body.appendChild(s);
  }} catch (e) {{}}
}})();
</script>""", height=1)
