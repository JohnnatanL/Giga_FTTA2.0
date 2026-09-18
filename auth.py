import pymysql
import psycopg2
from databricks import sql as dbsql
from dotenv import load_dotenv
import os

def conecta_gigaatitude():
    load_dotenv()
    conn_info = {
            'database': os.getenv('DB_GIGAATITUDE'),
            'user': os.getenv('USER_GIGAATITUDE'),
            'password': os.getenv('PSW_GIGAATITUDE'),
            'host': os.getenv('HOST_GIGAATITUDE'),
            'port': int(os.getenv('PORT_GIGAATITUDE'))
        }
    conn = pymysql.connect(**conn_info)
    return conn

def conecta_supabase():
    load_dotenv()
    conn_info = {
            'database': os.getenv('DB_SUPABASE'),
            'user': os.getenv('USER_SUPABASE'),
            'password': os.getenv('PSW_SUPABASE'),
            'host': os.getenv('HOST_SUPABASE'),
            'port': int(os.getenv('PORT_SUPABASE'))
        }
    conn = psycopg2.connect(**conn_info)
    return conn

def conecta_databricks():
    load_dotenv()
    
    try:
        # Estabelecer a conexão ODBC com Databricks
        conexao = dbsql.connect(
        server_hostname=os.getenv('HOST_DBRICKS'),
        http_path=os.getenv('HTTP_DBRICKS'),
        access_token=os.getenv('TOKEN_DBRICKS')
        )
        print('Conexão bem-sucedida')

    except dbsql.Error as e:
        print(f"Erro ao conectar:")

    return conexao