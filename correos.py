import pandas as pd
from mandar_email import procesar_y_notificar, obtener_reglas
from pipeline import pipeline
from mandar_email import obtener_reglas


def run():

    print("********----...PROCESO 1: Pipeline Iniciado....-----****************")
    df_maestro = pipeline()

    print("********----...PROCESO 2: Procesar y Notificar....-----****************")
    embajadores= obtener_reglas()
    procesar_y_notificar(df_maestro)


if __name__ == "__main__":
    """
    Este bloque es para probar el script en un entorno de desarrollo local,
    sin necesidad de subirlo a AWS.
    """
    run()
