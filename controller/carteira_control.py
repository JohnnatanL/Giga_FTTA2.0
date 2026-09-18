"""
Gerenciador de Carteira — leitura e edição da tbcarteira no MÊS ATUAL.

Premissas (ajuste aqui se o banco for diferente):
- tbcarteira(periodo, vendedor, id_condominio); vendedor = username em minúsculo
- periodo do mês = 1º dia do mês (date_trunc('month', current_date))
- tbhierarquia(id_usuario, gestor_direto, periodo) define a equipe do gestor
- excluir = DELETE da linha no mês atual (meses anteriores nunca são tocados)
"""
import pandas as pd
from auth import conecta_supabase

# Filtro do mês atual — funciona com periodo em date, timestamp ou texto ISO
MES_ATUAL = "date_trunc('month', periodo::date) = date_trunc('month', current_date)"
MES_ANTERIOR = "date_trunc('month', periodo::date) = date_trunc('month', current_date) - interval '1 month'"
PERIODO_INSERT = "date_trunc('month', current_date)::date"

LABEL_CONDOMINIO = """concat(c.nome, ' (', c.cidade, '-', c.sigla_estado, ', ', c.bairro, ', ',
    c.logradouro, ', ', c.numero, ', ', c.cep, ')')"""


def _consulta(query, params=()):
    conn = conecta_supabase()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        cols = [d[0] for d in cur.description] if cur.description else []
        return pd.DataFrame(cur.fetchall(), columns=cols)
    finally:
        cur.close()
        conn.close()


def _executa(query, params=()):
    conn = conecta_supabase()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        afetadas = cur.rowcount
        conn.commit()
        return afetadas
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def listar_vendedores(role, username):
    """Admin/planejamento: todos os consultores ativos. Gestão: só a equipe do mês atual."""
    if role == "gestao":
        return _consulta(
            """
            SELECT DISTINCT u.nome, lower(u.username) AS username
            FROM tbusuarios u
            JOIN tbhierarquia h ON u.id = h.id_usuario
            WHERE h.gestor_direto = %s
              AND date_trunc('month', h.periodo::date) = date_trunc('month', current_date)
              AND u.is_ativo = '1'
            ORDER BY u.nome;
            """,
            (username.lower(),),
        )
    return _consulta(
        """
        SELECT nome, lower(username) AS username
        FROM tbusuarios
        WHERE perfil = 'consultor' AND is_ativo = '1'
        ORDER BY nome;
        """
    )


def get_carteira_mes(vendedor, anterior=False):
    filtro = MES_ANTERIOR if anterior else MES_ATUAL
    return _consulta(
        f"""
        SELECT k.id_condominio, {LABEL_CONDOMINIO} AS condominio,
               c.cidade, c.sigla_estado AS uf, c.bairro
        FROM tbcarteira k
        LEFT JOIN tb_condominio c ON c.id::text = k.id_condominio::text
        WHERE lower(k.vendedor) = %s AND {filtro.replace('periodo', 'k.periodo')}
        ORDER BY c.nome;
        """,
        (vendedor.lower(),),
    )


def ids_por_rotulo(rotulos):
    """Converte os rótulos do selectbox (mesmo formato do get_condominios) em ids."""
    if not rotulos:
        return {}
    df = _consulta(
        f"SELECT {LABEL_CONDOMINIO} AS rotulo, c.id FROM tb_condominio c WHERE {LABEL_CONDOMINIO} = ANY(%s::text[]);",
        (list(rotulos),),
    )
    return dict(zip(df["rotulo"], df["id"]))


def donos_no_mes(ids, exceto_vendedor):
    """Prédios que já estão na carteira de OUTRO vendedor no mês atual."""
    if not ids:
        return pd.DataFrame(columns=["id_condominio", "vendedor"])
    return _consulta(
        f"""
        SELECT id_condominio, lower(vendedor) AS vendedor
        FROM tbcarteira
        WHERE id_condominio::text = ANY(%s::text[]) AND lower(vendedor) <> %s AND {MES_ATUAL};
        """,
        ([str(i) for i in ids], exceto_vendedor.lower()),
    )


def incluir_predios(vendedor, ids):
    if not ids:
        return 0
    return _executa(
        f"""
        INSERT INTO tbcarteira (periodo, vendedor, id_condominio)
        SELECT {PERIODO_INSERT}, %s, c.id
        FROM tb_condominio c
        WHERE c.id::text = ANY(%s::text[])
          AND NOT EXISTS (
            SELECT 1 FROM tbcarteira k
            WHERE k.id_condominio::text = c.id::text AND lower(k.vendedor) = %s
              AND {MES_ATUAL.replace('periodo', 'k.periodo')}
        );
        """,
        (vendedor.lower(), [str(i) for i in ids], vendedor.lower()),
    )


def excluir_predios(vendedor, ids):
    if not ids:
        return 0
    return _executa(
        f"""
        DELETE FROM tbcarteira
        WHERE lower(vendedor) = %s AND id_condominio::text = ANY(%s::text[]) AND {MES_ATUAL};
        """,
        (vendedor.lower(), [str(i) for i in ids]),
    )


def copiar_mes_anterior(vendedor):
    """Replica a carteira do mês anterior para o mês atual (sem duplicar)."""
    anterior = get_carteira_mes(vendedor, anterior=True)
    return incluir_predios(vendedor, anterior["id_condominio"].tolist())
