import pandas as pd
import os
from dotenv import load_dotenv
from db import gestionar_guardado, save_to_database
from rango_tiempo import fecha_z
from datetime import datetime

def test_delete_functionality():
    """
    Prueba específicamente si el comando DELETE FROM se está ejecutando correctamente
    en la tabla de datos actuales.
    """
    print("--- Iniciando prueba de la funcionalidad DELETE ---")

    # 1. Cargar configuración de la BD
    print("Cargando configuración de la base de datos...")
    load_dotenv()
    db_actual_table = os.getenv("BD_TABLE_ACTUAL")
    if not db_actual_table:
        print("\nERROR: No se encontró la variable de entorno BD_TABLE_ACTUAL.")
        return

    # 2. Crear datos de prueba con un ID único
    print("Creando DataFrame de prueba con ID único...")
    test_vehicle_id = 'VEHICULO_TEST_DELETE'
    data = {
        'Vehiculo': [test_vehicle_id], 'Proyecto': ['TEST_PROJ'], 'EC': ['EC-TEST-DEL'],
        'Conductor': ['TEST_DRIVER'], 'Puntuacion Seguridad': [100], 'Total Km': [10],
        'Choques': [0], 'Somnolencia': [0], 'Conduccion Distraida': [0],
        'Distancia Seguimiento': [0], 'Colision Frontal': [0], 'Obstruccion Camara': [0],
        'Aceleracion Brusca': [0], 'Frenado Brusco': [0], 'Giro Brusco': [0],
        'Uso Celular': [0], 'Sin Cinturon': [0], 'Excesos Velocidad': [0],
        'Total General': [0]
    }
    dummy_df = pd.DataFrame(data)

    # 3. Obtener y formatear fecha
    _, end_rfc = fecha_z()
    dt_object = datetime.fromisoformat(end_rfc.replace('Z', '+00:00'))
    db_friendly_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Usando fecha: {db_friendly_date}")

    # --- PRIMERA EJECUCIÓN ---
    print("\n--- PASO 1: Primer guardado ---")
    print("Se intentará insertar el registro de prueba por primera vez...")
    try:
        gestionar_guardado(dummy_df, db_friendly_date)
        print("✅ PRIMER GUARDADO EXITOSO: El registro de prueba debería estar en la tabla.")
    except Exception as e:
        print(f"❌ ERROR INESPERADO EN EL PRIMER GUARDADO: La prueba no puede continuar. Error: {e}")
        return

    # --- SEGUNDA EJECUCIÓN ---
    print("\n--- PASO 2: Segundo guardado (La prueba real del DELETE) ---")
    print("Se intentará insertar el MISMO registro por segunda vez.")
    print("Si DELETE funciona, la tabla se vaciará y este paso será exitoso.")
    print("Si DELETE falla, ocurrirá un error de 'PRIMARY KEY constraint'...")
    try:
        gestionar_guardado(dummy_df, db_friendly_date)
        print("\n*********************************************************************")
        print("✅ PRUEBA EXITOSA: La funcionalidad de DELETE funciona correctamente.")
        print("El segundo guardado se completó sin errores de clave duplicada,")
        print("lo que confirma que la tabla fue vaciada antes de la inserción.")
        print("\nEsto significa que el error original es causado por DATOS DUPLICADOS")
        print("que vienen del 'pipeline' en el script principal 'main.py'.")
        print("*********************************************************************")

    except Exception as e:
        print("\n*******************************************************************")
        print("❌ PRUEBA FALLIDA: Ocurrió un error en el segundo guardado.")
        print("Esto confirma que el comando 'DELETE FROM' NO está funcionando")
        print("como se esperaba, probablemente por un problema de permisos.")
        print(f"Error detallado: {e}")
        print("*******************************************************************")

if __name__ == "__main__":
    test_delete_functionality()