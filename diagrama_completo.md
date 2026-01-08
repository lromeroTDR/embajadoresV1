
# Código del Diagrama de Flujo Completo (Formato DOT)

Copia y pega el siguiente código en un renderizador de Graphviz (como [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/)) para generar el diagrama de flujo visual.

```dot
digraph EmbajadoresPipeline {
    // Configuración General
    graph [
        label="Diagrama de Flujo Detallado del Pipeline de Embajadores",
        labelloc=t,
        fontsize=20,
        fontname="Helvetica",
        rankdir=TB,
        splines=ortho
    ];
    node [
        shape=box,
        style="rounded,filled",
        fillcolor="#E6F7FF", // Azul claro
        fontname="Helvetica"
    ];
    edge [fontsize=10, fontname="Helvetica"];

    // Nodos de Inicio y Fin
    start [label="Inicio", shape=ellipse, style=filled, fillcolor="#C3E6CB"]; // Verde
    end [label="Fin", shape=ellipse, style=filled, fillcolor="#F5C6CB"]; // Rojo

    // --- Grupos de Archivos (Clusters) ---

    // Cluster para main.py
    subgraph cluster_main {
        label = "main.py";
        style="filled,rounded";
        fillcolor="#F0F0F0"; // Gris claro
        
        main_start [label="Punto de Entrada: Inicia la ejecución"];
        call_pipeline [label="Llama a 'pipeline.run()'"];
        read_excel [label="Lee 'Embajadores.xlsx'\npara obtener la lista de destinatarios"];
        call_email [label="Llama a 'mandar_email.procesar_y_notificar()'"];
    }

    // Cluster para pipeline.py
    subgraph cluster_pipeline {
        label = "pipeline.py (Módulo de Extracción y Transformación)";
        style="filled,rounded";
        fillcolor="#D9EAD3"; // Verde pálido
        
        pipeline_run [label="Función 'run'"];
        get_dates [label="Obtiene rango de fechas\ndesde 'rango_tiempo.py'"];
        get_config [label="Lee el token de la API\ndesde 'config.py'"];
        fetch_data [label="Extrae datos de la API de Samsara\n(vehículos, scores, eventos de seguridad)"];
        process_data [label="Unifica y procesa los datos\nen un DataFrame Maestro"];
    }

    // Cluster para mandar_email.py
    subgraph cluster_email {
        label = "mandar_email.py (Módulo de Notificación)";
        style="filled,rounded";
        fillcolor="#FFF2CC"; // Amarillo pálido
        
        procesar_notificar [label="Función 'procesar_y_notificar'"];
        loop_start [label="¿Hay destinatarios\nen la lista?", shape=diamond, style=filled, fillcolor="#FDE2A2"];
        filter_df [label="Filtra el DataFrame para el\ndestinatario actual"];
        save_csv [label="Guarda los datos filtrados en\nun nuevo archivo 'Reporte_EC-XX.csv'"];
        send_email [label="Envía el reporte por correo\ncon el archivo CSV adjunto"];
    }

    // --- Nodos de Datos y Archivos Externos ---
    node [shape=note, style=filled, fillcolor="#FDDFD6"]; // Rosa pálido
    embajadores_xlsx [label="Archivo\nEmbajadores.xlsx"];
    config_py [label="Archivo\nconfig.py"];
    rango_py [label="Archivo\nrango_tiempo.py"];
    reporte_csv [label="Archivo\nReporte_EC-XX.csv"];
    
    node [shape=cylinder, style=filled, fillcolor="#D1D1D1"]; // Gris oscuro
    samsara_api [label="API Externa\nde Samsara"];

    // --- Conexiones del Flujo ---
    
    // Flujo principal
    start -> main_start;
    main_start -> call_pipeline;
    
    // Flujo dentro de pipeline.py
    call_pipeline -> pipeline_run [lhead=cluster_pipeline, label="Ejecuta el pipeline"];
    rango_py -> get_dates;
    config_py -> get_config;
    pipeline_run -> get_dates;
    pipeline_run -> get_config;
    get_dates -> fetch_data;
    get_config -> fetch_data;
    samsara_api -> fetch_data [label="Peticiones GET"];
    fetch_data -> process_data;
    
    // Retorno a main.py y continuación
    process_data -> call_email [ltail=cluster_pipeline, label="Retorna el\nDataFrame Maestro"];
    main_start -> read_excel;
    embajadores_xlsx -> read_excel [label="Lee la lista"];
    read_excel -> call_email [label="Entrega la lista\nde destinatarios"];
    
    // Flujo dentro de mandar_email.py
    call_email -> procesar_notificar [lhead=cluster_email, label="Ejecuta el\nproceso de notificación"];
    procesar_notificar -> loop_start;
    loop_start -> filter_df [label="Sí"];
    filter_df -> save_csv;
    save_csv -> reporte_csv [dir=back, style=dashed];
    save_csv -> send_email;
    send_email -> loop_start [label="Siguiente destinatario"];
    
    // Fin del proceso
    loop_start -> end [label="No"];
}

```