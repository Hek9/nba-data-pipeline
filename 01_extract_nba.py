import os
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

def extract_nba_games():
    print("Iniciando extracción desde API NBA...")
    output_file = "nba_games_raw.parquet"
    
    custom_headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'Connection': 'keep-alive'
    }

    try:
        print("Intentando conectar a stats.nba.com desde GitHub Actions...")
        # Reducimos a 15 segundos porque sabemos que si bloquea, no responderá
        game_finder = leaguegamefinder.LeagueGameFinder(headers=custom_headers, timeout=15)
        games = game_finder.get_data_frames()[0]
        games.to_parquet(output_file, index=False)
        print(f"¡Extracción exitosa desde la API en vivo! Archivo guardado como '{output_file}'.")
        
    except Exception as e:
        print("====================================================================")
        print("ALERTA: El firewall de la NBA bloqueó la IP del servidor en la nube.")
        print(f"Detalle: {e}")
        print("Implementando estrategia de Fallback (Respaldo)...")
        print("====================================================================")
        
        # Estrategia de contingencia: Usar el archivo local del repositorio
        if os.path.exists(output_file):
            print(f"¡Respaldo activado! Se utilizará el archivo histórico '{output_file}' del repositorio.")
            print("El pipeline continuará con los datos de respaldo hacia Azure.")
        else:
            raise Exception(f"Fallo crítico: No se encontró la API ni el archivo '{output_file}'.")

if __name__ == "__main__":
    extract_nba_games()