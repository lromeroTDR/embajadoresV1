import pandas as pd
import requests
import time
from config import headers
from rango_tiempo import fecha_milisegundos, fecha_z



# EXTRACCION DE VEHICULOS

def extraer_vehiculos(headers, url_vehiculos):
    """
    Obtiene y limpia la lista de vehículos desde la API de Samsara manejando paginación.
    """
    todos_los_vehiculos = []
    params = {} # Diccionario para manejar el cursor de la página

    try:
        while True:
            # Realizamos la petición incluyendo los params (donde irá el cursor)
            response = requests.get(url_vehiculos, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            vehiculos_list = data.get('data', [])

            if vehiculos_list:
                todos_los_vehiculos.extend(vehiculos_list)

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

        # --- PROCESAMIENTO CON PANDAS (Fuera del bucle) ---
        if todos_los_vehiculos:
            df_vehicles = pd.DataFrame(todos_los_vehiculos)

            # Limpieza y Renombrado
            df_vehicles = df_vehicles.rename(columns={'id': 'vehicleId', 'name': 'vehicleName'})

            print(f" Éxito: Se obtuvieron {len(df_vehicles)} registros totales de vehículos (incluyendo todas las páginas).")
            return df_vehicles
        else:
            print("Advertencia: Lista de vehículos vacía.")
            return pd.DataFrame()

    except requests.exceptions.HTTPError as e:
        print(f" ERROR al obtener vehículos: {e}")
        return pd.DataFrame()
    

def transformacion_vehiculos(df_vehiculos):
    """
    Normaliza las columnas 'tags' y 'staticAssignedDriver' incluyendo el parentTagId.
    """
    # 1. Aseguramos que trabajamos con una copia de las columnas necesarias
    df = df_vehiculos[['vehicleId', 'vehicleName', 'tags', 'staticAssignedDriver']].copy()

    # 2. Normalizar 'staticAssignedDriver' (Diccionario simple)
    df_static_driver = pd.json_normalize(df['staticAssignedDriver']).add_prefix('staticDriver_')

    # 3. Normalizar 'tags' (Extrayendo id, name y parentTagId del primer elemento)
    df['tagId'] = df['tags'].apply(lambda x: x[0].get('id') if isinstance(x, list) and len(x) > 0 else None)
    df['tagName'] = df['tags'].apply(lambda x: x[0].get('name') if isinstance(x, list) and len(x) > 0 else None)
    # NUEVO: Extraer parentTagId
    df['parentTagId'] = df['tags'].apply(lambda x: x[0].get('parentTagId') if isinstance(x, list) and len(x) > 0 else None)

    # 4. Unir todo y limpiar
    df_final = pd.concat([
        df.drop(columns=['tags', 'staticAssignedDriver']).reset_index(drop=True),
        df_static_driver.reset_index(drop=True)
    ], axis=1)

    # 5. Asegurar tipos de datos para futuros merges y limpieza de 'nan' strings
    columnas_id = ['vehicleId', 'staticDriver_id', 'tagId', 'parentTagId']
    for col in columnas_id:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(str).replace(['nan', 'None'], None)

    print(f"Éxito: Vehículos transformados con Parent Tag. Columnas: {df_final.columns.tolist()}")

    return df_final

# EXTRAER SCORE POR VEHICULO

def extraer_score_vehiculo(headers, df_vehiculos, params_score):
    # 1. Obtener lista completa de vehículos

    if df_vehiculos.empty:
        print("No se encontraron vehículos.")
        return None

    lista_puntuaciones = []

    # 2. Iterar sobre cada vehículo obtenido
    print(f"Procesando {len(df_vehiculos)} vehículos...")

    for index, row in df_vehiculos.iterrows():
        v_id = row['vehicleId']
        v_name = row['vehicleName']

        # Reutilizamos tu lógica de petición
        url_score = f"https://api.samsara.com/v1/fleet/vehicles/{v_id}/safety/score"

        try:
            res = requests.get(url_score, headers=headers, params=params_score)
            if res.status_code == 200:
                data_score = res.json()
                # Añadimos el nombre para que el reporte sea legible
                data_score['vehicleName'] = v_name
                lista_puntuaciones.append(data_score)
            else:
                print(f" Error en ID {v_id}: Código {res.status_code}")
        except Exception as e:
            print(f" Error de conexión con ID {v_id}: {e}")

    # 3. Convertir resultados a DataFrame
    return pd.DataFrame(lista_puntuaciones)


# 3. UNIR LOS DATAFRAMES Y MOSTRAR RESULTADOS

def transformar_unir_vehiculos_puntuaciones(df_scores, df_vehiculos):

  print("\n Uniendo los resultados...")

  if not df_scores.empty and not df_vehiculos.empty:
      # Realizar el LEFT JOIN usando 'driverId'
      df_vehiculos['vehicleId'] = df_vehiculos['vehicleId'].astype(str)
      df_scores['vehicleId'] = df_scores['vehicleId'].astype(str)
      if 'vehicleName' in df_scores.columns:
         df_scores = df_scores.drop(columns=['vehicleName'])
      df_final = pd.merge(
          df_vehiculos,
          df_scores,
          on='vehicleId',
          how='left'
      )

      # Opcional: Conversión de unidades para la vista final
      df_final['totalDistanceDrivenKm'] = df_final['totalDistanceDrivenMeters'] / 1000

      # Seleccionar y mostrar las columnas clave
      df_final_view1 = df_final[[
          "vehicleId",
          "vehicleName",
          'safetyScore',
          #'totalHarshEventCount',
          #"harshEvents",
          #"harshBrakingCount",
          "harshAccelCount",
          #"harshTurningCount",
          #"crashCount",
          'totalDistanceDrivenKm',
          'tagId',
          'tagName',
          'parentTagId',
          'staticDriver_id',
          'staticDriver_name'
      ]]

      print("RESULTADO FINAL: Puntuaciones de Conductores Unificadas")

      return df_final_view1

  else:
      print("No se pudo realizar la unión. Uno o ambos DataFrames están vacíos.")


# LISTA DE TODOS LOS EVENTOS DE SEGURIDAD

def extraer_eventos_seguridad(start_time_rfc, end_time_rfc, headers, url):

  # Parámetros iniciales
  params_data_Z = {
      "startTime": start_time_rfc,
      "endTime": end_time_rfc
  }

  all_events = []
  has_next_page = True
  cursor = ""

  print(f"Iniciando descarga desde: {start_time_rfc}")

  # --- Bucle de Paginación ---
  while has_next_page:
      # Si hay un cursor, lo agregamos a los parámetros de la consulta
      if cursor:
          params_data_Z["after"] = cursor

      response = requests.get(url, headers=headers, params=params_data_Z)

      if response.status_code == 200:
          data = response.json()
          events = data.get('data', [])
          all_events.extend(events)

          # Extraer info de paginación de la respuesta
          pagination = data.get('pagination', {})
          has_next_page = pagination.get('hasNextPage', False)
          cursor = pagination.get('endCursor', "")

          print(f"Descargados {len(events)} eventos. Total acumulado: {len(all_events)}")

          # Pausa breve para evitar saturar la API
          if has_next_page:
              time.sleep(0.2)
      else:
          print(f"Error en la petición: {response.status_code}")
          print(response.text)
          break

  # --- Creación del DataFrame ---
  if all_events:
      df_final = pd.DataFrame(all_events)

      return df_final
  else:
      print("\n No se encontraron eventos en el período seleccionado.")

def transformar_eventos_seguridad(df_final_view2):
    # 1. Seleccionamos las columnas necesarias incluyendo vehicle
    df_temp = df_final_view2[[ 'behaviorLabels', 'vehicle']].copy()

    # 2. "Explotamos" la columna behaviorLabels
    df_explotado = df_temp.explode('behaviorLabels')

    # Desanidamos 'driver'
    #df_driver = pd.json_normalize(df_explotado['driver']).add_prefix('driver_')

    # 3. Desanidamos 'behaviorLabels'
    df_labels = pd.json_normalize(df_explotado['behaviorLabels']).add_prefix('behavior_')

    # 4. Desanidamos 'vehicle'
    # Usamos record_prefix para que sea vehicle_id, vehicle_name, etc.
    df_vehicle = pd.json_normalize(df_explotado['vehicle']).add_prefix('vehicle_')

    # 5. Unimos todo en un solo DataFrame limpio
    # Concatenamos eliminando las  columnas originales anidadas
    df_final = pd.concat([
        df_explotado.drop(columns=['behaviorLabels', 'vehicle']).reset_index(drop=True),
        df_vehicle.reset_index(drop=True),
        df_labels.reset_index(drop=True)
    ], axis=1)

    # 6. Creamos la tabla dinámica
    # Ahora puedes incluir 'vehicle_name' en el index si quieres ver qué vehículo traían
    resumen_operadores = df_final.pivot_table(
        index=['vehicle_id', 'vehicle_name'],
        columns='behavior_label', # Nota: Samsara suele usar 'label' en behaviorLabels, no 'name'
        aggfunc='size',
        fill_value=0
    )

    # Añadimos totales y ordenamos
    resumen_operadores['Total_General'] = resumen_operadores.sum(axis=1)
    resumen_operadores = resumen_operadores.sort_values(by='Total_General', ascending=False)

    return resumen_operadores

def unir_vehiculos_eventos_seguridad(df_final_view1, resumen_operadores):
  # 1. Asegúrate de que el resumen de comportamientos no tenga los ID en el índice
  # (si usaste pivot_table, ejecuta esto primero)
  resumen_comportamientos = resumen_operadores.reset_index()

  # 2. Unimos mediante un 'left join' para mantener todos los conductores  aunque no tengan eventos de comportamiento registrados.
  df_maestro = pd.merge(
      df_final_view1,
      resumen_comportamientos,
      left_on='vehicleId',
      right_on='vehicle_id',
      how='left'
  )

  # 3. Limpieza: Eliminamos la columna repetida de ID y llenamos los NaNs con 0
  # (los conductores sin infracciones específicas aparecerán con 0 en lugar de NaN)
  df_maestro = df_maestro.drop(columns=['vehicle_id', 'vehicle_name'])
  df_maestro = df_maestro.fillna(0)

  print(df_maestro.head())

  return df_maestro

# EXCESO DE VELOCIDAD

def extraer_intervalos_velocidad(headers, start_time_rfc, end_time_rfc, df_vehiculos):
    url_speeding = "https://api.samsara.com/speeding-intervals/stream"

    # 1. Obtener todos los IDs únicos de tu DataFrame
    todos_los_ids = df_vehiculos['vehicleId'].astype(str).unique().tolist()
    total_vehiculos = len(todos_los_ids)

    resultados_totales = []

    # 2. Iterar en bloques de 50 IDs (Límite de la API)
    for i in range(0, total_vehiculos, 50):
        bloque_ids = todos_los_ids[i:i + 50]
        ids_string = ",".join(bloque_ids)

        print(f"Procesando bloque {i//50 + 1}: Vehículos del {i} al {min(i+50, total_vehiculos)}...")

        cursor = None  # Para la paginación

        while True:
            # Configurar parámetros del bloque actual
            params = {
                "startTime": start_time_rfc,
                "endTime": end_time_rfc,
                "assetIds": ids_string,
                "includeAsset": "true"
            }
            if cursor:
                params["after"] = cursor

            try:
                res = requests.get(url_speeding, headers=headers, params=params)

                if res.status_code == 200:
                    json_data = res.json()
                    data_raw = json_data.get("data", [])

                    # Filtrar solo viajes que tengan intervalos registrados
                    viajes_con_datos = [v for v in data_raw if v.get('intervals')]

                    if viajes_con_datos:
                        # Aplanar intervalos de esta página
                        df_temp = pd.json_normalize(
                            viajes_con_datos,
                            record_path=['intervals'],
                            meta=['tripStartTime', ['asset', 'id'], ['asset', 'name']],
                            errors='ignore'
                        )
                        resultados_totales.append(df_temp)

                    # Verificar si hay más páginas (paginación)
                    pagination = json_data.get("pagination", {})
                    if pagination.get("hasNextPage"):
                        cursor = pagination.get("endCursor")
                        time.sleep(0.2) # Pausa breve para respetar límites de tasa (rate limiting)
                    else:
                        break # No hay más páginas para este bloque de 50
                else:
                    print(f"Error en bloque {i}: {res.status_code} - {res.text}")
                    break

            except Exception as e:
                print(f"Error de conexión: {e}")
                break

    # 3. Consolidar todos los DataFrames encontrados
    if resultados_totales:
        df_final = pd.concat(resultados_totales, ignore_index=True)
        df_final = df_final.rename(columns={
            'asset.id': 'vehicleId',
            'asset.name': 'vehicleName'
        })
        print(f"¡Hecho! Se encontraron {len(df_final)} registros de exceso de velocidad.")
        return df_final
    else:
        print("No se encontraron registros de exceso de velocidad en ningún vehículo.")
        return pd.DataFrame()
    
# EXTRAER TAGS SAMSARA

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
            return pd.DataFrame()

        # Normalizamos el JSON
        df_tags = pd.json_normalize(data)

        # Seleccionamos y renombramos columnas clave para que sean claras
        # Columnas típicas: id, name, parentTagId
        columnas_interes = {
            'id': 'tagId',
            'name': 'tagName',
            'parentTagId': 'parentTagId'
        }

        # Filtramos solo las columnas que existan en la respuesta
        df_tags = df_tags.rename(columns=columnas_interes)

        # Aseguramos que los IDs sean tratados como objetos/strings
        for col in ['tagId', 'parentTagId']:
            if col in df_tags.columns:
                df_tags[col] = df_tags[col].astype(str).replace('nan', None)

        print(f"Éxito: Se obtuvieron {len(df_tags)} tags.")
        return df_tags

    except requests.exceptions.RequestException as e:
        print(f"ERROR al obtener tags: {e}")
        return pd.DataFrame()

def transformacion_tags(df_tags_final):
    # Usamos errors='ignore' para que no truene si la columna ya fue borrada o no existe
    # Asignamos de nuevo a la variable para que el cambio se mantenga
    df_tags_final = df_tags_final[["parentTag.id", "parentTag.name"]]

    return df_tags_final

def unir_tag_metricas_vehiculo(df_maestro, df_tags):
    """
    Une el nombre del tag padre al DataFrame maestro usando el ID del padre.
    """
    print("\n Agregando nombres de Tags Padres...")

    # 1. Limpieza de la tabla de tags para tener una referencia única de ID -> Nombre
    # Nos quedamos solo con las columnas necesarias y quitamos duplicados
    # Nota: Ajusta 'parentTag.id' y 'parentTag.name' si los nombres varían en tu DF
    df_ref_tags = df_tags[['parentTag.id', 'parentTag.name']].drop_duplicates()

    # 2. Aseguramos que los IDs sean del mismo tipo (String) para evitar fallos
    df_maestro['parentTagId'] = df_maestro['parentTagId'].astype(str)
    df_ref_tags['parentTag.id'] = df_ref_tags['parentTag.id'].astype(str)

    # 3. Realizamos la unión (Merge)
    # left_on: columna en df_maestro
    # right_on: columna en la tabla de referencia
    df_unificado = pd.merge(
        df_maestro,
        df_ref_tags,
        left_on='parentTagId',
        right_on='parentTag.id',
        how='left'
    )

    # 4. Limpieza final: Renombramos la columna nueva y eliminamos el ID repetido
    df_unificado = df_unificado.rename(columns={'parentTag.name': 'nameParent'})

    # Eliminamos la columna de ID que viene de la tabla de tags para no tener duplicados
    if 'parentTag.id' in df_unificado.columns:
        df_unificado = df_unificado.drop(columns=['parentTag.id'])

    print(f" Éxito: Columna 'nameParent' agregada correctamente.")

    return df_unificado

def ordenar_puntuaciones(df_maestro):
  # Usamos ascending=False para que los que tienen MÁS eventos salgan primero
  df_maestro = df_maestro.sort_values(by='safetyScore', ascending=False)
  return df_maestro

  print(f"Éxito: Se generó el reporte con {len(df_maestro)} conductores, ordenados por mayor impacto.")


def filtracion_columnas(df_maestro):
  columnas = ['vehicleName',
              'tagName',
              "nameParent",
              'staticDriver_name',
              'safetyScore',
              'totalDistanceDrivenKm',
              'crash',
              'drowsy',
              'genericDistraction',
               'followingDistance',
              'forwardCollisionWarning',
              'obstructedCamera',
              'harshAccelCount',
              'braking',
              'harshTurn',
              'mobileUsage',
              'noSeatbelt',
              'Total_General']
  return df_maestro[columnas].copy()

def cambio_idioma(df):
    # Diccionario de mapeo (Inglés: Español)
    columnas_espanol = {
    "vehicleName": "Vehiculo",
    'tagName': "Proyecto",
    'nameParent': "EC",
    'staticDriver_name': 'Conductor',
    'safetyScore': 'Puntuacion Seguridad',
    'totalDistanceDrivenKm': 'Total Km',
    'crash': 'Choques',
    'drowsy': 'Somnolencia',
    'genericDistraction': "Conduccion Distraida",
    'followingDistance': 'Distancia Seguimiento',
    'forwardCollisionWarning': 'Colision Frontal',
    'obstructedCamera': 'Obstruccion Camara',
    'harshAccelCount': 'Aceleracion Brusca',
    'braking': 'Frenado Brusco',
    'harshTurn': 'Giro Brusco',
    'mobileUsage': 'Uso Celular',
    'noSeatbelt': 'Sin Cinturon',
    'Total_General': 'Total General',
  }
# Aplicar el cambio al DataFrame
    df.rename(columns=columnas_espanol, inplace=True)

  # Verificar los nombres
    print(df.columns)


def pipeline():
  print("\n Iniciando Fechas")
  params_data_ml= fecha_milisegundos()
  start_time_rfc, end_time_rfc = fecha_z()
  print("==========================================================")
  print("\n 1.- Obteniendo metadatos de conductores (Nombres, IDs)...")
  url_metadata = "https://api.samsara.com/fleet/vehicles"
  df_meta1= extraer_vehiculos(url_vehiculos=url_metadata,headers=headers)
  print("==========================================================")
  print("\n 1.1.- Transfomando DF Vehiculos")
  df_meta1= transformacion_vehiculos( df_meta1)
  print("==========================================================")
  print("\n 2.- Obteniendo las puntuaciones de los conductores")
  df_meta2 = extraer_score_vehiculo(df_vehiculos=df_meta1, params_score=params_data_ml,headers=headers)
  print("==========================================================")
  print("\n 3.- Uniendo df Operadores con Df puntuaciones")
  df_meta3 = transformar_unir_vehiculos_puntuaciones(df_scores=df_meta2, df_vehiculos=df_meta1)
  print("\n 4.- Obteniendo eventos de seguridad")
  print("==========================================================")
  url_eventos = "https://api.samsara.com/fleet/safety-events"
  df_meta4 = extraer_eventos_seguridad(end_time_rfc=end_time_rfc, start_time_rfc=start_time_rfc, headers=headers, url=url_eventos)
  print("==========================================================")
  print("\n 4.1.- Transformar datos anidados de la lista de eventos de seguridad")
  df_meta4= transformar_eventos_seguridad(df_final_view2=df_meta4)
  print("==========================================================")
  print("\n 5.- Uniendo puntuaciones con eventos de seguridad")
  df_meta5= unir_vehiculos_eventos_seguridad(df_final_view1=df_meta3, resumen_operadores=df_meta4)
  print("==========================================================")
  print("\n 6.- Extraer Tags")
  df_meta6= extraer_tags_samsara(headers=headers)
  print("==========================================================")
  print("\n 6.1.- Extraer Tags")
  df_meta6= transformacion_tags(df_tags_final=df_meta6)
  df_meta7 = unir_tag_metricas_vehiculo(df_maestro=df_meta5, df_tags= df_meta6)
  print("==========================================================")
  print("\n A.- Ordenar Puntuaciones")
  a = ordenar_puntuaciones(df_maestro=df_meta7)
  print("\n B.- Filtrar columnas reglas de negocio")
  b= filtracion_columnas(df_maestro=a)
  print("\n C.- Cambiar el idioma")
  cambio_idioma(df=b)

  return b