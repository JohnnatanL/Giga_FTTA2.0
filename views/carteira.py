import streamlit as st
from datetime import date

from controller.controller import get_condominios
from controller.carteira_control import (
    listar_vendedores,
    get_carteira_mes,
    ids_por_rotulo,
    donos_no_mes,
    incluir_predios,
    excluir_predios,
    copiar_mes_anterior,
)
from stylo.tema import estado_vazio, resumo_numeros, CORES

PERFIS_CARTEIRA = ["admin", "planejamento", "gestao"]
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


@st.dialog("Excluir prédios da carteira")
def _confirmar_exclusao(vendedor, ids, nomes):
    st.write(f"Remover **{len(ids)}** prédio(s) da carteira de **{vendedor}** neste mês?")
    for n in nomes[:8]:
        st.caption(f"• {n}")
    if len(nomes) > 8:
        st.caption(f"… e mais {len(nomes) - 8}")
    c1, c2 = st.columns(2)
    if c1.button("Excluir", type="primary", use_container_width=True):
        n = excluir_predios(vendedor, ids)
        st.session_state["carteira_msg"] = f"{n} prédio(s) excluído(s) da carteira."
        st.rerun()
    if c2.button("Cancelar", use_container_width=True):
        st.rerun()


def render_carteira():
    role = st.session_state.get("role")
    username = st.session_state.get("username", "")
    if role not in PERFIS_CARTEIRA:
        st.error("Você não tem permissão para gerenciar carteiras.")
        return

    hoje = date.today()
    mes_label = f"{MESES[hoje.month - 1]}/{str(hoje.year)[2:]}"

    if msg := st.session_state.pop("carteira_msg", None):
        st.success(msg)
    if aviso := st.session_state.pop("carteira_aviso", None):
        st.warning(aviso)

    vendedores = listar_vendedores(role, username)
    if vendedores.empty:
        estado_vazio(
            "Nenhum vendedor encontrado",
            "Não há consultores na sua equipe neste mês. Confira a hierarquia com o planejamento.",
        )
        return

    opcoes = {f"{r.nome} ({r.username})": r.username for r in vendedores.itertuples()}
    escolha = st.selectbox("Vendedor", list(opcoes), index=None, placeholder="Selecione um vendedor")
    if not escolha:
        estado_vazio("Escolha um vendedor", f"A carteira exibida e editada é sempre a do mês atual ({mes_label}).")
        return
    vendedor = opcoes[escolha]

    carteira = get_carteira_mes(vendedor)
    resumo_numeros([
        ("Prédios na carteira", len(carteira), "destaque"),
        ("Período", mes_label, CORES["verde"]),
    ])

    # ── Carteira atual ──────────────────────────────────────────────────────
    st.subheader("Carteira do mês")
    if carteira.empty:
        anterior = get_carteira_mes(vendedor, anterior=True)
        estado_vazio("Carteira vazia neste mês", "Inclua prédios abaixo ou copie a carteira do mês anterior.")
        if not anterior.empty and st.button(f"Copiar carteira do mês anterior ({len(anterior)} prédios)", type="primary"):
            n = copiar_mes_anterior(vendedor)
            st.session_state["carteira_msg"] = f"{n} prédio(s) copiado(s) do mês anterior."
            st.rerun()
    else:
        sel = st.dataframe(
            carteira[["condominio", "cidade", "uf", "bairro"]],
            hide_index=True,
            width="stretch",
            on_select="rerun",
            selection_mode="multi-row",
            key=f"tabela_carteira_{vendedor}",
            column_config={
                "condominio": st.column_config.TextColumn("Condomínio", width="large"),
                "cidade": "Cidade", "uf": "UF", "bairro": "Bairro",
            },
        )
        linhas = sel.selection.rows if sel else []
        st.caption("Marque as linhas na tabela para excluir prédios da carteira.")
        if st.button(f"Excluir {len(linhas)} selecionado(s)", disabled=not linhas):
            escolhidos = carteira.iloc[linhas]
            _confirmar_exclusao(vendedor, escolhidos["id_condominio"].tolist(), escolhidos["condominio"].tolist())

    # ── Inclusão ────────────────────────────────────────────────────────────
    st.subheader("Incluir prédios")
    ja_na_carteira = set(carteira["condominio"]) if not carteira.empty else set()
    disponiveis = [c for c in get_condominios(username, role) if c not in ja_na_carteira]

    with st.form(f"incluir_{vendedor}", border=True):
        novos = st.multiselect(
            "Prédios liberados para venda",
            disponiveis,
            placeholder="Busque pelo nome, cidade ou bairro",
        )
        enviar = st.form_submit_button("Incluir na carteira", type="primary")

    if enviar:
        if not novos:
            st.error("Selecione pelo menos um prédio para incluir.")
            return
        mapa = ids_por_rotulo(novos)
        ids = list(mapa.values())
        donos = donos_no_mes(ids, vendedor)
        if not donos.empty:
            ocupados = set(donos["id_condominio"].astype(str))
            nome_por_id = {str(v): k for k, v in mapa.items()}
            st.session_state["carteira_aviso"] = (
                "Estes prédios já estão na carteira de outro vendedor neste mês e não foram incluídos:\n\n"
                + "\n".join(f"- {nome_por_id.get(str(r.id_condominio), r.id_condominio)} → {r.vendedor}"
                            for r in donos.itertuples())
            )
            ids = [i for i in ids if str(i) not in ocupados]
        if ids:
            n = incluir_predios(vendedor, ids)
            st.session_state["carteira_msg"] = f"{n} prédio(s) incluído(s) na carteira de {vendedor}."
        st.rerun()
