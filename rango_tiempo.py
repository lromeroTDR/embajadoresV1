
import zoneinfo
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


def inicio_semana_anterior():
    try: 
        # Definir zona horaria Mexico
        tz_local = zoneinfo.ZoneInfo("America/Mexico_City")
        # Obtener el ahora reginal
        ahora_local = datetime.now(tz_local)
        # Calcular el lunes a las 00:00:00 De esta semana
        dias_al_lunes = ahora_local.weekday()
        inicio_lunes_local = (ahora_local -timedelta(days=dias_al_lunes) ).replace( hour=0, minute=0, second=0, microsecond=0)
        inicio_lunes_anterior = inicio_lunes_local-timedelta(days=7)
        final_domingo_anterior = inicio_lunes_local - timedelta(seconds=1)
        return inicio_lunes_anterior, final_domingo_anterior
    except zoneinfo.ZoneInfoNotFoundError:
        logger.error("No se encontro la zona horaria Mexico")
        raise    

def fecha_milisegundos():
    try:
        inicio_local, final_local =inicio_semana_anterior()
        # Convertir a UTC 
        inicio_lunes_utc = inicio_local.astimezone(timezone.utc)
        final_domingo_utc = final_local.astimezone(timezone.utc)
        # Convertir a milisegundos 
        start_time_ms = int(inicio_lunes_utc.timestamp() * 1000)
        end_time_ms = int(final_domingo_utc.timestamp() * 1000)
        logger.info(f"Parametros generados: Start={start_time_ms}, End={end_time_ms}")

        params_data_ml = {
        "startMs": start_time_ms ,
        "endMs": end_time_ms 
        }
        return params_data_ml
    
    except Exception as e:
        logger.error(f"Error al generar fechas en milisegundos: {e}")
        raise

def fecha_z(utc = True):
    try:
        inicio_local, final_local =inicio_semana_anterior()
        if utc:
            inicio = inicio_local.astimezone(timezone.utc)
            final = final_local.astimezone(timezone.utc)
        else:
            inicio = inicio_local
            final = final_local
        start_time = inicio.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 
        end_time = final.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 
        if utc:
            start_time += "Z"
            end_time += "Z"
        else:
            start_time += inicio.strftime("%z")
            end_time += final.strftime("%z")
        logger.info("Parametros de fecha generados correctamente")
        return start_time, end_time
    except Exception as e:
        logger.error(f"Error al generar fechas en formato Z: {e}")
        raise