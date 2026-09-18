from auth import conecta_gigaatitude, conecta_supabase
import pandas as pd

conn = conecta_supabase()
cursor = conn.cursor()

df = pd.read_excel(r"\\192.168.30.4\\grupo\\Atendimento\\Apoio_Atrix\\meso_microrregiao.xlsx")

sql_values = ",".join(
    [
        "(" + ",".join([f"'{str(v).replace("'", "''")}'" if not pd.isna(v) else "NULL" for v in row]) +")"
        for row in df.values
    ]
)
query = f"""INSERT INTO tbibge
    (macrorregiao, unidade_federativa, municipio, nm_municipio_alt,
    cidade_uf, cod_ibge, cod_meso_microrregiao, cod_mesorregiao, mesorregiao,
    cod_microrregiao, microrregiao, regiao_intermediaria, regiao_imediata,
    lat_microrregiao, long_microrregiao, lat_mesorregiao, long_mesorregiao,
    lat_cidade, long_cidade)
        VALUES {sql_values}"""

cursor.execute(query)
conn.commit()

cursor.close()
conn.close()