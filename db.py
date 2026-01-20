import logging
import pyodbc
import pandas as pd
# Asumo que estos nombres están en tu config.py
from config import conn_str, BD_TABLE_ACTUAL, BD_TABLE_HISTORICO

def connectdb():
    try:
        conn = pyodbc.connect(conn_str())
        return conn
    except Exception as e:
        logging.error("Error crítico al conectar a la base de datos: %s", e)
        raise

def save_to_database(df: pd.DataFrame, tbl: str, fecha_corte: str) -> int:
    if df.empty:
        logging.warning("El DataFrame está vacío.")
        return 0

    conn = None
    try:
        conn = connectdb()
        cur = conn.cursor()
        cur.fast_executemany = True

        if tbl == BD_TABLE_ACTUAL:
            cur.execute(f"DELETE FROM {tbl}")

        # 1. Definición de INSERT con nombres de columna fijos (ahora ambas tablas son iguales)
        sql = f"""
        INSERT INTO {tbl} (
            [Operador], [Proyecto], [EC], [Vehiculo], [Score], 
            [Total_Km], [Choques], [Somnolencia], [Conduccion_Distraida], 
            [Distancia_Seguimiento], [Colision_Frontal], [Obstruccion_Camara], 
            [Aceleracion_Brusca], [Frenado_Brusco], [Giro_Brusco], 
            [Uso_Celular], [Sin_Cinturon], [Excesos_Velocidad], [Total_General], [Fecha_Corte]
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # 2. Preparación de datos
        registros = df.to_dict(orient='records')
        
        payload = [
            (
                r['Operador'], 
                r['Proyecto'], 
                r['EC'], 
                r['Vehiculo'], 
                r['Score'],
                r['Total Km'], 
                r['Choques'], 
                r['Somnolencia'], 
                r['Conduccion Distraida'],
                r['Distancia Seguimiento'], 
                r['Colision Frontal'], 
                r['Obstruccion Camara'],
                r['Aceleracion Brusca'], 
                r['Frenado Brusco'], 
                r['Giro Brusco'],
                r['Uso Celular'], 
                r['Sin Cinturon'],
                r['Excesos Velocidad'],  
                r['Total General'],
                fecha_corte
            ) 
            for r in registros
        ]

        cur.executemany(sql, payload)
        conn.commit()
        
        logging.info(f"Éxito: {len(payload)} registros en {tbl}.")
        return len(payload)

    except Exception as e:
        logging.error(f"Error al guardar en BD: {e}")
        if conn: conn.rollback()
        raise
    finally:
        if conn: conn.close()


def gestionar_guardado(df: pd.DataFrame, fecha_corte: str):
    """
    Coordina el guardado en la tabla Actual e Histórica.
    Evita duplicados en el histórico usando la fecha de fin de semana.
    """
    # 1. Guardar en la tabla Actual (Siempre se limpia y se inserta)
    print(f"-> Actualizando tabla: {BD_TABLE_ACTUAL}")
    save_to_database(df, BD_TABLE_ACTUAL, fecha_corte)

    # 2. Verificar si ya existe esta semana en el Histórico
    conn = None
    try:
        conn = connectdb()
        cur = conn.cursor()
        
        # Usa Fecha_Corte para la tabla histórica, ahora que ambas tablas son iguales
        query_check = f"SELECT COUNT(*) FROM {BD_TABLE_HISTORICO} WHERE Fecha_Corte = ?"
        cur.execute(query_check, fecha_corte)
        existe = cur.fetchone()[0]

        if existe == 0:
            print(f"-> Insertando nueva semana en histórico: {fecha_corte}")
            save_to_database(df, BD_TABLE_HISTORICO, fecha_corte)
        else:
            print(f"-> Aviso: El histórico para {fecha_corte} ya existe. Omitiendo.")

    except Exception as e:
        logging.error(f"Error al gestionar el guardado: {e}")
    finally:
        if conn: conn.close()
            
