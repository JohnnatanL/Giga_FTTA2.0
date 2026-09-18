import streamlit as st
from controller.login import autenticar_usuario
from controller.user_control import alterar_senha
from controller.hidden import hidden
from time import sleep
from stylo.tema import aplicar_tema, hero_fibra, LOGO_POSITIVO


def tela_login():
    st.set_page_config(page_title="Entrar · Portal Alto Valor", layout="wide", initial_sidebar_state="collapsed")
    hidden()
    aplicar_tema("login")
    st.markdown(
        "<style>[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl']{display:none}"
        "[data-testid='stMainBlockContainer']{padding-top:3rem}</style>",
        unsafe_allow_html=True,
    )

    cena, form = st.columns([1.35, 1], gap="large", vertical_alignment="center")

    with cena:
        hero_fibra(
            titulo="Cada condomínio, uma conexão de alto valor.",
            subtitulo="Portal da equipe FTTA Giga+ Fibra · Alloha Fibra",
            rodape="Portal Alto Valor",
            altura=520,
        )

    with form:
        st.image(LOGO_POSITIVO, width=170)
        st.markdown("### Entrar no portal")
        st.caption("Use o usuário e a senha fornecidos pelo planejamento.")
        with st.form("login_form", border=False):
            username = st.text_input("Usuário", placeholder="nome.sobrenome")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", type="primary", width="stretch")

            if submitted:

                role = autenticar_usuario(username.lower(), password)

                if role:
                    user_reset = username.lower().split('.')[0]
                    if password == f"{user_reset}@AltoValor":
                        mudar_senha(username.lower())
                    elif username.lower() == "exec_r6":
                        st.session_state['role'] = "consultor"
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = "tatiana.alianca"
                        st.rerun()
                    elif username.lower() == "gestor_r6":
                        st.session_state['role'] = "gestao"
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = "arthur.wigner"
                        st.rerun()
                    elif username.lower() == "gestor_r3":
                        st.session_state['role'] = "gestao"
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = "mariane.sobreira"
                        st.rerun()
                    else:
                        st.session_state['role'] = role
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username.lower()
                        st.rerun()
                else:
                    st.error("Usuário ou senha incorretos. Confira os dados e tente de novo.")


@st.dialog("Crie uma nova senha")
def mudar_senha(username):
    st.caption("Você entrou com a senha padrão. Defina uma senha pessoal para continuar.")
    with st.form("mudar_senha_form", border=False):
        st.text(f"""Usuário: {username}""")
        senha1 = st.text_input("Nova senha", type="password")
        senha2 = st.text_input("Confirmar nova senha", type="password")
        submitted = st.form_submit_button("Salvar nova senha", type="primary", width="stretch")
        if submitted:
            if senha1 == senha2:
                retorno = alterar_senha(username, senha1)
                if retorno == True:
                    st.success("Senha alterada. Entre novamente com a nova senha.")
                    sleep(2)
                    st.rerun()
                else:
                    st.error("Não foi possível alterar a senha. Tente de novo.")
            elif senha1 != senha2:
                st.error("As senhas não conferem.")
            else:
                st.error("Não foi possível alterar a senha. Tente de novo.")
