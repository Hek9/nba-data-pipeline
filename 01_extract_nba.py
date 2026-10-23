import os
import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import commonallplayers

# --- Cabeceras compartidas para evadir Firewall (Basado en Repo Oficial) ---
CUSTOM_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nba.com/stats/',
    'Origin': 'https://www.nba.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

def get_data_with_fallback(endpoint_class, output_filename, entity_name):
    """
    Función genérica para extraer datos de la API de NBA.
    Si el firewall bloquea, busca el archivo local de respaldo (.parquet).
    """
    try:
        print(f"\n--- Iniciando extracción de {entity_name} ---")
        print(f"Intentando conectar a la API de stats.nba.com para {entity_name}...")
        
        # Eliminamos el timeout para forzar la conexión
        api_caller = endpoint_class(headers=CUSTOM_HEADERS)
        df = api_caller.get_data_frames()[0]
        
        # Guardado del Parquet en crudo
        df.to_parquet(output_filename, index=False)
        print(f"✅ ¡Extracción exitosa desde la API en vivo! Archivo guardado como '{output_filename}'.")
        
    except Exception as e:
        print("====================================================================")
        print(f"❌ ALERTA: El firewall de la NBA bloqueó la descarga de {entity_name}.")
        print(f"Detalle: {e}")
        print("Implementando estrategia de Fallback (Respaldo)...")
        print("====================================================================")
        
        if os.path.exists(output_filename):
            print(f"✅ ¡Respaldo activado! Se utilizará el archivo histórico '{output_filename}' del repositorio.")
        else:
            raise Exception(f"Fallo crítico: No se encontró la API ni el archivo '{output_filename}'.")

def extract_nba_games():
    """Extrae la tabla histórica de partidos"""
    get_data_with_fallback(
        endpoint_class=leaguegamefinder.LeagueGameFinder,
        output_filename="nba_games_raw.parquet",
        entity_name="PARTIDOS (fct_games)"
    )

def extract_nba_players():
    """Extrae el catálogo maestro de jugadores"""
    get_data_with_fallback(
        endpoint_class=commonallplayers.CommonAllPlayers,
        output_filename="nba_players_raw.parquet",
        entity_name="JUGADORES (dim_players)"
    )

if __name__ == "__main__":
    print("INICIANDO PIPELINE DE EXTRACCIÓN - FASE 1")
    
    # 1. Extraer Juegos
    extract_nba_games()
    
    # Pausa intencional de 10 segundos para parecer humanos (mejorada)
    time.sleep(10)
    
    # 2. Extraer Jugadores
    extract_nba_players()
    
    print("\n¡Fase de extracción finalizada correctamente!")