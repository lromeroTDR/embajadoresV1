import os
import glob
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


required_env_vars = [
    "BD_DRIVER",           # Ruta al driver ODBC (usado principalmente en desarrollo local).
    "BD_SERVER",           # Dirección del servidor de la base de datos.
    "BD_DATABASE",         # Nombre de la base de datos a la que conectarse.
    "BD_USERNAME",         # Usuario para la conexión a la base de datos.
    "BD_PASSWORD",         # Contraseña para la conexión a la base de datos.
    "BD_TABLE_HISTORICO",  # Nombre de la tabla para los datos históricos (cargas diarias).
    "BD_TABLE_ACTUAL"      # Nombre de la tabla para los datos del día en curso (se sobreescribe).
]

# Se comprueba si alguna de las variables requeridas no está definida.
#missing = [k for k in required_env_vars if not os.getenv(k)]
#if missing:
    # Si faltan variables, se lanza un error inmediatamente. Esto previene fallos
    # inesperados más adelante y deja claro qué configuración falta.
 #   raise EnvironmentError(f"Faltan las siguientes variables de entorno: {', '.join(missing)}")

# --- ASIGNACIÓN DE VARIABLES A CONSTANTES ---
# Se asignan los valores de las variables de entorno a constantes de Python
# para un acceso más fácil y legible en el resto del código.
# Por esto (para que coincida con el import de db.py):
BD_TABLE_HISTORICO = os.getenv("BD_TABLE_HISTORICO")
BD_TABLE_ACTUAL = os.getenv("BD_TABLE_ACTUAL")
BD_DRIVER = os.getenv("BD_DRIVER")

def conn_str() -> str:
    """
    Construye y retorna la cadena de conexión para la base de datos (ODBC).

    Esta función es dinámica:
    - En un contenedor (entorno de producción), busca la ruta del driver ODBC
      automáticamente en la ruta estándar `/opt/microsoft/msodbcsql18/lib64/`.
    - Para desarrollo local, se usa la variable BD_DRIVER.

    Returns:
        str: La cadena de conexión completa para pyodbc.
    """
    # Para desarrollo local, se usa la variable BD_DRIVER.
    driver_path = BD_DRIVER 

    # Se construye la cadena de conexión con los parámetros base.
    connection_string = (
        f'DRIVER={driver_path};'
        f'SERVER={os.getenv("BD_SERVER")};'
        f'DATABASE={os.getenv("BD_DATABASE")};'
    )

    # Añadir autenticación basada en usuario/contraseña si están presentes, de lo contrario, usar autenticación de Windows.
    if os.getenv("BD_USERNAME") and os.getenv("BD_PASSWORD"):
        connection_string += (
            f'UID={os.getenv("BD_USERNAME")};'
            f'PWD={os.getenv("BD_PASSWORD")};'
        )
    else:
        connection_string += 'Trusted_Connection=yes;'

    # Opciones adicionales para la conexión con SQL Server en entornos modernos.
    connection_string += 'TrustServerCertificate=yes;Encrypt=yes;'
    
    return connection_string
