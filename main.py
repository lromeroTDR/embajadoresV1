import pandas as pd
from mandar_info import procesar_y_notificar, obtener_reglas
from pipeline import pipeline
from db import gestionar_guardado
from rango_tiempo import fecha_z
from datetime import datetime



def run():

    print("********----...PROCESO 1: Pipeline Iniciado....-----****************")
    df_maestro = pipeline()
    print("********----...PROCESO 2: Guardar en Base de datos....-----****************")
    _, end_rfc = fecha_z()
    # Convertir la fecha de formato RFC3339 a un formato amigable para SQL Server DATETIME
    dt_object = datetime.fromisoformat(end_rfc.replace('Z', '+00:00'))
    db_friendly_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    gestionar_guardado(df_maestro, db_friendly_date)
    print("********----...PROCESO 3: Procesar y Notificar....-----****************")
    embajadores= obtener_reglas()
    procesar_y_notificar(df_maestro)


if __name__ == "__main__":
    """
    Este bloque es para probar el script en un entorno de desarrollo local,
    sin necesidad de subirlo a AWS.
    """
    run()
