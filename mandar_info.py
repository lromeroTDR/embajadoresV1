import pandas as pd
import smtplib
import requests
import os
from config import token_mail, api_reglas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


def enviar_reporte_por_correo(destinatario, nombre, archivo_adjunto):
    remitente = "eduardo.romero.sinapsis@gmail.com"
    password = token_mail 

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"Reporte Semanal de Seguridad - {datetime.now().strftime('%d/%m/%Y')}"

    # Cuerpo personalizado con el nombre del embajador
    cuerpo = f"""
    Hola {nombre},
    
    Adjunto encontrarás la tabla de Habitos de Manejo  del Equipo Colaborativo ({os.path.basename(archivo_adjunto).replace('Reporte_', '').replace('.xlsx', '')}) de la última semana.
    

    Para cualquier aclaracion, favor de contactarse al correo lromero@bgcapitalgroup.mx.
    Esta es una automatizacion, no se generaran respuestas.

    Saludos cordiales.

    Ing. Analista de Base de Datos.
    """
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        with open(archivo_adjunto, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {archivo_adjunto}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        print(f" Correo enviado con éxito a {nombre} ({destinatario})")

    except Exception as e:
        print(f"Error al enviar a {nombre}: {e}")

def aplicar_colores(valor):
    if valor >= 70:
        color = 'background-color: #2ecc71; color: white'  # Verde
    elif 40 <= valor < 70:
        color = 'background-color: #f1c40f; color: black'  # Amarillo
    else:
        color = 'background-color: #e74c3c; color: white'  # Rojo
    return color

def obtener_reglas():
    # 1. Configuración del endpoint
    url_reglas = api_reglas
    try:
        # 2. Consumir la API
        response = requests.get(url_reglas)
        response.raise_for_status()  # Verifica si hubo errores en la petición
        # 3. Convertir JSON a una lista de diccionarios
        datos = response.json()
        # 4. Crear el DataFrame de Pandas
        df = pd.DataFrame(datos)
        # Mostrar los primeros resultados
        print("Datos cargados exitosamente:")
        print(df.head())
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return pd.DataFrame()
    

def procesar_y_notificar(df_datos):
    """
    Filtra el dataset por cada embajador, crea el CSV y envía el correo.
    """

    df_embajadores=obtener_reglas()
    
    # Limpiamos nombres de columnas por si acaso
    df_datos.columns = df_datos.columns.str.strip()
    df_embajadores.columns = df_embajadores.columns.str.strip()

    if not os.path.exists('Datos'):
        os.makedirs('Datos')

    for _, fila in df_embajadores.iterrows():
        nombre = fila['Nombre']
        ec_objetivo = fila['EC']
        correo = fila['Correo']
        km = float(fila["km"])
        score = float(fila["score"])
        # Filtrar datos (usamos coincidencia exacta para evitar mezclar EC-01 con EC-010)
        df_filtrado = df_datos[
            (df_datos['EC'] == ec_objetivo) & 
            (df_datos["Total Km"] >= km) & 
            (df_datos["Score"] <= score)
        ].copy()
        
        columnas_a_quitar = ['EC']
        df_filtrado = df_filtrado.drop(columns=columnas_a_quitar)
 
        if not df_filtrado.empty:
            # 1. Definir el nombre con extensión .xlsx
            nombre_archivo = f"Datos/Reporte_{ec_objetivo}.xlsx"
            # 2. Aplicar los colores antes de guardar
            df_filtrado = df_filtrado.style.map(aplicar_colores, subset=['Score'])
            # 3. Guardar como Excel usando el motor openpyxl
            df_filtrado.to_excel(nombre_archivo, index=False, engine='openpyxl')
            # Enviar correo
            enviar_reporte_por_correo(correo, nombre, nombre_archivo)
            if os.path.exists(nombre_archivo):
                os.remove(nombre_archivo)
                print(f"Archivo temporal {nombre_archivo} eliminado.")
        else:
            print(f"No se encontraron datos para {nombre} (EC: {ec_objetivo})")


