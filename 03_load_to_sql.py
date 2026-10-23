import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Cargar variables de entorno
load_dotenv()

server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
username = os.getenv("AZURE_SQL_USER")
password = os.getenv("AZURE_SQL_PASSWORD")

def load_parquet_to_azure_sql():
    parquet_file = "nba_games_raw.parquet"
    
    if not os.path.exists(parquet_file):
        print(f"Error: No se encontró {parquet_file} localmente.")
        return

    print("Leyendo datos locales del archivo Parquet...")
    df = pd.read_parquet(parquet_file)

    # Cadena de conexión usando ODBC Driver 18 o 17 para SQL Server
    connection_string = (
        f"mssql+pyodbc://{username}:{password}@{server}/{database}"
        "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
    )

    try:
        print("Conectando a Azure SQL Database...")
        engine = create_engine(connection_string)

        print("Cargando datos a la tabla 'stg_nba_games'...")
        # Carga los datos en la tabla staging 'stg_nba_games'
        df.to_sql(name="stg_nba_games", con=engine, if_exists="replace", index=False)

        print("¡Carga exitosa! La tabla 'stg_nba_games' ha sido creada/actualizada en Azure SQL Database.")

    except Exception as e:
        print(f"Error al conectar o cargar datos a Azure SQL: {e}")

if __name__ == "__main__":
    load_parquet_to_azure_sql()