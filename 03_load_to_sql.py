import os
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("AZURE_SQL_SERVER")
DATABASE = os.getenv("AZURE_SQL_DATABASE")
USERNAME = os.getenv("AZURE_SQL_USER")
PASSWORD = os.getenv("AZURE_SQL_PASSWORD")

# Crear cadena de conexión para SQLAlchemy con ODBC Driver 18
connection_string = (
    f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
)

def load_parquet_to_staging(parquet_file, staging_table_name):
    print(f"\nLeyendo datos locales de '{parquet_file}'...")
    df = pd.read_parquet(parquet_file)
    
    # Convertir nombres de columnas a minúsculas por buenas prácticas en SQL
    df.columns = [col.lower() for col in df.columns]

    print(f"Conectando a Azure SQL para cargar en la tabla de Staging: [{staging_table_name}]...")
    engine = create_engine(connection_string)

    # Carga masiva a SQL (si la tabla existe, la reemplaza)
    df.to_sql(staging_table_name, con=engine, if_exists='replace', index=False, chunksize=1000)
    print(f"✅ Tabla de Staging '{staging_table_name}' cargada exitosamente con {len(df)} registros.")

if __name__ == "__main__":
    # 1. Cargar Staging de Partidos
    load_parquet_to_staging("nba_games_raw.parquet", "stg_nba_games")
    
    # 2. Cargar Staging de Jugadores
    load_parquet_to_staging("nba_players_raw.parquet", "stg_nba_players")