import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

def enviar_reporte_por_correo(destinatario, nombre, archivo_adjunto):
    remitente = "eduardo.romero.sinapsis@gmail.com"
    password = "lvatglrsjpxyqqjo" # Tu contraseña de aplicación

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"Reporte Semanal de Seguridad - {datetime.now().strftime('%d/%m/%Y')}"

    # Cuerpo personalizado con el nombre del embajador
    cuerpo = f"""
    Hola {nombre},
    
    Adjunto encontrarás el análisis inteligente de seguridad del Equipo Colaborativo ({archivo_adjunto.replace('Reporte_', '').replace('.csv', '')}) de la última semana.
    
    Saludos cordiales.
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
        print(f"📧 Correo enviado con éxito a {nombre} ({destinatario})")

    except Exception as e:
        print(f"❌ Error al enviar a {nombre}: {e}")

def procesar_y_notificar(df_datos, df_embajadores):
    """
    Filtra el dataset por cada embajador, crea el CSV y envía el correo.
    """
    # Limpiamos nombres de columnas por si acaso
    df_datos.columns = df_datos.columns.str.strip()
    df_embajadores.columns = df_embajadores.columns.str.strip()

    for index, fila in df_embajadores.iterrows():
        nombre = fila['Nombre']
        ec_objetivo = fila['EC']
        correo = fila['Correo']
        
        # Filtrar datos (usamos coincidencia exacta para evitar mezclar EC-01 con EC-010)
        df_filtrado = df_datos[df_datos['EC'] == ec_objetivo]
        
        if not df_filtrado.empty:
            nombre_archivo = f"Reporte_{ec_objetivo}.csv"
            # Guardar archivo temporalmente
            df_filtrado.to_csv(nombre_archivo, index=False)
            
            # Enviar correo
            enviar_reporte_por_correo(correo, nombre, nombre_archivo)
            
            # Opcional: eliminar el archivo después de enviar para no llenar el Drive
            # import os; os.remove(nombre_archivo)
        else:
            print(f"⚠️ No se encontraron datos para {nombre} (EC: {ec_objetivo})")