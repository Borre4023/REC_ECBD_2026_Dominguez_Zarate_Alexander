# Power BI — versión alternativa del dashboard

Esta carpeta contiene el dashboard de Power BI (versión de BI corporativo) del proyecto
South German Credit. El dashboard HTML (`dashboard/index.html`) sigue siendo el entregable
reproducible con un comando; este `.pbix` muestra la misma historia en Power BI Desktop.

## Contenido

| Ruta | Descripción |
|---|---|
| `datos/*.csv` | Datos exportados del Data Mart SQLite y de los artefactos de modelos (regenerables) |
| `SouthGermanCredit.pbix` | Dashboard con las 4 páginas (lo construye el alumno en Power BI Desktop) |

## Regenerar los datos

```bash
py src/dashboard/exportar_powerbi.py
```

Salidas en `datos/` (UTF-8 con BOM, separador `;`, decimales con punto):

- `dm_riesgo_crediticio.csv` — 1 000 créditos × 23 columnas (vista plana del Data Mart)
- `segmentos.csv` — perfil de los 2 clústeres
- `pca_coordenadas.csv` — PC1/PC2 + clúster por crédito
- `pca_varianza.csv` — 70 CP con varianza explicada y acumulada
- `seleccion_k.csv` — k = 2..8 con inercia y silhouette
- `metricas_modelos.csv` — métricas en formato largo
- `matriz_confusion.csv` — real × predicción (TP/FN/FP/TN)

## Construcción del `.pbix`

Seguir `docs/resultados/guia_powerbi.md`: importación, medidas DAX, las 4 páginas,
paleta y checklist de aceptación (cifras idénticas al dashboard HTML).

> Nota: el `.pbix` es un binario; los cambios de datos se reflejan al actualizar los CSV
> y refrescar el modelo en Power BI (Inicio → Actualizar).
