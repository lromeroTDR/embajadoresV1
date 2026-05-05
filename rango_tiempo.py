
from datetime import datetime, timedelta, timezone


def fecha_milisegundos():
    # 1. Obtener la fecha y hora actual
    hoy = datetime.now()
    
    # 2. Encontrar el inicio de la semana actual (Lunes 00:00:00)
    inicio_semana_actual = hoy.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=hoy.weekday())
    
    # 3. Definir rangos de la semana pasada
    inicio_semana_pasada = inicio_semana_actual - timedelta(days=7)
    fin_semana_pasada = inicio_semana_actual - timedelta(seconds=1)

    # 4. Convertir a milisegundos (Unix Timestamp * 1000)
    start_time_ms = int(inicio_semana_pasada.timestamp() * 1000)
    end_time_ms = int(fin_semana_pasada.timestamp() * 1000)

    # Constante de ajuste (6 horas)
    seis_horas_en_ms = 6 * 60 * 60 * 1000

    # CORRECCIÓN: Usar los nombres de variables correctos
    params_data_ml = {
        "startMs": start_time_ms + seis_horas_en_ms,
        "endMs": end_time_ms + seis_horas_en_ms
    }
    
    print(f"Reporte generado (ms): {params_data_ml}")
    print(f"Rango legible: {inicio_semana_pasada} a {fin_semana_pasada}")
    
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
    lunes_pasado_ajustado = lunes_pasado + timedelta(hours=6)
    domingo_pasado_ajustado = domingo_pasado + timedelta(hours=6)
    # ------------------------------------

    # 6. Formatear a RFC 3339 con 'Z'
    start_time_rfc = lunes_pasado_ajustado.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_rfc = domingo_pasado_ajustado.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Rango capturado (Semana Pasada con -6h):")
    print(f"Inicio: {start_time_rfc}")
    print(f"Fin:    {end_time_rfc}")

    return start_time_rfc, end_time_rfc
