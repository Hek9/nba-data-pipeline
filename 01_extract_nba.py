import os
import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

def extract_nba_games():
    print("Iniciando extracción de partidos de la NBA desde GitHub Actions...")

    # Cabeceras para simular un navegador real y evitar bloqueos en stats.nba.com
    custom_headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'Connection': 'keep-alive'
    }

    max_retries = 3
    games = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Conectando a stats.nba.com (Intento {attempt}/{max_retries})...")
            game_finder = leaguegamefinder.LeagueGameFinder(
                headers=custom_headers,
                timeout=60
            )
            games = game_finder.get_data_frames()[0]
            print("¡Datos recibidos correctamente de la API!")
            break
        except Exception as e:
            print(f"El intento {attempt} falló debido a tiempo de espera/bloqueo: {e}")
            if attempt < max_retries:
                print("Esperando 5 segundos antes del siguiente intento...")
                time.sleep(5)
            else:
                raise Exception("No se pudo conectar a la API de la NBA tras varios intentos.") from e

    output_file = "nba_games_raw.parquet"
    games.to_parquet(output_file, index=False)
    print(f"¡Extracción exitosa! Archivo local guardado como '{output_file}' con {len(games)} filas.")

if __name__ == "__main__":
    extract_nba_games()