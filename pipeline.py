import pandas as pd
import requests
import time
from config import headers
from rango_tiempo import fecha_milisegundos, fecha_z


#######################################
# EXTRACCION DE OPERADORES
def extraer_operadores(headers, url_operadores):
    """
    Obtiene y limpia la lista de operadores desde la API de Samsara manejando paginación.
    """
    todos_los_operadores = []
    params = {} # Diccionario para manejar el cursor de la página

    try:
        while True:
            # Realizamos la petición incluyendo los params (donde irá el cursor)
            response = requests.get(url_operadores, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            operadores_list = data.get('data', [])

            if operadores_list:
                todos_los_operadores.extend(operadores_list)

            # --- LÓGICA DE PAGINACIÓN ---
            pagination = data.get('pagination', {})
            has_next_page = pagination.get('hasNextPage', False)
            end_cursor = pagination.get('endCursor', '')

            if has_next_page and end_cursor:
                # Actualizamos el parámetro 'after' para la siguiente iteración
                params['after'] = end_cursor
            else:
                # Si no hay más páginas, rompemos el bucle
                break

        # --- PROCESAMIENTO CON PANDAS 
        if todos_los_operadores:
            df_drivers = pd.DataFrame(todos_los_operadores)

            print(f" Éxito: Se obtuvieron {len(df_drivers)} registros totales de operadores (incluyendo todas las páginas).")
            return df_drivers
        else:
            print("Advertencia: Lista de operadores esta vacía.")
            return pd.DataFrame()

    except requests.exceptions.HTTPError as e:
        print(f" ERROR al obtener Operadores: {e}")
        return pd.DataFrame()

def transformacion_operadores(df_operadores):
    """
    Normaliza las columnas 'tags' y 'staticAssignedVehicle' incluyendo el parentTagId.
    """
    # Limpieza y Renombrado
    df_operadores = df_operadores.rename(columns={'id': 'driverId', 'name': 'driverName'})
    df_operadores= df_operadores[df_operadores['driverActivationStatus']=="active"]
    # 1. Aseguramos que trabajamos con una copia de las columnas necesarias
    df = df_operadores[['driverId', 'driverName', 'tags']].copy()
    # 3. Normalizar 'tags' (Extrayendo id, name y parentTagId del primer elemento)
    df['tagId'] = df['tags'].apply(lambda x: x[0].get('id') if isinstance(x, list) and len(x) > 0 else None)
    df['tagName'] = df['tags'].apply(lambda x: x[0].get('name') if isinstance(x, list) and len(x) > 0 else None)
    # Extraer parentTagId
    df['parentTagId'] = df['tags'].apply(lambda x: x[0].get('parentTagId') if isinstance(x, list) and len(x) > 0 else None)
    # 4. Unir todo y limpiar
    df_final = df.drop(columns=['tags']).reset_index(drop=True)
   
    return df_final


def extraer_tags_samsara(headers):
    """
    Obtiene la lista de tags de la organización y la devuelve como un DataFrame.
    """
    url = "https://api.samsara.com/tags"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json().get('data', [])

        if not data:
            print("Advertencia: No se encontraron tags.")
            raise ValueError("No se encontraron tags.")

        print(f"Éxito: Se obtuvieron {len(data)} tags.")
        return data

    except requests.exceptions.RequestException as e:
        print(f"ERROR al obtener tags: {e}")
        raise

def transformacion_tags(data):
    # 1. Normalizamos el JSON (aquí se creará la columna 'parentTag.name')
    df_tags = pd.json_normalize(data)
  
    # 2. Mapeamos las columnas clave, incluyendo la del objeto anidado
    columnas_interes = {
        'id': 'tagId',
        'name': 'tagName',
        'parentTagId': 'parentTagId',
        'parentTag.name': 'parentTagName'  
    }
    
    # 3. Renombramos las columnas
    df_tags = df_tags.rename(columns=columnas_interes)

    # 4. Aseguramos que los IDs sean tratados como objetos/strings
    for col in ['tagId', 'parentTagId']:
        if col in df_tags.columns:
            df_tags[col] = df_tags[col].astype(str).replace('nan', None)

  
    columnas_a_filtrar = ["parentTagId", "parentTagName"]
    # Usamos esto por si algún registro no trae la columna en la API
    df_tags_final = df_tags[[col for col in columnas_a_filtrar if col in df_tags.columns]].copy()

    # 6. Aplicamos tu filtro por Equipos Colaborativos
    filtro_ec = ["EC-01", "EC-02", "EC-03", "EC-05", "EC-08", "EC-10"]
    if "parentTagName" in df_tags_final.columns:
        df_tags_final = df_tags_final[df_tags_final["parentTagName"].isin(filtro_ec)]

    df_tags_final= df_tags_final.drop_duplicates(subset=['parentTagId']).reset_index(drop=True)

    return df_tags_final

def extraer_score_operadores(headers, url_operadores, start, end):
    """
    Obtiene y limpia la lista de operadores desde la API de Samsara manejando paginación.
    """
    todos_los_operadores = []
    params  = {
      "startTime": start,
      "endTime": end
    }
    try:
        while True:
            # Realizamos la petición incluyendo los params (donde irá el cursor)
            response = requests.get(url_operadores, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            operadores_list = data.get('data', [])

            if operadores_list:
                todos_los_operadores.extend(operadores_list)

            # --- LÓGICA DE PAGINACIÓN ---
            pagination = data.get('pagination', {})
            has_next_page = pagination.get('hasNextPage', False)
            end_cursor = pagination.get('endCursor', '')

            if has_next_page and end_cursor:
                # Actualizamos el parámetro 'after' para la siguiente iteración
                params['after'] = end_cursor
            else:
                # Si no hay más páginas, rompemos el bucle
                break

        # --- PROCESAMIENTO CON PANDAS 
        if todos_los_operadores:
            df_drivers = pd.DataFrame(todos_los_operadores)

            print(f" Éxito: Se obtuvieron {len(df_drivers)} registros totales de operadores (incluyendo todas las páginas).")
            return df_drivers
        else:
            print("Advertencia: Lista de operadores esta vacía.")
            return pd.DataFrame()

    except requests.exceptions.HTTPError as e:
        print(f" ERROR al obtener Operadores: {e}")
        return pd.DataFrame()

def transformar_eventos(scores):
    def extraer_impacto_max_speed(lista_speeding):
        """ Filtra la lista buscando 'maxSpeed' y extrae su 'scoreImpact' """
        if not isinstance(lista_speeding, list):
            return 0
        for registro in lista_speeding:
            if isinstance(registro, dict) and registro.get('speedingType') == 'maxSpeed':
                return registro.get('scoreImpact', 0)
        return 0
    df_explotado = scores.explode('behaviors')
  # Convertimos los diccionarios de 'behaviors' en columnas reales
    df_comportamientos = pd.json_normalize(df_explotado['behaviors'].dropna())

  # Reasignamos el driverId correspondiente para no perder la relación
    df_comportamientos['driverId'] = df_explotado.dropna(subset=['behaviors'])['driverId'].values
  # Pivotamos para que cada 'behaviorType' sea una columna y su valor sea el 'count'
    df_habitos_columnas = df_comportamientos.pivot(
        index='driverId', 
        columns='behaviorType', 
        values='count'
    ).reset_index()
  # Rellenamos con 0 los hábitos que el conductor NO cometió
    df_habitos_columnas = df_habitos_columnas.fillna(0)
  # --- Paso B: Unificar todo y procesar 'speeding' ---
  # Unimos las nuevas columnas de hábitos de regreso al DataFrame original (eliminando la columna anidada vieja)
    df_final = pd.merge(
        scores.drop(columns=['behaviors']), 
        df_habitos_columnas, 
        on='driverId', 
        how='left'
    ).fillna(0)
  # Extraemos el impacto de 'maxSpeed' usando la función auxiliar y creamos la columna requerida
    df_final['impSpeed'] = scores['speeding'].apply(extraer_impacto_max_speed)
  # Eliminamos la columna original de speeding que ya no se necesita
    df_final = df_final.drop(columns=['speeding'], errors='ignore')
  
    df_final['Horas Conducidas'] = (df_final['driveTimeMilliseconds'] / 3600000).round(3)
    # 2. Si tu columna de metros se llamaba diferente antes de ser 'Total Km' (ej. 'driveDistanceMeters')
    df_final['Total Km'] = (df_final['driveDistanceMeters'] / 1000).round(3)
    # Eliminamos ambas columnas viejas a la vez
    columnas_a_eliminar = ['driveTimeMilliseconds', 'driveDistanceMeters']

    df_final = df_final.drop(columns=columnas_a_eliminar, errors='ignore')
    return df_final

def integrar_operadores_etiquetas_y_telemetria(df_operadores, df_tags_padre, df_comportamientos):
    """
    Realiza la unión secuencial (Left Joins) manteniendo el 100% de la relación 
    operadores-etiquetas y rellenando con 0 a los conductores sin telemetría.
    """
    # 1. Copias de seguridad para no modificar los DataFrames originales fuera de la función
    op = df_operadores.copy()
    tags = df_tags_padre.copy()
    comp = df_comportamientos.copy()
    
    # 2. Homogeneizar tipos de datos a string para evitar fallas en los joins
    for dataframe in [op, tags]:
        if 'parentTagId' in dataframe.columns:
            dataframe['parentTagId'] = dataframe['parentTagId'].astype(str).str.strip()
            
    op['driverId'] = op['driverId'].astype(str).str.strip()
    comp['driverId'] = comp['driverId'].astype(str).str.strip()
    
    # 3. Limpiar el catálogo de tags padre para evitar que se dupliquen operadores
    # (Resuelve el problema de filas repetidas en el catálogo de ECs)
    if 'parentTagId' in tags.columns:
        tags = tags.drop_duplicates(subset=['parentTagId'])
    
    # 4. PRIMER LEFT JOIN: Operadores + Nombre de su Equipo Colaborativo (parentTagName)
    df_operadores_etiquetados = pd.merge(
        tags,
        op,
        on='parentTagId',
        how='left'
    )
    
    # 5. SEGUNDO LEFT JOIN: El resultado anterior + Sus comportamientos de manejo
    df_master_final = pd.merge(
        df_operadores_etiquetados,
        comp,
        on='driverId',
        how='left'
    )
    
    # 6. Identificar columnas numéricas de telemetría para rellenar sus vacíos con 0
    # Esto asegura que si un operador no tiene viajes, sus métricas no queden como NaN
    columnas_a_poner_cero = [
        'driverScore', 'driveDistanceMeters', 'driveTimeMilliseconds', 
        'braking', 'crash', 'defensiveDriving', 'distractedDrivingAutomatic',
        'Impacto de velocidad'  # Por si ya habías procesado los excesos de velocidad
    ]
    
    for col in columnas_a_poner_cero:
        if col in df_master_final.columns:
            df_master_final[col] = df_master_final[col].fillna(0)
            
    # 7. Resetear el índice para entregar un DataFrame completamente limpio
    return df_master_final.reset_index(drop=True)


######################################

def ordenar_puntuaciones(df_maestro):
  # Usamos ascending=False para que los que tienen MÁS eventos salgan primero
  df_maestro = df_maestro.sort_values(by='driverScore', ascending=False)

  print(f"Éxito: Se generó el reporte con {len(df_maestro)} conductores, ordenados por mayor impacto.")
 
  return df_maestro

def filtracion_columnas(df_maestro):
    # 1. Tu lista de columnas deseadas (se queda igual)
    columnas = [
        'driverName', 'tagName', "parentTagName", 
        'driverScore', 'Total Km', "Horas Conducidas", 'driveTimeMilliseconds','crash', 'drowsy',
        'distractedDrivingAutomatic', 'followingDistance', 'forwardCollisionWarning',
        'obstructedCamera', 'harshAccelCount', 'braking', 'harshTurn', 'defensiveDriving',
        'mobileUsage', 'noSeatbelt',"impSpeed" 
    ]

    # 2. Reindex: busca las columnas. Si no existen, las crea y pone 0 (fill_value=0)
    # Esto evita el KeyError y garantiza que el orden sea siempre el mismo
    df_filtrado = df_maestro.reindex(columns=columnas, fill_value=0)

    return df_filtrado.copy()

def cambio_idioma(df):
    # Diccionario de mapeo (Inglés: Español)
    columnas_espanol = {
    "driverName": "Operador",
    'tagName': "Proyecto",
    'parentTagName': "EC",
    'driverScore': 'Score',
    'crash': 'Choques',
    'drowsy': 'Somnolencia',
    'distractedDrivingAutomatic': "Conduccion Distraida",
    'followingDistance': 'Distancia Seguimiento',
    'forwardCollisionWarning': 'Colision Frontal',
    'obstructedCamera': 'Obstruccion Camara',
    'harshAccelCount': 'Aceleracion Brusca',
    'braking': 'Frenado Brusco',
    'harshTurn': 'Giro Brusco',
    'defensiveDriving': 'Conduccion Defensiva',
    'mobileUsage': 'Uso Celular',
    'noSeatbelt': 'Sin Cinturon',
    "impSpeed": "Excesos Velocidad",
  }
    # Aplicar el cambio al DataFrame
    df.rename(columns=columnas_espanol, inplace=True)
    # Verificar los nombres
    print(df.columns)

def validar_tipo_datos(df):
    """
    Convierte los float64 a int para que SQL Server los acepte en columnas INT.
    """
    # 1. Columnas que SQL Server tiene como INT (y que en tu info salían como float64)
    cols_a_entero = [
        'Score', 'Aceleracion Brusca', 'Frenado Brusco',
        'Choques', 'Somnolencia', 'Distancia Seguimiento',
        'Colision Frontal', 'Conduccion Distraida', 'Giro Brusco',
        'Uso Celular', 'Sin Cinturon', 'Obstruccion Camara',"Excesos Velocidad"
    ]

    for col in cols_a_entero:
        if col in df.columns:
            # fillna(0) es obligatorio para poder convertir a int
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 2. Kilómetros: Es float64, lo dejamos con decimales pero REDONDEADO a 3
    if 'Total Km' in df.columns:
        df['Total Km'] = pd.to_numeric(df['Total Km'], errors='coerce').fillna(0).round(3)

    # 3. Limpieza de strings (para evitar errores con nulos en EC/nameParent)
    cols_texto = ['Operador', 'Proyecto', 'EC', 'Vehiculo']
    for col in cols_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).replace(['nan', 'None'], 'N/A')

    # Correccion de duplicados

    if df['Operador'].duplicated().any():
        print("\n¡ADVERTENCIA! Se encontraron operadores duplicados en los datos procesados.")
        print("Filas duplicadas (incluyendo todas las ocurrencias):")
        # Muestra todas las filas que tienen valores duplicados en la columna 'Vehiculo'
        print(df[df['Operador'].duplicated(keep=False)].sort_values('Operador'))

        # Elimina los duplicados, conservando solo la primera aparición
        df.drop_duplicates(subset=['Operador'], keep='first', inplace=True)
        print("\nSe eliminaron los duplicados, conservando la primera aparición de cada vehículo.")
        print(f"DataFrame después de eliminar duplicados: {len(df)} filas.")


    print("\n", df.info())

    return df

def guardar_reporte(fecha, reporte):
    if not reporte.empty:
            nombre_archivo = f"Datos/Reporte_{fecha.replace(':', '-')}.csv"
            # Guardar archivo temporalmente
            reporte.to_csv(nombre_archivo, index=False)
            print(f"Reporte Guardado Correctamente. Nombre: {nombre_archivo}")
    else:
            print("No Se guardo el archivo")

def pipeline():

    print("\n Iniciando Fechas")
    params_data_ml= fecha_milisegundos()
    start_time_rfc, end_time_rfc = fecha_z()
    print("==========================================================")
    print("\n Obteniendo metadatos de conductores (Nombres, IDs)...")
    url_metadata ="https://api.samsara.com/fleet/drivers"
    df_meta1= extraer_operadores(url_operadores=url_metadata,headers=headers)
    print("\n 1.1.- Transfomando DF Vehiculos")
    o= transformacion_operadores( df_meta1)
    print("==========================================================")
    print("\n Extraer Tags")
    tags= extraer_tags_samsara(headers=headers)
    t= transformacion_tags(tags)
    print("==========================================================")
    print("\n Obteniendo Metricas Conductores...")
    url_metadata ="https://api.samsara.com/safety-scores/drivers"
    scores = extraer_score_operadores(url_operadores=url_metadata,headers=headers,start=start_time_rfc, end= end_time_rfc)
    eventos = transformar_eventos(scores)
    final = integrar_operadores_etiquetas_y_telemetria(o, t, eventos)
    print("==========================================================")
    print("\n A.- Ordenar Puntuaciones")
    a = ordenar_puntuaciones(df_maestro=final)
    print("\n B.- Filtrar columnas reglas de negocio")
    b= filtracion_columnas(df_maestro=a)
    print("\n C.- Cambiar el idioma")
    cambio_idioma(df=b)
    print("\n D.- Validacion de datos")
    d= validar_tipo_datos(df=b)
    print("\n E.- Guardar Reporte")
    guardar_reporte(fecha=end_time_rfc,reporte=d)
    print("\n PIPELINE TERMINADO")

    return d
