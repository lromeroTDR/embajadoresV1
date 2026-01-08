import pandas as pd
from mandar_email import procesar_y_notificar
from pipeline import pipeline


def run():

    df_maestro = pipeline()
    path = 'Embajadores.xlsx'
    embajadores = pd.read_excel(path)
    procesar_y_notificar(df_maestro, embajadores)


if __name__ == "__main__":
    """
    Este bloque es para probar el script en un entorno de desarrollo local,
    sin necesidad de subirlo a AWS.
    """
    run()
