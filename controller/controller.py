import datetime
from auth import conecta_supabase
import pandas as pd
import re
import streamlit as st
import  json

def limpa_telefone(telefone):
    if telefone is None:
        return None
    return re.sub(r'\D', '', str(telefone))

def get_carteira_vendedor(username):
    username = username.lower()
    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """
    WITH ultimo_periodo AS (
    SELECT MAX(periodo) AS periodo
    FROM tbcarteira
    where vendedor = %s
)
SELECT id_condominio
FROM tbcarteira
WHERE periodo = (SELECT periodo FROM ultimo_periodo) and
vendedor = %s;"""

    cursor.execute(query, (username, username))
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    conn.close()

    return df

def get_condominios(username, role):
    username = username.lower()
    if role == "consultor":
        carteira = get_carteira_vendedor(username)
        
        if carteira.empty:
            where = "and 1=0"  # nenhuma carteira -> nenhum condomínio
        else:
            ids = ",".join(
                f"""'{str(v).replace("'", "''")}'""" if not pd.isna(v) else "NULL"
                for v in carteira["id_condominio"]
            )
            where = f"and c.id in ({ids})"
    elif username == "arthur.wigner":
        where = "and c.sigla_estado in ('CE')"
    elif username == "mariane.sobreira":
        where = "and c.sigla_estado in ('SP') and c.cidade in ('Praia Grande', 'Santos', 'Guarujá', 'Bertioga')"
    elif username == "rafael.drumond":
        where = "and c.sigla_estado in ('ES') AND c.cidade in ('Guarapari')"
    else:
        where = "and 1=1"

    conn = conecta_supabase()
    cursor = conn.cursor()

    query = f"""select
        concat(c.nome, ' (',
            c.cidade, '-',
            c.sigla_estado, ', ',
            c.bairro, ', ',
            c.logradouro, ', ',
            c.numero, ', ',
            c.cep, ')'
            )
        FROM tb_condominio c
        where c.status = '11 - Liberado para venda'
        {where};
    """

    cursor.execute(query)
    result = cursor.fetchall()

    lista = [row[0] for row in result]

    cursor.close()
    conn.close()

    return lista

def round_to_quarter():
    t = datetime.datetime.now()
    # Arredonda os minutos para baixo ao múltiplo de 15 mais próximo
    rounded_minutes = (t.minute // 15) * 15
    return t.replace(minute=rounded_minutes, second=0, microsecond=0)

def get_id_condominio(nome_condominio):
    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """select
        c.id
        FROM tb_condominio c
        where concat(c.nome, ' (',
            c.cidade, '-',
            c.sigla_estado, ', ',
            c.bairro, ', ',
            c.logradouro, ', ',
            c.numero, ', ',
            c.cep, ')') = %s;"""

    cursor.execute(query, (nome_condominio,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0]

def inserir_visita(id_condominio, data_inicio, data_fim, usuario, tipo_forms, subtipo_forms, response, observacoes, status_entrada):
    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """INSERT INTO tbvisita (
				                    id_condominio,
									dt_inicio,
									dt_fim,
                                    usuario,
									tipo_forms,
									subtipo_forms,
                                    response,
                                    observacoes,
                                    status_entrada
									)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    
    cursor.execute(query, (id_condominio, data_inicio, data_fim, usuario, tipo_forms, subtipo_forms, response, observacoes, status_entrada))
    conn.commit()

    cursor.close()
    conn.close()

def get_visitas(usuarios):
    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """select 
    v.id as "idVisita",
    concat(
        c.nome, ' (',
        c.cidade, '-',
        c.sigla_estado, ', ',
        c.bairro, ', ',
        c.logradouro, ', ',
        c.numero, ', ',
        c.cep, ')'
    ) as condominio,
    to_char(v.dt_inicio, 'DD/MM/YYYY HH24:MI') as "Data Inicio",
    to_char(v.dt_fim, 'DD/MM/YYYY HH24:MI') as "Data Fim",
    v.usuario as "Usuario",
    v.response->>'qtde_torres'     AS "QtdeTorres",
    v.response->>'qtde_andares'    AS "QtdeAndares",
    v.response->>'qtde_apto_andar' AS "QtdeAptoPorAndar",
    v.response->>'permuta'         AS "Permuta",
    (
        SELECT string_agg(valor, ' | ')
        FROM jsonb_array_elements_text(v.response::jsonb->'concorrencia') AS valor
    ) AS "Concorrencia",
    (
        SELECT string_agg(
            concat_ws(
                ' - ',
                contato->>'Nome',
                contato->>'Cargo',
                contato->>'Telefone'
            ),
            ' | '
        )
        FROM jsonb_array_elements(v.response::jsonb->'contatos') AS contato
    ) AS "Contatos",
    (
        SELECT string_agg(
            concat_ws(
                ' - ',
                parceiro->>'Nome da Empresa',
                parceiro->>'Tipo de Negócio',
                parceiro->>'Pessoa de Contato',
                parceiro->>'Telefone do Parceiro'
            ),
            ' | '
        )
        FROM jsonb_array_elements(v.response::jsonb->'parceiros') AS parceiro
    ) AS "Parceiros"
FROM tbvisita v
left join tb_condominio c on v.id_condominio = c.id
where usuario in (%s);"""

    cursor.execute(query, (usuarios,))
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    conn.close()

    return df

def get_consultores(gestor, dt_inicio, dt_fim):
    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """SELECT
        distinct(concat(u.nome, ' (', u.username, ')'))
    FROM tbusuarios u
    LEFT JOIN tbhierarquia h on u.id = h.id_usuario
    WHERE (h.gestor_direto = %s) and (h.periodo between %s and %s);"""

    cursor.execute(query, (gestor, dt_inicio, dt_fim))
    result = cursor.fetchall()

    lista = []
    for row in result:
        lista.append(row[0])

    cursor.close()
    conn.close()

    return lista

def get_visita_by_id(id_visita):
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """select
        concat(
            c.nome, ' (',
            c.cidade, '-',
            c.sigla_estado, ', ',
            c.bairro, ', ',
            c.logradouro, ', ',
            c.numero, ', ',
            c.cep, ')'
        ) as condominio,
        v.*
    FROM tbvisita v
    left JOIN tb_condominio c on v.id_condominio = c.id
    where v.id = %s;"""

    cursor.execute(query, (id_visita,))
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    conn.close()

    return df

def update_visita(id_visita, response):
    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """UPDATE tbvisita
    SET response = %s
    WHERE id = %s;"""

    cursor.execute(query, (response, id_visita))
    conn.commit()

    cursor.close()
    conn.close()

def validar_lead_repetido(condominio, telefone, banco):
    conn = conecta_supabase()
    cursor = conn.cursor()

    id_condominio = get_id_condominio(condominio)
    telefone_limpo = limpa_telefone(telefone)

    if banco =="tbleads":
        query = """select *
        from tbleads
        where id_condominio = %s
        and telefone = %s;"""
    elif banco =="tbficha":
        query = """select *
        from tbficha
        where id_condominio = %s
        and telefone = %s;"""
    cursor.execute(query, (id_condominio, telefone_limpo))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return True
    else:
        return False

def inserir_leads(condominio, nome, telefone, apt_bloco, vendedor):

    id_condominio = get_id_condominio(condominio)
    telefone_limpo = limpa_telefone(telefone)

    conn = conecta_supabase()
    cursor = conn.cursor()

    query = """INSERT INTO tbleads (
                id_condominio,
                nome,
                telefone,
                bloco_apt,
                vendedor
                )
                VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(query, (id_condominio, nome, telefone_limpo, apt_bloco, vendedor))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def inserir_ficha(condominio, nome, cargo, telefone, aniversario, torres, andares, apt_andar, vendedor):
    id_condominio = get_id_condominio(condominio)
    telefone_limpo = limpa_telefone(telefone)

    conn = conecta_supabase()
    cursor = conn.cursor()

    hp_real = torres * andares * apt_andar

    query = """INSERT INTO tbficha (
                id_condominio,
                nome,
                cargo,
                telefone,
                aniversario,
                torres,
                andares,
                apt_andar,
                vendedor,
                hp
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    cursor.execute(query, (id_condominio, nome, cargo, telefone_limpo, aniversario, torres, andares, apt_andar, vendedor, hp_real))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def inserir_checkin(condominio, dt_inicio, dt_fim, vendedor):
    id_condominio = get_id_condominio(condominio)
    vendedor = vendedor.lower()
    
    conn = conecta_supabase()
    cursor = conn.cursor()

    status = False
    query = """INSERT INTO tbacao (
                id_condominio,
                dt_inicio,
                dt_fim,
                vendedor,
                status
                )
                VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(query, (id_condominio, dt_inicio, dt_fim, vendedor, status))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def ler_checkout(vendedor):
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    select concat_ws(' | ',
    a.id,
    concat('Condominio: ',c.nome),
    concat('Data Inicio: ', TO_CHAR(a.dt_inicio, 'DD/MM/YYYY HH24:MI')),
    concat('Data Fim: ', TO_CHAR(a.dt_fim, 'DD/MM/YYYY HH24:MI'))
    ) as valor
    from tbacao a
    left join tb_condominio c on a.id_condominio = c.id
    where a.status = False and
    a.vendedor = %s;"""
    cursor.execute(query, (vendedor,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(result, columns=["valor"])
    return df
    
def inserir_checkout(id, leads, vendas):
    conn = conecta_supabase()
    cursor = conn.cursor()
    
    query = """UPDATE tbacao
    SET status = True,
    leads = %s,
    vendas = %s
    WHERE id = %s;"""
    cursor.execute(query, (leads, vendas, id))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def get_ficha(condo):
    id_condominio = get_id_condominio(condo)
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    select *
    from tbvisita
    where id_condominio = %s;"""
    cursor.execute(query, (id_condominio,))
    result = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]  # pega ANTES de fechar
    cursor.close()
    conn.close()

    df = pd.DataFrame(result, columns=colunas).reset_index(drop=True)

    # parse do response caso venha como string
    df['response'] = df['response'].apply(
        lambda x: json.loads(x) if isinstance(x, str) else (x or {})
    )

    # achata os campos escalares + traz concorrencia/contatos como colunas
    expandido = pd.json_normalize(df['response']).reset_index(drop=True)
    df = df.drop(columns=['response']).join(expandido)

    # concorrencia (lista de strings) -> texto separado por vírgula
    if 'concorrencia' in df.columns:
        df['concorrencia'] = df['concorrencia'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else x
        )

    # contatos (lista de dicts) -> uma linha por contato + colunas com prefixo
    if 'contatos' in df.columns:
        df['contatos'] = df['contatos'].apply(
            lambda x: x if isinstance(x, list) and x else [{}]
        )
        df = df.explode('contatos').reset_index(drop=True)
        contatos_exp = pd.json_normalize(df['contatos']).add_prefix('contato_')
        df = df.drop(columns=['contatos']).join(contatos_exp)

        # contatos (lista de dicts) -> uma linha por contato + colunas com prefixo
    if 'parceiros' in df.columns:
        df['parceiros'] = df['parceiros'].apply(
            lambda x: x if isinstance(x, list) and x else [{}]
        )
        df = df.explode('parceiros').reset_index(drop=True)
        parceiros_exp = pd.json_normalize(df['parceiros']).add_prefix('parceiro_')
        df = df.drop(columns=['parceiros']).join(parceiros_exp)

    return df

def resume_condominio(df):
    df = df.copy()
    df['created_at'] = pd.to_datetime(df['created_at'])

    # ---- 1) métricas da visita MAIS RECENTE (por created_at) ----
    recente = df.loc[df['created_at'].idxmax()]

    # ---- helpers ----
    def limpa(v):
        if pd.isna(v):
            return None
        if isinstance(v, float) and v.is_integer():   # 32742267.0 -> "32742267"
            return str(int(v))
        s = str(v).strip()
        return s if s else None

    def concat_distinto(series, sep='; '):
        vistos, out = set(), []
        for v in series:
            s = limpa(v)
            if s and s.lower() not in vistos:
                vistos.add(s.lower())
                out.append(s)
        return sep.join(out)

    # ---- 2) contatos distintos: Nome | Cargo | Telefone | Email ----
    def linha_contato(r):
        partes = [limpa(r['contato_Nome']), limpa(r['contato_Cargo']),
                  limpa(r['contato_Telefone']), limpa(r['contato_Email'])]
        return ' | '.join(p for p in partes if p) or None

    contatos = concat_distinto(df.apply(linha_contato, axis=1))

    # ---- 3) parceiros distintos: Empresa | Tipo | Contato | Telefone ----
    def linha_parceiro(r):
        partes = [limpa(r['parceiro_Nome da Empresa']), limpa(r['parceiro_Tipo de Negócio']),
                  limpa(r['parceiro_Pessoa de Contato']), limpa(r['parceiro_Telefone do Parceiro'])]
        return ' | '.join(p for p in partes if p) or None

    parceiros = concat_distinto(df.apply(linha_parceiro, axis=1))

    # ---- 4) concorrencia: split por virgula + outros_conc, distinto ----
    concorrentes, ordem = set(), []
    for col in ['concorrencia', 'outros_conc']:
        for v in df[col]:
            s = limpa(v)
            if not s:
                continue
            for item in (i.strip() for i in s.split(',')):
                if item and item.lower() not in concorrentes:
                    concorrentes.add(item.lower())
                    ordem.append(item)
    concorrencia = ', '.join(ordem)

    return pd.DataFrame([{
        'id_condominio': recente['id_condominio'],
        'qtde_torres': recente['qtde_torres'],
        'qtde_andares': recente['qtde_andares'],
        'qtde_apto_andar': recente['qtde_apto_andar'],
        'contatos': contatos,
        'parceiros': parceiros,
        'concorrencia': concorrencia,
    }])