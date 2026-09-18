import streamlit as st
from controller.data_control import visitas_e_vendas
from controller.hidden import hidden
from stylo.tema import aplicar_tema, cabecalho, resumo_numeros, CORES

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
hidden()
aplicar_tema("muralha")

cabecalho("Projeto Muralha", "Visitas, prédios únicos e vendas por vendedor.")

df_visitas, df_vendas = visitas_e_vendas()

visitas_agg = (
    df_visitas
    .groupby("usuario", dropna=False)
    .agg(
        total_visitas   = ("qtdevisita", "sum"),
        predios_unicos  = ("idcondominio", "nunique"),
    )
    .reset_index()
    .rename(columns={"usuario": "username"})
)

# ── 2. df_vendas ──────────────────────────────────────────────────────────────
# Extrai o username do e-mail  (ex: "basilio.junior@alloha.com" → "basilio.junior")
df_vendas["username"] = df_vendas["email_vendedor"].str.split("@").str[0]

vendas_agg = (
    df_vendas
    .groupby("username", dropna=False)
    .agg(
        total_vendas = ("id_contrato", "count"),
    )
    .reset_index()
)

# ── 3. Une os dois ────────────────────────────────────────────────────────────
df_final = (
    visitas_agg
    .merge(vendas_agg, on="username", how="left")
    .fillna(0)
)

# Converte para inteiro após o fillna
df_final[["total_visitas", "predios_unicos", "total_vendas"]] = (
    df_final[["total_visitas", "predios_unicos", "total_vendas"]].astype(int)
)

# Métricas resumo
resumo_numeros([
    ("Vendedores", len(df_final), CORES["noite"]),
    ("Total visitas", int(df_final["total_visitas"].sum()), CORES["verde"]),
    ("Prédios únicos", int(df_final["predios_unicos"].sum()), CORES["ciano"]),
    ("Total vendas", int(df_final["total_vendas"].sum()), "destaque"),
])

# Tabela principal
st.dataframe(
    df_final.sort_values("total_vendas", ascending=False).reset_index(drop=True),
    width="stretch",
    column_config={
        "username":       st.column_config.TextColumn("Usuário",        width="large"),
        "total_visitas":  st.column_config.NumberColumn("Visitas",       format="%d"),
        "predios_unicos": st.column_config.NumberColumn("Prédios únicos", format="%d"),
        "total_vendas":   st.column_config.NumberColumn("Vendas",        format="%d"),
    },
    hide_index=True,
)