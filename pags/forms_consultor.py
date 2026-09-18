from controller.controller import inserir_visita
import numpy as np
import streamlit as st
from controller.controller import (get_condominios,
                                    round_to_quarter,
                                    get_id_condominio,
                                    get_visitas,
                                    get_visita_by_id,
                                    get_consultores,
                                    update_visita,
                                    inserir_leads, validar_lead_repetido, inserir_ficha, inserir_checkin, ler_checkout, inserir_checkout)
import pandas as pd
from datetime import datetime
import datetime as dt
from auth import conecta_supabase
import json
from time import sleep
from controller.hidden import hidden
from stylo.tema import aplicar_tema, cabecalho, estado_vazio

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Forms",
    page_icon="📋",
    layout="wide",
)
hidden()
aplicar_tema("forms")

@st.dialog("Detalhes da Visita", width="medium")
def mostrar_detalhes(id_visita):
    visita = get_visita_by_id(id_visita)

    f = visita.loc[
        visita["id"] == id_visita
    ].iloc[0]
    st.markdown(f"**Condominio:** {f['condominio']}")
    coll1, coll2 = st.columns(2)
    with coll1: st.markdown(f"**Data de Início:** {f['dt_inicio'].strftime('%d/%m/%Y %H:%M')}")
    with coll2: st.markdown(f"**Data de Término:** {f['dt_fim'].strftime('%d/%m/%Y %H:%M')}")


    df_contatos = pd.DataFrame([
        {
            "Nome": "",
            "Cargo": "",
            "Telefone": "",
            "Email": "",
        }]
    )

    contatos = st.data_editor(
        df_contatos,
        column_config={
            "Nome": st.column_config.TextColumn("Nome"),
            "Cargo": st.column_config.SelectboxColumn(
                "Cargo",
                options=[
                    'Síndico', 
                    'Administrador', 
                    'Porteiro', 
                    'Zelador', 
                    'Segurança',
                    'Outro'
                ],
                required=True,
            ),
            "Telefone": st.column_config.TextColumn("Telefone"),
            "E-mail": st.column_config.TextColumn("E-mail"),
        },
        hide_index=True,
        num_rows="dynamic",
        key="contatos",
            )

    # Contatos
    lista_contatos = [
        {
            "cid": i[0],
            "Nome": i[1],
            "Cargo": i[2],
            "Telefone": i[3],
            "Email": i[4],
        }
        for i in contatos.itertuples()
        if any([
            str(i[1]).strip(),
            str(i[2]).strip(),
            str(i[3]).strip(),
            str(i[4]).strip()
        ])
    ]

    response = visita['response'].iloc[0]

    if isinstance(response, str):
        response = json.loads(response)

    if lista_contatos:
        response["contatos"] = lista_contatos

    if st.button("Salvar contatos", type="primary"):
        update_visita(id_visita, json.dumps(response, ensure_ascii=False))
        st.success("Contatos salvos com sucesso!")
        sleep(0.7)
        st.rerun()


cabecalho("Registrar atividade", "Escolha o tipo de registro. Cada envio entra na sua carteira e nos relatórios da equipe.")

pills = st.pills(label="Tipo de registro", label_visibility="collapsed", options=["Nova Visita", "Ficha Cadastral", "Cadastro de Leads", "Checkin Plantão", "Checkout Plantão", "Permutas"])

if pills is None:
    estado_vazio("Nenhum formulário aberto", "Selecione acima o que você quer registrar agora.")

if pills == "Cadastro de Leads":
    with st.form("cadastro_leads"):
        condominio = st.selectbox("Condomínio", options=get_condominios(st.session_state['username'], st.session_state['role']), placeholder="Selecione condomínio", key="condominio")
        nome = st.text_input("Nome", key="nome")
        telefone = st.text_input("Telefone", key="telefone")
        apt_bloco = st.text_input("Apartamento/Bloco", key="apt_bloco")
        
        if st.form_submit_button("Salvar", type="primary"):
            if st.session_state['condominio'] and st.session_state['nome'] and st.session_state['telefone'] and st.session_state['apt_bloco']:
                if validar_lead_repetido(st.session_state['condominio'], st.session_state['telefone'], "tbleads") == True:
                    st.error("Lead já cadastrado!", icon="⚠️")
                    sleep(1)
                    st.rerun()
                else:
                    inserir_leads(st.session_state['condominio'], st.session_state['nome'], st.session_state['telefone'], st.session_state['apt_bloco'], st.session_state['username'])
                    st.success("Lead salvo com sucesso!")
                    sleep(0.7)
                    st.rerun()
            else:
                st.error("Preencha todos os campos!")

elif pills == "Histórico de Visitas":
    with st.form("hist_visita"):

        cola, colb = st.columns([1, 5])

        with cola:
            data = st.date_input(
                "Selecione o período",
                value=[
                    pd.to_datetime("today").replace(day=1),
                    pd.to_datetime("today"),
                ],
                format="DD.MM.YYYY",
                width=200,
            )

            try:
                data_inicial = data[0]
                data_final = data[1]

            except:
                st.info("Selecione um período válido!", icon="⚠️")

        with colb:

            if st.session_state['role'] == "gestao" and data_inicial and data_final:

                consultores = get_consultores(
                    st.session_state['username'],
                    data_inicial,
                    data_final
                )

                if consultores:
                    consultor = st.multiselect(
                        "Consultor",
                        options=consultores,
                        key="consultor",
                        default=consultores
                    )
                else:
                    st.warning("Nenhum consultor encontrado")

            elif st.session_state['role'] == 'consultor':

                consultor = st.selectbox(
                    "Consultor",
                    options=[st.session_state['username']],
                    key="consultor"
                )

        submitted = st.form_submit_button("Enviar", type="primary")
        if submitted:
            df_visitas = pd.DataFrame()
            if st.session_state['role'] == 'consultor':
                username = st.session_state['username']
                df_visitas = pd.concat([df_visitas, get_visitas(username)])
            elif st.session_state['role'] == 'gestao':
                for c in consultor:
                    username = c.split('(')[1].replace(')', '')
                    df_visitas = pd.concat([df_visitas, get_visitas(username)])



            st.subheader("Visitas")
            st.dataframe(df_visitas, width="stretch", hide_index=True)


elif pills == "Nova Visita":
    with st.form("nova_visita"):
        tipo_forms = "Teste"
        subtipo_forms = "Teste_Fortaleza"

        a0, a1, a2, a3, a4 = st.columns([1.5, 1.2, 1.5, 1.2, 5])

        with a0: dt_inicio = st.date_input("Data de Início",key="dt_inicio", format="DD/MM/YYYY")
        with a1: hr_inicio = st.time_input("Hora de Início", key="hr_inicio", value=round_to_quarter().time())
        with a2: dt_fim = st.date_input("Data de Término",key="dt_fim", format="DD/MM/YYYY")
        with a3: hr_fim = st.time_input("Hora de Término", key="hr_fim", value=round_to_quarter().time())
        
        condominio = st.selectbox("Condomínio", options=get_condominios(st.session_state['username'], st.session_state['role']), placeholder="Selecione condomínio", key="condominio")

        torres = 0
        andares = 0
        apto_andar = 0
        #b0, b1, b2, b3 = st.columns([1, 1, 1, 5])
        #with b0: torres = st.number_input("Qtde Torres", key="qtde_torres", min_value=1, step=1)
        #with b1: andares = st.number_input("Qtde Andares", key="qtde_andares", min_value=1, step=1)
        #with b2: apto_andar = st.number_input("Apto por Andar", key="apto_por_andar", min_value=1, step=1)

        c0, c1, c2 = st.columns([2, 4, 2.5])
        with c0: permuta = st.selectbox("Possui permuta?", ["Não possui", "Possui 1 permuta", "Possui 2 permutas", "Possui 3 ou mais permutas"] ,key="permuta")
        with c1: concorrencia = st.multiselect("Possui concorrência?", ["Exclusivo Giga+ Fibra", "Claro", "Vivo", "TIM", "Oi", "Brisanet", "Multiplay (Alares)", "Algar Telecom", "ProveNET", "Velocinet Provedor", "Byteplay Connect", "QNet Telecom", "Telefibra", "HD Provedor", "Lay Provedor", "Fortalnet", "RedeNet Telecom", "WireXtreme", "Infortec", "JWS Provedor", "Argohost Net", "Orion Telecom", "Bayde Net", "Ciberdyne Internet", "Wire Link", "Ponto Net", "Linknet Provedor", "Outros"], key="concorrencia")
        #with c2: outros_conc = st.text_input("Outros", key="outros_conc")
        
        with st.expander("Contatos"):
            df_contatos = pd.DataFrame([
                {
                    "Nome": "",
                    "Cargo": "",
                    "Telefone": "",
                    "Email": "",
                    "Aniversário": ""
                }]
            )

            contatos = st.data_editor(
                df_contatos,
                column_config={
                    "Nome": st.column_config.TextColumn("Nome"),
                    "Cargo": st.column_config.SelectboxColumn(
                        "Cargo",
                        options=[
                            'Síndico', 
                            'Administrador', 
                            'Porteiro', 
                            'Zelador', 
                            'Segurança',
                            'Outro'
                        ],
                        required=True,
                    ),
                    "Telefone": st.column_config.TextColumn("Telefone"),
                    "E-mail": st.column_config.TextColumn("Email"),
                    "Aniversário": st.column_config.TextColumn("Aniversário", max_chars=10),
                },
                hide_index=True,
                num_rows="dynamic",
                key="contatos",
            )

        with st.expander("Parceiros"):
            df_parceiros = pd.DataFrame([{
                    "Nome da Empresa": "",
                    "Tipo de Negócio": "",
                    "Pessoa de Contato": "",
                    "Telefone do Parceiro": "",
                }]
            )
            parceiros = st.data_editor(
                df_parceiros,
                column_config={
                    "Nome da Empresa": st.column_config.TextColumn("Nome da Empresa"),
                    "Tipo de Negócio": st.column_config.SelectboxColumn(
                        "Tipo de Negócio",
                        options=[
                            'Máquinas de vendas',
                            'Academia',
                            'Mercearia interna',
                            'Lavanderia',
                            'Geladeiras inteligentes',
                            'Dog Walker',
                            'Food Trucks',
                            'Automação residencial',
                            'Estação de carregamento para carros elétricos',
                            'Outro'
                        ],
                        required=True,
                    ),
                    "Pessoa de Contato": st.column_config.TextColumn("Pessoa de Contato"),
                    "Telefone do Parceiro": st.column_config.TextColumn("Telefone do Parceiro"),
                },
                hide_index=True,
                num_rows="dynamic",
                key="parceiros",
            )

        observacoes = st.text_area("Observações", key="observacoes")

        status_entrada = st.selectbox("Status Entrada", ["Autorizado", "Sem Autorização", "Pendente Autorização"])
        
        submitted = st.form_submit_button("Enviar", type="primary")
        if submitted:

            dataInicial = datetime.combine(dt_inicio, hr_inicio)
            dataFinal = datetime.combine(dt_fim, hr_fim)
            # Contatos
            lista_contatos = [
                    {
                        "cid": i[0],
                        "Nome": i[1],
                        "Cargo": i[2],
                        "Telefone": i[3],
                        "Email": i[4],
                        "Aniversario": i[5],
                    }
                    for i in contatos.itertuples()
                    if any([
                        str(i[1]).strip(),
                        str(i[2]).strip(),
                        str(i[3]).strip(),
                        str(i[4]).strip()
                    ])
                ]
            # Parceiros
            lista_parceiros = [
                    {
                        "pid": i[0],
                        "Nome da Empresa": i[1],
                        "Tipo de Negócio": i[2],
                        "Pessoa de Contato": i[3],
                        "Telefone do Parceiro": i[4],
                    }
                    for i in parceiros.itertuples()
                    if any([
                        str(i[1]).strip(),
                        str(i[2]).strip(),
                        str(i[3]).strip(),
                        str(i[4]).strip()
                    ])
                ]


            if dataInicial >= dataFinal:
                st.error("Data inicial deve ser anterior à data final")
            elif not all([dt_inicio, hr_inicio, dt_fim, hr_fim, condominio, permuta, concorrencia]):
                st.error("Preencha os campos obrigatórios")
            elif not lista_contatos:
                st.error("Preencha pelo menos um contato")
            elif not status_entrada:
                st.error("Informe sobre status da entrada no local.")
            else:
                id_condominio = get_id_condominio(condominio)
                response = {
                    "qtde_torres": torres,
                    "qtde_andares": andares,
                    "qtde_apto_andar": apto_andar,
                    "permuta": permuta,
                    "concorrencia": concorrencia,
                    #"outros_conc": outros_conc,
                }

                if lista_contatos:
                    response["contatos"] = lista_contatos

                if lista_parceiros:
                    response["parceiros"] = lista_parceiros

                inserir_visita(id_condominio, dataInicial, dataFinal, st.session_state['username'], tipo_forms, subtipo_forms, json.dumps(response, ensure_ascii=False), observacoes, status_entrada)

                st.success("Formulário enviado com sucesso!")
                sleep(0.7)
                st.rerun()
                
elif pills == "Ficha Cadastral":
    with st.form("Ficha Cadastral"):
        condominio = st.selectbox("Condomínio", options=get_condominios(st.session_state['username'], st.session_state['role']), placeholder="Selecione condomínio", key="condominio_ficha")
        a0, b0, c0 = st.columns([7, 3, 3])
        with a0: nome = st.text_input("Nome", key="nome_ficha")
        with b0: cargo = st.selectbox("Cargo", options=["Síndico", "Administrador", "Porteiro", "Zelador", "Segurança", "Outro"], key="cargo_ficha")
        with c0: aniversario = st.date_input("Aniversário", key="aniversario_ficha", format="DD/MM/YYYY", min_value="1925-01-01", max_value="2007-12-31", value="2000-01-01")
        telefone = st.text_input("Telefone", key="telefone_ficha")

        a, b, c, d, e = st.columns(5)
        with a: torres = st.number_input("Torres", key="torres_ficha", value=1, min_value=1, max_value=999, step=1)
        with b: andares = st.number_input("Andares", key="andares_ficha", value=1, min_value=1, max_value=999, step=1)
        with c: apt_andar = st.number_input("Apt por Andar", key="apt_andar", value=1, min_value=1, max_value=999, step=1)

        if st.form_submit_button("Salvar", type="primary"):
            if condominio and nome and cargo and telefone:
                if validar_lead_repetido(condominio, telefone, "tbficha") == True:
                    st.error("Contato já cadastrado!", icon="⚠️")
                    sleep(1)
                    st.rerun()
                else:
                    inserir_ficha(condominio, nome, cargo, telefone, aniversario, torres, andares, apt_andar, st.session_state['username'])
                    st.success("Contato salvo com sucesso!")
                    sleep(0.7)
                    st.rerun()
            else:
                st.error("Preencha todos os campos!")

elif pills == "Checkin Plantão":
    with st.form("Checkin Plantão"):
        condominio = st.selectbox("Condomínio", options=get_condominios(st.session_state['username'], st.session_state['role']), placeholder="Selecione condomínio", key="condominio_checkin")
        
        a, b, c = st.columns([2, 1, 6])
        with a: dt_inicio = st.date_input("Data Inicio", key="data_checkin")
        with b: hr_inicio = st.time_input("Hor Inicio", key="hora_checkin")

        a, b, c = st.columns([2, 1, 6])
        with a: dt_fim = st.date_input("Data Fim", key="data_checkout")
        with b: hr_fim = st.time_input("Hora Fim", key="hora_checkout")

        if st.form_submit_button("Salvar", type="primary"):
            if condominio and dt_inicio and hr_inicio and dt_fim and hr_fim:
                dataInicial = datetime.combine(dt_inicio, hr_inicio)
                dataFinal = datetime.combine(dt_fim, hr_fim)
                if dataInicial >= dataFinal:
                    st.error("Data inicial deve ser anterior à data final")
                else:
                    inserir_checkin(condominio, dataInicial, dataFinal, st.session_state['username'])
                    st.success("Checkin salvo com sucesso!")
                    sleep(0.7)
                    st.rerun()
            else:
                st.error("Preencha todos os campos!")

elif pills == "Checkout Plantão":
    with st.form("Checkout Plantão"):
        df_checkin = ler_checkout(st.session_state['username'])

        checkin = st.selectbox("Checkin Plantão", options=df_checkin["valor"], key="id_checkout")

        a, b, c = st.columns([1, 1, 10])
        with a: leads = st.number_input("Leads", key="leads", min_value=0, max_value=999, step=1)
        with b: vendas = st.number_input("Vendas", key="vendas", min_value=0, max_value=999, step=1)

        if checkin:
            id_checkin = checkin.split(' | ')[0]
        else:
            st.info("⚠️ Nenhum checkin disponível")

        if st.form_submit_button("Salvar", type="primary"):
            if checkin and leads >=0 and vendas >= 0:
                inserir_checkout(id_checkin, leads, vendas)
                st.success("Checkout salvo com sucesso!")
                sleep(0.7)
                st.rerun()
            else:
                st.error("Preencha todos os campos!")

elif pills == "Permutas":
    estado_vazio("Permutas em breve", "Este formulário ainda está em construção. Por enquanto, registre a permuta no campo da Nova Visita.")
