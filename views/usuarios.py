import streamlit as st
from time import sleep
from stylo.tema import estado_vazio
from controller.user_control import (
    criar_usuario,
    editar_usuario,
    deletar_usuario,
    listar_usuarios,
    validar_submissao,
    resetar_senha,
    get_perfil
)

PERFIS_USUARIOS = ["admin", "planejamento"]


def render_usuarios():
    """Aba Usuários do Gerenciar (antigo Gerenciamento de Usuários). Só admin e planejamento."""
    if st.session_state.get("role") not in PERFIS_USUARIOS:
        st.error("Você não tem permissão para gerenciar usuários.")
        return

    pills = st.pills(label="Ação", label_visibility="collapsed", key="usuarios_acao", options=["Criar Usuário", "Editar Usuário", "Excluir Usuário", "Resetar Senha"])

    if pills is None:
        estado_vazio("Escolha uma ação", "Selecione acima o que você quer fazer com os usuários.")

    elif pills == "Criar Usuário":

        with st.form("criar_usuario"):
            nome = st.text_input("Nome")
            username = st.text_input("Username")
            perfil = st.selectbox("Perfil", get_perfil())
            submitted = st.form_submit_button("Criar", type="primary")

            if submitted:
                retorno_validacao = validar_submissao(nome, username, perfil)
                if retorno_validacao == "Continue":
                    retorno = criar_usuario(nome, username, perfil)
                    if retorno == True:
                        st.success("Usuário criado com sucesso")
                        sleep(2)
                        st.rerun()
                    else:
                        st.error("Erro ao criar usuário")
                else:
                    st.error(retorno_validacao)
            elif not submitted and not nome and not username and not perfil:
                st.error("Preencha todos os campos")
                st.rerun()

    elif pills == "Editar Usuário":

        user_map, usuarios_dict, display_options = listar_usuarios()

        user_selection = st.selectbox("Usuário", display_options, index=None, placeholder="Selecione um usuário")

        if user_selection:

            user_id = user_map[user_selection]
            usuario = usuarios_dict[user_id]

            with st.form("editar_usuario"):

                nome = st.text_input("Nome", value=usuario["nome"])
                username = st.text_input("Username", value=usuario["username"])
                perfis = get_perfil()
                perfil_index = perfis.index(usuario["perfil"])

                perfil = st.selectbox(
                    "Perfil",
                    perfis,
                    index=perfil_index
                )

                submitted = st.form_submit_button("Editar", type="primary")

                if submitted:
                    retorno_validacao = validar_submissao(nome, username, perfil)
                    if retorno_validacao == "Continue":
                        retorno = editar_usuario(user_id, nome, username, perfil)
                        if retorno == True:
                            st.success("Usuário editado com sucesso")
                            sleep(2)
                            st.rerun()
                        else:
                            st.error("Erro ao editar usuário")
                    else:
                        st.error(retorno_validacao)
                elif not submitted and not nome and not username and not perfil:
                    st.error("Preencha todos os campos")
                    st.rerun()

    elif pills == "Excluir Usuário":

        user_map, usuarios_dict, display_options = listar_usuarios()

        user_selection = st.selectbox("Usuário", display_options, index=None, placeholder="Selecione um usuário")

        if user_selection:

            user_id = user_map[user_selection]
            usuario = usuarios_dict[user_id]

            with st.form("excluir_usuario"):
                id = usuario['id']
                idd = st.text(f"ID: {id}")
                nome = st.text(f"Nome: {usuario['nome']}")
                username = st.text(f"Username: {usuario['username']}")
                perfil = st.text(f"Perfil: {usuario['perfil']}")
                submitted = st.form_submit_button("Excluir", type="primary")

                if submitted and id:
                    retorno = deletar_usuario(id)
                    if retorno == True:
                        st.success("Usuário excluído com sucesso")
                        sleep(2)
                        st.rerun()
                    else:
                        st.error("Erro ao excluir usuário")

    elif pills == "Resetar Senha":
        user_map, usuarios_dict, display_options = listar_usuarios()
        user_selection = st.selectbox("Usuário", display_options, index=None, placeholder="Selecione um usuário")
        if user_selection:
            user_id = user_map[user_selection]
            usuario = usuarios_dict[user_id]
            with st.form("resetar_senha"):
                id = usuario['id']
                idd = st.text(f"ID: {id}")
                nome = st.text(f"Nome: {usuario['nome']}")
                username = st.text(f"Username: {usuario['username']}")
                perfil = st.text(f"Perfil: {usuario['perfil']}")
                submitted = st.form_submit_button("Resetar Senha", type="primary")
                if submitted and id:
                    retorno = resetar_senha(id, usuario['username'])
                    if retorno == True:
                        st.success(f"Senha resetada com sucesso para {usuario['username']}@Mudar123")
                        sleep(2)
                        st.rerun()
                    else:
                        st.error("Erro ao resetar senha")
