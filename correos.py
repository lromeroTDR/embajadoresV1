import logging
from mandar_info import procesar_y_notificar
from pipeline import pipeline



logging.basicConfig(
    filename="logg_correos.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def run():

    print("        ----   ...  PROCESO 1: Pipeline Iniciado  ....   ----        ")
    df_maestro = pipeline()

    print("        ----   ...  PROCESO 2: Procesar y Notificar  ....   ----        ")
    procesar_y_notificar(df_maestro)


if __name__ == "__main__":
    """
    Este bloque es para probar el script en un entorno de desarrollo local,
    sin necesidad de subirlo a AWS.
    """
    run()
