import time
from datetime import datetime, timedelta, timezone


# --- FECHAS ---

# --- RANGO DE TIEMPO (Últimos 7 días como ejemplo) En milisegundos
def fecha_milisegundos():
  end_time_ms = int(time.time() * 1000)
  seven_days_ms = 7 * 24 * 60 * 60 * 1000
  start_time_ms = end_time_ms - seven_days_ms

  # Parámetros para la API de Puntuaciones
  params_data_ml = {
    "startMs": start_time_ms,
    "endMs": end_time_ms
    }
  return params_data_ml
  print(f"Rango de tiempo de la consulta: {datetime.fromtimestamp(start_time_ms / 1000).strftime('%Y-%m-%d')} a {datetime.fromtimestamp(end_time_ms / 1000).strftime('%Y-%m-%d')}")


# --- RANGO DE TIEMPO (Últimos 7 días como ejemplo) En Formato Z
def fecha_z():
  # Tiempo actual con zona horaria UTC
  now = datetime.now(timezone.utc)

  # Calcular la hora de inicio (hace 7 días)
  start_time = now - timedelta(days=7)

  # Formatear a RFC 3339 (el formato que pide la imagen con la 'Z' al final)
  # .isoformat() genera el estándar, reemplazamos el desfase por 'Z'
  start_time_rfc = start_time.isoformat().replace("+00:00", "Z")
  end_time_rfc = now.isoformat().replace("+00:00", "Z")

  # Definimos los nuevos parámetros de consulta para la URL

  return start_time_rfc, end_time_rfc
  print(f"Inicio: {startTime}")
  print(f"Fin:    {endTime}")