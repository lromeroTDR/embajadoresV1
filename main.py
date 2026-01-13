import pandas as pd
from mandar_email import procesar_y_notificar    
from pipeline import pipeline
from db import gestionar_guardado
from rango_tiempo import fecha_z
from datetime import datetime



def run():

    print("********----...PROCESO 1: Pipeline Iniciado....-----****************")
    df_maestro = pipeline()

    # --- INICIO: Verificación y limpieza de duplicados para 'Vehiculo' ---
    # Asumimos que 'Vehiculo' es la clave primaria y no debería tener duplicados.
    if df_maestro['Vehiculo'].duplicated().any():
        print("\n¡ADVERTENCIA! Se encontraron vehículos duplicados en los datos procesados.")
        print("Filas duplicadas (incluyendo todas las ocurrencias):")
        # Muestra todas las filas que tienen valores duplicados en la columna 'Vehiculo'
        print(df_maestro[df_maestro['Vehiculo'].duplicated(keep=False)].sort_values('Vehiculo'))
        
        # Elimina los duplicados, conservando solo la primera aparición
        df_maestro.drop_duplicates(subset=['Vehiculo'], keep='first', inplace=True)
        print("\nSe eliminaron los duplicados, conservando la primera aparición de cada vehículo.")
        print(f"DataFrame después de eliminar duplicados: {len(df_maestro)} filas.")
    # --- FIN: Verificación y limpieza de duplicados ---

    path = 'Embajadores.xlsx'
    embajadores = pd.read_excel(path)
    print("********----...PROCESO 2: Guardar en Base de datos....-----****************")
    _, end_rfc = fecha_z()
    
    # Convertir la fecha de formato RFC3339 a un formato amigable para SQL Server DATETIME
    dt_object = datetime.fromisoformat(end_rfc.replace('Z', '+00:00'))
    db_friendly_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    gestionar_guardado(df_maestro, db_friendly_date)
    print("********----...PROCESO 3: Procesar y Notificar....-----****************")
    procesar_y_notificar(df_maestro, embajadores)


if __name__ == "__main__":
    """
    Este bloque es para probar el script en un entorno de desarrollo local,
    sin necesidad de subirlo a AWS.
    """
    run()
