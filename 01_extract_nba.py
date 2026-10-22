import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

def extract_nba_games():
    print("Iniciando extracción de partidos de la NBA...")
    
    # Instanciamos el endpoint para buscar partidos de la temporada regular
    game_finder = leaguegamefinder.LeagueGameFinder(
        season_type_nullable='Regular Season'
    )
    
    # Obtenemos los resultados como un DataFrame de Pandas
    games = game_finder.get_data_frames()[0]
    
    print(f"Total de registros extraídos: {len(games)}")
    print("\nPrimeras 5 filas:")
    print(games[['GAME_DATE', 'TEAM_NAME', 'MATCHUP', 'PTS', 'WL']].head())
    
    # Guardamos los datos crudos en formato Parquet (eficiente para Data Lakes)
    games.to_parquet("nba_games_raw.parquet", index=False)
    print("\nDatos guardados exitosamente en 'nba_games_raw.parquet'")

if __name__ == "__main__":
    extract_nba_games()