import pandas as pd
from auth import conecta_databricks, conecta_supabase
import streamlit as st
from controller.controller import (
    get_condominios,
    round_to_quarter,
    get_id_condominio,
    get_visitas,
    get_consultores
)
import calendar

def buscar_vendedores():

    conn_sup = conecta_supabase()
    cursor_sup = conn_sup.cursor()

    query = """select concat(lower(username), '@alloha.com') as consultor
    from tbusuarios where perfil in ('consultor', 'gestao');"""

    cursor_sup.execute(query)
    result = cursor_sup.fetchall()

    lista_consultores = []
    for row in result:
        lista_consultores.append(f"'{row[0]}'")
    lista_consultores = ",".join(lista_consultores)

    cursor_sup.close()
    conn_sup.close()

    return lista_consultores


def vendas():
    lista_consultores = buscar_vendedores()
    
    conn = conecta_databricks()
    cursor = conn.cursor()


    query = f"""select
        v.*,
        ftta.flag_ftta,
        year (a.data_ativacao) as ano_ativacao,
        month (a.data_ativacao) as mes_ativacao,
        day (a.data_ativacao) as dia_ativacao
    from gold.kpis_oficiais.tbl_kpi_vendas as v
    left join gold.base.fato_marcador_cliente_ftta as ftta
    on v.id_contrato = ftta.contrato_codigo
    left join gold.base.fato_primeira_ativacao as a
    on v.id_contrato = a.id_contrato
    where lower(email_vendedor) in ({lista_consultores})
    and ano = 2026
    and mes >= 5"""

    cursor.execute(query)
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[description[0] for description in cursor.description])
    
    return df

def visitas_e_vendas():

    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """select
    c.id as idCondominio,
	c.nome as Condominio,
	c.cep as CEP,
	c.numero as Numero,
	v.usuario,
	count(v.id) as QtdeVisita
from tbvisita v
left join tb_condominio c on v.id_condominio = c.id
group by c.id, c.nome, c.cep, c.numero, v.usuario;"""

    cursor.execute(query)
    result = cursor.fetchall()

    df_visitas = pd.DataFrame(result, columns=[description[0] for description in cursor.description])

    cursor.close()
    conn.close()

    df_vendas = vendas()

    return df_visitas, df_vendas


#print(buscar_vendedores())

def acoes_gestor(periodo, gestor):
    conn = conecta_supabase()
    cursor = conn.cursor()

    ultimo = periodo.replace(day=calendar.monthrange(periodo.year, periodo.month)[1])

    query = """select concat(c.nome, ' (',
            c.cidade, '-',
            c.sigla_estado, ', ',
            c.bairro, ', ',
            c.logradouro, ', ',
            c.numero, ', ',
            c.cep, ')') as Condominio, a.*, h.gestor_direto as gestor
from
(
select id_condominio, dt_inicio as data, usuario as Executivo, 'Visita' as Tipo
from tbvisita
where dt_inicio between %s and %s
union
select id_condominio, dt_inicio as Data, vendedor as Executivo, 'Acao de Vendas' as Tipo
from tbacao
where dt_inicio between %s and %s
union
select id_condominio, created_at as Data, vendedor as Executivo, 'Ficha Cadastro' as Tipo
from tbficha
where created_at between %s and %s
union
select id_condominio, created_at as data, vendedor as Executivo, 'Lead' as Tipo
from tbleads
where created_at between %s and %s
) a
left join tbusuarios u on a.executivo = u.username
left join tb_condominio c on a.id_condominio = c.id
left join tbhierarquia h on u.id = h.id_usuario and h.periodo = %s
where h.gestor_direto = %s"""

    cursor.execute(query, (periodo, ultimo, periodo, ultimo, periodo, ultimo, periodo, ultimo, periodo, gestor))
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[description[0] for description in cursor.description])

    cursor.close()
    conn.close()

    df.columns = [c.capitalize() for c in df.columns]

    df.drop(columns=['Id_condominio'], inplace=True)

    return df

def acoes_consultor(periodo, consultor):
    conn = conecta_supabase()
    cursor = conn.cursor()

    ultimo = periodo.replace(day=calendar.monthrange(periodo.year, periodo.month)[1])

    query = """select concat(c.nome, ' (',
            c.cidade, '-',
            c.sigla_estado, ', ',
            c.bairro, ', ',
            c.logradouro, ', ',
            c.numero, ', ',
            c.cep, ')') as Condominio, a.*
from
(
select id_condominio, dt_inicio as data, usuario as Executivo, 'Visita' as Tipo
from tbvisita
where dt_inicio between %s and %s
union
select id_condominio, dt_inicio as Data, vendedor as Executivo, 'Acao de Vendas' as Tipo
from tbacao
where dt_inicio between %s and %s
union
select id_condominio, created_at as Data, vendedor as Executivo, 'Ficha Cadastro' as Tipo
from tbficha
where created_at between %s and %s
union
select id_condominio, created_at as data, vendedor as Executivo, 'Lead' as Tipo
from tbleads
where created_at between %s and %s
) a
left join tb_condominio c on a.id_condominio = c.id
where a.Executivo = %s"""

    cursor.execute(query, (periodo, ultimo, periodo, ultimo, periodo, ultimo, periodo, ultimo, consultor))
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[description[0] for description in cursor.description])

    cursor.close()
    conn.close()
    
    df.columns = [c.capitalize() for c in df.columns]

    df.drop(columns=['Id_condominio'], inplace=True)

    return df

def acoes_planej(periodo):
    conn = conecta_supabase()
    cursor = conn.cursor()

    ultimo = periodo.replace(day=calendar.monthrange(periodo.year, periodo.month)[1])

    query = """select a.*, h.gestor_direto as gestor
from
(
    select id_condominio, dt_inicio as Data, vendedor as Executivo, 'Acao de Vendas' as Tipo
    from tbacao
    where dt_inicio between %s and %s
    union
    select id_condominio, created_at as Data, vendedor as Executivo, 'Ficha Cadastro' as Tipo
    from tbficha
    where created_at between %s and %s
    union
    select id_condominio, created_at as Data, vendedor as Executivo, 'Lead' as Tipo
    from tbleads
    where created_at between %s and %s
) a
left join tbusuarios u on a.executivo = u.username
left join tbhierarquia h on u.id = h.id_usuario and h.periodo = %s
where a.Executivo not in ('john', 'johnteste', 'vitor.horacio', 'jose.canale', 'juliana.maximo');"""

    cursor.execute(query, (periodo, ultimo, periodo, ultimo, periodo, ultimo, periodo))
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[description[0] for description in cursor.description])

    df.columns = [c.capitalize() for c in df.columns]

    cursor.close()
    conn.close()

    return df