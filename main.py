import streamlit as st
from pags.tela_login import tela_login

# Paginas
home = st.Page("pags/home.py", title="Inicio", icon="🏠")

forms_consultor = st.Page("pags/forms_consultor.py", title="Forms", icon="📋", default=True)
gerenciar = st.Page("pags/gerenciar.py", title="Gerenciar", icon="⚙️")
rel_muralha = st.Page("pags/vendas_du.py", title="Relatório - Projeto Muralha", icon="🎯")
rel_gestor = st.Page("pags/relat_gestor.py", title="Relatórios", icon="📊")
contatos = st.Page("pags/contatos.py", title="Contatos de Condomínios", icon="📇")

def main():
    if st.session_state.get("authenticated"):

        if st.session_state.get("role") == "admin":
            pg = st.navigation({"Portal Alto Valor": [home, forms_consultor, rel_gestor, contatos, gerenciar]})
            pg.run()

        elif st.session_state.get("role") == "planejamento":
            pg = st.navigation({"Portal Alto Valor": [home, rel_gestor, contatos, gerenciar]})
            pg.run()

        elif st.session_state.get("role") == "gestao":
            pg = st.navigation({"Portal Alto Valor": [home, forms_consultor, rel_gestor, contatos, gerenciar]})
            pg.run()

        elif st.session_state.get("role") == "consultor":
            pg = st.navigation({"Portal Alto Valor": [home, forms_consultor, rel_gestor]})
            pg.run()

    else:
        
        tela_login()

if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    main()
