
# Diagrama Detallado de Extracción de Datos (Formato DOT)

Este diagrama se enfoca exclusivamente en el funcionamiento interno de `pipeline.py`, detallando las funciones y los endpoints de la API que se utilizan.

```dot
digraph DetailedExtraction {
    graph [
        label="Diagrama Detallado de Extracción de Datos (pipeline.py)",
        labelloc=t,
        fontsize=18,
        rankdir=TB
    ];
    node [shape=box, style="rounded,filled", fontname="Helvetica"];
    edge [fontname="Helvetica", fontsize=9];

    subgraph cluster_pipeline {
        label = "pipeline.py";
        style="filled,rounded";
        fillcolor="#D9EAD3";

        // Funciones principales del pipeline
        p_main [label="Función principal 'pipeline()'"];
        p_extract_vehicles [label="1. extraer_vehiculos()"]
        p_transform_vehicles [label="1.1. transformacion_vehiculos()"]
        p_extract_score [label="2. extraer_score_vehiculo()"]
        p_join_scores [label="3. transformar_unir_vehiculos_puntuaciones()"]
        p_extract_events [label="4. extraer_eventos_seguridad()"]
        p_transform_events [label="4.1. transformar_eventos_seguridad()"]
        p_join_events [label="5. unir_vehiculos_eventos_seguridad()"]
        p_extract_tags [label="6. extraer_tags_samsara()"]
        p_join_tags [label="6.1. unir_tag_metricas_vehiculo()"]
        p_final_process [label="A, B, C: Ordenar,\nFiltrar y Traducir"];
    }

    // Nodos externos (APIs, archivos de config)
    node [style="filled", fillcolor="#FFF2CC"];
    config [label="config.py", shape=note];
    rango [label="rango_tiempo.py", shape=note];
    
    node [shape=cylinder, style=filled, fillcolor="#D1D1D1"];
    api_vehicles [label="GET /fleet/vehicles"];
    api_safety_score [label="GET /v1/fleet/vehicles/{id}/safety/score"];
    api_safety_events [label="GET /fleet/safety-events"];
    api_tags [label="GET /tags"];

    // Flujo de ejecución
    p_main -> rango [label="Obtiene fechas"];
    p_main -> config [label="Obtiene headers"];
    
    p_main -> p_extract_vehicles;
    p_extract_vehicles -> api_vehicles [label="Llama a API"];
    p_extract_vehicles -> p_transform_vehicles [label="Retorna df_vehiculos"];
    
    p_transform_vehicles -> p_extract_score [label="Retorna df_vehiculos_transformado"];
    p_extract_score -> api_safety_score [label="Llama a API por cada vehículo"];
    p_extract_score -> p_join_scores [label="Retorna df_scores"];
    
    p_join_scores -> p_extract_events [label="Retorna df_unido_1"];
    p_extract_events -> api_safety_events [label="Llama a API"];
    p_extract_events -> p_transform_events [label="Retorna df_eventos"];
    p_transform_events -> p_join_events [label="Retorna df_eventos_procesado"];

    p_join_events -> p_extract_tags [label="Retorna df_unido_2"];
    p_extract_tags -> api_tags [label="Llama a API"];
    p_extract_tags -> p_join_tags [label="Retorna df_tags"];

    p_join_tags -> p_final_process [label="Retorna df_unido_3"];
    
    p_final_process [shape=invhouse, style=filled, fillcolor="#C3E6CB", label="Retorna DataFrame Final"];
}
```