from controller.controller import inserir_visita
import numpy as np
import streamlit as st
from controller.data_control import acoes_gestor, acoes_consultor, acoes_planej
from controller.controller import get_condominios, get_ficha, resume_condominio
import pandas as pd
from datetime import datetime
import datetime as dt
from auth import conecta_supabase
import json
from time import sleep
from datetime import date
from controller.hidden import hidden
from controller.carteira_export import (carteira_para_export, opcoes_filtro, para_excel,
                                        para_pdf, mes_atual_label, TITULOS, COLUNAS)
from stylo.tema import (aplicar_tema, cabecalho, estado_vazio, resumo_numeros,
                        cartao_executivo, bloco_chips, bloco_lista, bloco_dados, CORES)

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Relatório",
    page_icon="📋",
    layout="wide",
)
hidden()
aplicar_tema("relatorios")

cabecalho("Relatórios", "Ações da equipe no mês e o retrato de cada condomínio da carteira.")

pills = st.pills(label="Relatório", label_visibility="collapsed", options=["Ficha do Condomínio", "Relatório de Ações", "Exportar Carteira", "Crescimento de Base"])

COLUNAS_DETALHE = {
    "Gestor": st.column_config.TextColumn(width=160),
    "Executivo": st.column_config.TextColumn(width=180),
    "Acao de Vendas": st.column_config.NumberColumn("Ação de Vendas", width=130),
    "Ficha Cadastro": st.column_config.NumberColumn(width=130),
    "Lead": st.column_config.NumberColumn(width=90),
}
TIPOS = ['Acao de Vendas', 'Visita', 'Lead', 'Ficha Cadastro']

if pills is None:
    estado_vazio("Escolha um relatório", "Selecione acima a ficha do condomínio ou o relatório de ações do mês.")

elif pills == "Relatório de Ações":

    cola, colb = st.columns([1, 3], vertical_alignment="bottom")

    MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
         
    with cola:
        hoje = date.today()
        inicio = date(2026, 6, 1)  # primeiro mês com dados

        # de Jun/26 até o mês atual
        periodos = []
        d = inicio
        while d <= hoje:
            periodos.append(d)
            d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)

        data_ref = st.selectbox(
            "Período",
            options=periodos,
            index=len(periodos) - 1,  # mês atual
            format_func=lambda d: f"{MESES[d.month - 1]}/{str(d.year)[2:]}",
        )
        data = f"{MESES[data_ref.month - 1]}/{str(data_ref.year)[2:]}"  # usado no st.caption

        meses = {"Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4, "Mai": 5, "Jun": 6,
                 "Jul": 7, "Ago": 8, "Set": 9, "Out": 10, "Nov": 11, "Dez": 12}

        mes, ano = data.split("/")
        data_ref = date(2000 + int(ano), meses[mes], 1)

    with colb:

        botao = st.button("Gerar relatório", type="primary")

    if botao:
        if st.session_state['role'] == 'gestao':
            df = acoes_gestor(data_ref, st.session_state['username'])
            df_sumarizado = df.pivot_table(index='Executivo', 
                                     columns='Tipo', 
                                     values='Data', 
                                     aggfunc='count', 
                                     fill_value=0)

        elif st.session_state['role'] == 'consultor':

            df = acoes_consultor(data_ref, st.session_state['username'])

            df_sumarizado = df.pivot_table(index='Executivo', 
                                     columns='Tipo', 
                                     values='Data', 
                                     aggfunc='count', 
                                     fill_value=0)
                                    
        elif st.session_state['role'] in ['planejamento','admin']:
            df = acoes_planej(data_ref)
            df_sumarizado = df.pivot_table(index=['Gestor', 'Executivo'], 
                                     columns='Tipo', 
                                     values='Data', 
                                     aggfunc='count', 
                                     fill_value=0)
        if st.session_state['role'] == 'consultor':
            if 'Visita' in df_sumarizado.columns:
                visitas = df_sumarizado['Visita'].iloc[0]
            else:
                visitas = 0
            if 'Ficha Cadastro' in df_sumarizado.columns:
                ficha = df_sumarizado['Ficha Cadastro'].iloc[0]
            else:
                ficha = 0
            if 'Lead' in df_sumarizado.columns:
                lead = df_sumarizado['Lead'].iloc[0]
            else:
                lead = 0
            if 'Acao de Vendas' in df_sumarizado.columns:
                acoes = df_sumarizado['Acao de Vendas'].iloc[0]
            else:
                acoes = 0

            st.caption(f"Executivo de vendas: {st.session_state['username']} · {data}")
            resumo_numeros([
                ("Total de ações", acoes + visitas + lead + ficha, "destaque"),
                ("Visitas", visitas, CORES["verde"]),
                ("Ações de vendas", acoes, CORES["ciano"]),
                ("Leads", lead, "#7C6CFF"),
                ("Fichas de cadastro", ficha, "#F2A541"),
            ])

            st.subheader("Detalhamento")
            st.dataframe(df, width="stretch", hide_index=False, column_config=COLUNAS_DETALHE)

        elif st.session_state['role'] == 'gestao':
            df_sumarizado = df_sumarizado.reset_index()
            for c in TIPOS:
                if c not in df_sumarizado.columns:
                    df_sumarizado[c] = 0

            totais = df_sumarizado[TIPOS].sum()
            resumo_numeros([
                ("Total de ações da equipe", int(totais.sum()), "destaque"),
                ("Visitas", int(totais['Visita']), CORES["verde"]),
                ("Ações de vendas", int(totais['Acao de Vendas']), CORES["ciano"]),
                ("Leads", int(totais['Lead']), "#7C6CFF"),
                ("Fichas de cadastro", int(totais['Ficha Cadastro']), "#F2A541"),
            ])

            st.subheader("Por executivo")
            maximo = int(df_sumarizado[TIPOS].max().max() or 0)
            ordem = df_sumarizado.assign(_t=df_sumarizado[TIPOS].sum(axis=1)).sort_values("_t", ascending=False)
            cols = st.columns(3)
            for i, (_, row) in enumerate(ordem.iterrows()):
                with cols[i % 3]:
                    cartao_executivo(row['Executivo'], row.to_dict(), maximo)

            st.subheader("Detalhamento")
            st.dataframe(df, width="stretch", hide_index=False, column_config=COLUNAS_DETALHE)

        elif st.session_state['role'] in ['planejamento', 'admin']:
            df_sumarizado = df_sumarizado.reset_index()
            for c in TIPOS:
                if c not in df_sumarizado.columns:
                    df_sumarizado[c] = 0
            totais = df_sumarizado[TIPOS].sum()
            resumo_numeros([
                ("Total de ações", int(totais.sum()), "destaque"),
                ("Visitas", int(totais['Visita']), CORES["verde"]),
                ("Ações de vendas", int(totais['Acao de Vendas']), CORES["ciano"]),
                ("Leads", int(totais['Lead']), "#7C6CFF"),
                ("Fichas de cadastro", int(totais['Ficha Cadastro']), "#F2A541"),
            ])
            st.subheader("Por gestor e executivo")
            st.dataframe(df_sumarizado, width="stretch", hide_index=True, column_config=COLUNAS_DETALHE)
            st.subheader("Detalhamento")
            st.dataframe(df, width="stretch", hide_index=False, column_config=COLUNAS_DETALHE)

elif pills == "Exportar Carteira":

    role = st.session_state['role']
    username = st.session_state['username']
    mes = mes_atual_label()

    if role == 'consultor':
        st.caption(f"Sua carteira de {mes}.")
        executivo = gestor = None
    else:
        execs, gestores = opcoes_filtro(role, username)
        a, b = st.columns(2)
        with a:
            executivo = st.selectbox("Executivo", execs, index=None,
                                     placeholder="Todos da sua visão", key="exp_exec")
        with b:
            gestor = st.selectbox("Gestor direto", gestores, index=None,
                                  placeholder="Todos", key="exp_gestor",
                                  disabled=role == 'gestao') if gestores else None
        st.caption(f"Carteira de {mes}. Sem filtro, o arquivo sai com todos os executivos da sua visão.")

    df = carteira_para_export(role, username,
                              executivo=None if role != 'consultor' and not executivo else executivo,
                              gestor=None if role != 'consultor' and not gestor else gestor)

    if df.empty:
        estado_vazio("Nenhum prédio na carteira deste mês",
                     "Fale com o planejamento se a carteira ainda não foi montada.")
    else:
        resumo_numeros([
            ("Prédios", len(df), "destaque"),
            ("Executivos", df.executivo.nunique(), CORES["ciano"]),
            ("Período", mes, CORES["verde"]),
        ])

        nome = f"carteira_{mes.replace('/', '-')}"
        if executivo if role != 'consultor' else False:
            nome += "_" + str(executivo).lower().replace(" ", "-")
        titulo = f"Carteira {mes}" + (f" · {executivo}" if role != 'consultor' and executivo else "")

        d1, d2, _ = st.columns([1, 1, 2])
        with d1:
            st.download_button("Exportar Excel", para_excel(df, titulo), file_name=f"{nome}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               type="primary", width="stretch")
        with d2:
            st.download_button("Exportar PDF", para_pdf(df, titulo), file_name=f"{nome}.pdf",
                               mime="application/pdf", width="stretch")

        st.dataframe(df.rename(columns=TITULOS), width="stretch", hide_index=True,
                     column_config={"Endereço completo": st.column_config.TextColumn(width="large")})

elif pills == "Crescimento de Base":
    
    estado_vazio("Crescimento de Base em construção", "Em breve você acompanha aqui a evolução da base por condomínio.")

elif pills == "Ficha do Condomínio":
    
    a, b = st.columns([3, 1], vertical_alignment="bottom")
    with a: condominio = st.selectbox("Condomínio", options=get_condominios(st.session_state['username'], st.session_state['role']), placeholder="Selecione condomínio", key="condominio")
    with b: 
        vai = st.button("Gerar ficha", type="primary")

    
    if condominio and vai:
        try:
            df_ficha = resume_condominio(get_ficha(condominio))

            st.subheader(condominio)
            d, e, f, g = st.columns(4)

            with d:
                bloco_dados("Estrutura", [
                    ("Torres", df_ficha['qtde_torres'].iloc[0]),
                    ("Andares", df_ficha['qtde_andares'].iloc[0]),
                    ("Apto por andar", df_ficha['qtde_apto_andar'].iloc[0]),
                ])

            with e:
                texto = df_ficha['contatos'].iloc[0]
                linhas = [c.strip() for c in str(texto).split(';') if c.strip()]
                bloco_lista("Contatos", linhas, CORES["ciano"], "Sem contatos registrados.")

            with f:
                texto = df_ficha['parceiros'].iloc[0]
                linhas = [c.strip() for c in str(texto).split(';') if c.strip()]
                bloco_lista("Parceiros", linhas, "#7C6CFF", "Sem parceiros registrados.")

            with g:
                texto = df_ficha['concorrencia'].iloc[0]
                linhas = [c.strip() for c in str(texto).split(',') if c.strip()]
                bloco_chips("Concorrência", linhas, "ambar", "Sem concorrência registrada.")

        except Exception:
            st.info("Sem dados de ficha para este condomínio.")
