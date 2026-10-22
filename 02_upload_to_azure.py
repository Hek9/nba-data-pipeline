import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Cargar credenciales desde el archivo .env
load_dotenv()

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def upload_file_to_azure():
    container_name = "nba-raw-data"
    local_file_name = "nba_games_raw.parquet"
    blob_name = "raw/nba_games_raw.parquet"

    if not os.path.exists(local_file_name):
        print(f"Error: El archivo {local_file_name} no existe localmente. Ejecuta primero 01_extract_nba.py")
        return

    try:
        print("Conectando con Azure Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print(f"Subiendo '{local_file_name}' hacia el contenedor '{container_name}'...")
        with open(local_file_name, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print("Carga completada exitosamente en la nube.")

    except Exception as e:
        print(f"Ocurrió un error al subir el archivo: {e}")

if __name__ == "__main__":
    upload_file_to_azure()