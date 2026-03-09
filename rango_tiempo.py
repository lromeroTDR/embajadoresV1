
from datetime import datetime, timedelta, timezone


def fecha_milisegundos():
    # 1. Obtener la fecha y hora actual (hoy)
    hoy = datetime.now()
    
    # 2. Encontrar el inicio de la semana actual (Lunes a las 00:00:00)
    # hoy.weekday() devuelve 0 para Lunes, 1 para Martes, etc.
    inicio_semana_actual = hoy.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=hoy.weekday())
    
    # 3. El Domingo pasado es un segundo antes del inicio de esta semana (o simplemente el día anterior)
 
    fin_semana_pasada = inicio_semana_actual - timedelta(seconds=1)
    
    # 4. El Lunes de la semana pasada es 7 días antes del inicio de esta semana
    inicio_semana_pasada = inicio_semana_actual - timedelta(days=7)

    # Convertir a milisegundos para la API
    start_time_ms = int(inicio_semana_pasada.timestamp() * 1000)
    end_time_ms = int(fin_semana_pasada.timestamp() * 1000)

    seis_horas_en_ms = 6 * 60 * 60 * 1000

    params_data_ml = {
        "startMs": start_ms - seis_horas_en_ms,
        "endMs": end_ms - seis_horas_en_ms
    }
    
    # Imprimir el rango para verificar (Movido antes del return para que se ejecute)
    print(f"Reporte generado: {inicio_semana_pasada.strftime('%Y-%m-%d %H:%M:%S')} a {fin_semana_pasada.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return params_data_ml


def fecha_z():
    # 1. Obtener la fecha actual en UTC
    ahora = datetime.now(timezone.utc)
    
    # 2. Ir al inicio del día de hoy (00:00:00)
    hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 3. Encontrar el lunes de la semana actual
    lunes_semana_actual = hoy_inicio - timedelta(days=ahora.weekday())
    
    # 4. Calcular Lunes de la semana pasada (Inicio)
    # 5. Calcular Domingo de la semana pasada (Fin)
    lunes_pasado = lunes_semana_actual - timedelta(days=7)
    domingo_pasado = lunes_semana_actual - timedelta(seconds=1)

    # --- NUEVA LÓGICA: Restar 6 horas ---
    lunes_pasado_ajustado = lunes_pasado - timedelta(hours=6)
    domingo_pasado_ajustado = domingo_pasado - timedelta(hours=6)
    # ------------------------------------

    # 6. Formatear a RFC 3339 con 'Z'
    start_time_rfc = lunes_pasado_ajustado.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_rfc = domingo_pasado_ajustado.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Rango capturado (Semana Pasada con -6h):")
    print(f"Inicio: {start_time_rfc}")
    print(f"Fin:    {end_time_rfc}")

    return start_time_rfc, end_time_rfc
