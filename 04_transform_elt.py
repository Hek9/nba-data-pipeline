import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()

server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
username = os.getenv("AZURE_SQL_USER")
password = os.getenv("AZURE_SQL_PASSWORD")

password_encoded = quote_plus(password)

# Mantenemos TrustServerCertificate=yes para evitar bloqueos SSL en GitHub Actions / Cloud
connection_string = (
    f"mssql+pyodbc://{username}:{password_encoded}@{server}/{database}"
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
)

def transform_nba_data():
    print("Conectando a Azure SQL Database para ejecutar transformaciones ELT (Capas Plata y Oro)...")
    engine = create_engine(connection_string)

    sql_script = """
    -- =========================================================
    -- 1. CAPA ORO: Dimensión de Equipos (dim_teams)
    -- =========================================================
    IF OBJECT_ID('dbo.dim_teams', 'U') IS NOT NULL DROP TABLE dbo.dim_teams;

    CREATE TABLE dbo.dim_teams (
        team_id BIGINT NOT NULL,
        team_name VARCHAR(100) NULL,
        team_abbreviation VARCHAR(20) NULL,
        CONSTRAINT PK_dim_teams PRIMARY KEY (team_id)
    );

    INSERT INTO dbo.dim_teams (team_id, team_name, team_abbreviation)
    SELECT 
        TEAM_ID,
        MAX(TEAM_NAME) AS team_name,
        MAX(TEAM_ABBREVIATION) AS team_abbreviation
    FROM dbo.stg_nba_games
    WHERE TEAM_ID IS NOT NULL
    GROUP BY TEAM_ID;


    -- =========================================================
    -- 2. CAPA ORO: Dimensión de Jugadores (dim_players)
    -- =========================================================
    IF OBJECT_ID('dbo.dim_players', 'U') IS NOT NULL DROP TABLE dbo.dim_players;

    CREATE TABLE dbo.dim_players (
        player_id BIGINT NOT NULL,
        player_name VARCHAR(150) NULL,
        is_active INT NULL,
        CONSTRAINT PK_dim_players PRIMARY KEY (player_id)
    );

    INSERT INTO dbo.dim_players (player_id, player_name, is_active)
    SELECT DISTINCT
        CAST(id AS BIGINT) AS player_id,
        CAST(full_name AS VARCHAR(150)) AS player_name,
        CAST(is_active AS INT) AS is_active
    FROM dbo.stg_nba_players
    WHERE id IS NOT NULL;


    -- =========================================================
    -- 3. CAPA ORO: Tabla de Hechos de Partidos (fct_games)
    -- =========================================================
    IF OBJECT_ID('dbo.fct_games', 'U') IS NOT NULL DROP TABLE dbo.fct_games;

    CREATE TABLE dbo.fct_games (
        game_id VARCHAR(50) NOT NULL,
        game_date DATE NULL,
        season VARCHAR(20) NULL,
        home_team_id BIGINT NULL,
        visitor_team_id BIGINT NULL,
        home_team_score INT NULL,
        visitor_team_score INT NULL,
        pts_diff INT NULL,
        home_win INT NULL,
        CONSTRAINT PK_fct_games PRIMARY KEY (game_id),
        CONSTRAINT FK_fct_home_team FOREIGN KEY (home_team_id) REFERENCES dbo.dim_teams(team_id),
        CONSTRAINT FK_fct_visitor_team FOREIGN KEY (visitor_team_id) REFERENCES dbo.dim_teams(team_id)
    );

    INSERT INTO dbo.fct_games (
        game_id, game_date, season, home_team_id, visitor_team_id,
        home_team_score, visitor_team_score, pts_diff, home_win
    )
    SELECT 
        h.GAME_ID,
        MAX(CAST(h.GAME_DATE AS DATE)),
        MAX(h.SEASON_ID),
        MAX(h.TEAM_ID),
        MAX(v.TEAM_ID),
        MAX(h.PTS),
        MAX(v.PTS),
        MAX(ABS(h.PTS - v.PTS)),
        MAX(CASE WHEN h.WL = 'W' THEN 1 ELSE 0 END)
    FROM dbo.stg_nba_games h
    INNER JOIN dbo.stg_nba_games v 
        ON h.GAME_ID = v.GAME_ID 
       AND h.MATCHUP LIKE '% vs. %' 
       AND v.MATCHUP LIKE '% @ %'
    GROUP BY h.GAME_ID;
    """

    try:
        with engine.connect() as connection:
            trans = connection.begin()
            print("Ejecutando sentencias DDL/DML del Esquema Estrella...")
            connection.execute(text(sql_script))
            trans.commit()
            print("¡Transformación completada exitosamente! Tablas 'dim_teams', 'dim_players' y 'fct_games' creadas e integradas en Azure SQL.")

    except Exception as e:
        print(f"Error durante la transformación: {e}")

if __name__ == "__main__":
    transform_nba_data()