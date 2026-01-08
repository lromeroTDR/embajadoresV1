### Diagrama de Flujo del Proceso

```
( Inicio )
     |
     v
[ main.py: Inicia la ejecución ]
     |
     v
[ Llama a la función pipeline.run() para construir el reporte principal ]
     |
     +-----> [ pipeline.py ]
     |         |
     |         v
     |       [ 1. Lee las fechas desde rango_tiempo.py ]
     |         |
     |         v
     |       [ 2. Lee las credenciales de la API desde config.py ]
     |         |
     |         v
     |       [ 3. Obtiene datos de la API de Samsara (vehículos, eventos, etc.) ]
     |         |
     |         v
     |       [ 4. Procesa y unifica los datos en un DataFrame de pandas ]
     |         |
     |         v
     |       < Retorna el DataFrame Maestro >
     |
     v
[ main.py: Recibe el DataFrame Maestro ]
     |
     v
[ Lee el archivo <Embajadores.xlsx> para obtener la lista de destinatarios ]
     |
     v
[ Llama a mandar_email.procesar_y_notificar() con el DataFrame y la lista ]
     |
     +-----> [ mandar_email.py ]
     |         |
     |         v
     |       ( Inicia bucle: Para cada destinatario en la lista )
     |         |
     |         v
     |       [ a. Filtra el DataFrame para el destinatario actual ]
     |         |
     |         v
     |       [ b. Guarda los datos filtrados en un nuevo archivo <Reporte_EC-XX.csv> ]
     |         |
     |         v
     |       [ c. Envía un correo electrónico adjuntando el archivo CSV ]
     |         |
     |         v
     |       ( ¿Hay más destinatarios? ) --Sí--> [ Repite el bucle ]
     |         |
     |         +--No
     |         |
     v
[ Proceso finalizado ]
     |
     v
( Fin )
```