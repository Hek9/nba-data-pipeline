import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Cargar variables de entorno locales si existen
load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "nba-raw-data"

# Lista de archivos que conforman nuestra capa Bronce
FILES_TO_UPLOAD = [
    "nba_games_raw.parquet",
    "nba_players_raw.parquet"
]

def upload_files_to_blob():
    print("Iniciando conexión con Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Crear el contenedor si no existe
    if not container_client.exists():
        container_client.create_container()
        print(f"Contenedor '{CONTAINER_NAME}' creado exitosamente.")

    for file_name in FILES_TO_UPLOAD:
        if os.path.exists(file_name):
            print(f"Subiendo '{file_name}' hacia el contenedor '{CONTAINER_NAME}'...")
            blob_client = container_client.get_blob_client(file_name)
            
            with open(file_name, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"✅ ¡{file_name} subido exitosamente a la nube!")
        else:
            print(f"❌ Advertencia: No se encontró el archivo local '{file_name}'.")

if __name__ == "__main__":
    upload_files_to_blob()