import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Obtener el token de la variable de entorno
token = os.getenv("SAMSARA_TOKEN")

# Headers actualizados
headers = {
    "accept": "application/json",
    "authorization": f"Bearer {token}"
}