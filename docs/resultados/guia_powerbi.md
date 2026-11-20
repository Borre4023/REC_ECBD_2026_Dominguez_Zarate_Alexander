# Guía de construcción del dashboard en Power BI (versión alternativa)

**Proyecto:** Análisis de riesgo crediticio — South German Credit (UTTT)
**Alumno:** Alexander Domínguez Zárate · Matrícula 23301324
**Entregable:** `powerbi/SouthGermanCredit.pbix` (mismas 4 páginas que `dashboard/index.html`)

Esta guía describe cómo construir el dashboard en **Power BI Desktop** a partir de los CSV
exportados del Data Mart. El dashboard HTML sigue siendo el entregable reproducible con un
comando; el `.pbix` es la versión de BI corporativo (misma historia, mismas cifras).

---

## 1. Requisitos y datos

- Power BI Desktop (Store o instalador), versión 2.1xx o superior.
- Datos generados con:

```bash
py src/dashboard/exportar_powerbi.py
```

| Archivo (`powerbi/datos/`) | Contenido | Uso |
|---|---|---|
| `dm_riesgo_crediticio.csv` | 1 000 créditos × 23 columnas (vista plana del Data Mart) | Todas las páginas descriptivas |
| `segmentos.csv` | Perfil de los 2 clústeres (clientes, monto, plazo, % bad) | Página 4 |
| `pca_coordenadas.csv` | PC1, PC2 y clúster por crédito | Scatter de la página 4 |
| `pca_varianza.csv` | 70 CP con varianza explicada y acumulada | Scree (opcional) |
| `seleccion_k.csv` | k = 2..8 con inercia y silhouette | Línea de silhouette (página 4) |
| `metricas_modelos.csv` | Métricas en formato largo (problema, modelo, métrica, valor, conjunto) | Tarjetas de la página 4 |
| `matriz_confusion.csv` | real × predicción (TP/FN/FP/TN) | Matriz de la página 4 |

**Formato de los CSV:** UTF-8 con BOM, separador `;`, decimales con punto. Al importar,
usar *Texto/CSV* → delimitador `;` → codificación 65001: UTF-8 → "Detectar tipos de datos".

## 2. Importación y modelo

1. **Inicio → Obtener datos → Texto/CSV** y cargar los 7 archivos.
2. En *Transformar datos*, verificar tipos:
   - Enteros: `sk_credito`, `edad`, `personas_a_cargo`, `duracion_meses`, `monto_dm`,
     `tiempo_residencia`, `num_creditos_banco`, `riesgo_credito`, `cluster`, `k`,
     `clientes`, `creditos`.
   - Decimales: `cuota_aprox_mensual`, `pc1`, `pc2`, `valor`, `pct_bad`, `monto_medio_dm`,
     `plazo_medio_meses`, `edad_media`, `var_explicada_pct`, `acumulada_pct`, `inercia`,
     `silhouette`.
   - Texto: el resto (categorías decodificadas, `riesgo_credito_cat`, `segmento`, etc.).
3. **Modelo:** cada archivo es una tabla independiente; **no se necesitan relaciones**
   (`dm_riesgo_crediticio` es una tabla plana). Ocultar en la vista de informe las tablas
   auxiliares (`pca_varianza`, `seleccion_k`) y dejar solo los campos usados.

## 3. Medidas DAX (copiar en `dm_riesgo_crediticio`)

```dax
Total Créditos = COUNTROWS('dm_riesgo_crediticio')

Créditos Bad =
CALCULATE([Total Créditos], 'dm_riesgo_crediticio'[riesgo_credito] = 0)

% Bad = DIVIDE([Créditos Bad], [Total Créditos])

Monto Total DM = SUM('dm_riesgo_crediticio'[monto_dm])

Monto Medio DM = AVERAGE('dm_riesgo_crediticio'[monto_dm])

Cuota Media DM = AVERAGE('dm_riesgo_crediticio'[cuota_aprox_mensual])

Plazo Medio Meses = AVERAGE('dm_riesgo_crediticio'[duracion_meses])
```

Columnas calculadas para el histograma de montos (página 1 y 3):

```dax
Rango Monto =
SWITCH(TRUE(),
    'dm_riesgo_crediticio'[monto_dm] < 1500, "< 1 500",
    'dm_riesgo_crediticio'[monto_dm] < 4000, "1 500–3 999",
    'dm_riesgo_crediticio'[monto_dm] < 8000, "4 000–7 999",
    "≥ 8 000")

Orden Rango Monto =
SWITCH([Rango Monto], "< 1 500", 1, "1 500–3 999", 2, "4 000–7 999", 3, 4)
```

Ordenar `Rango Monto` por `Orden Rango Monto` (Herramientas de columna → Ordenar por columna).

En `segmentos`:

```dax
% Bad Segmento = MAX('segmentos'[pct_bad]) / 100
```

Formatear como porcentaje con 1 decimal.

## 4. Páginas (mismas 4 del dashboard HTML)

### Página 1 · Panorama de la cartera

| Visual | Campos |
|---|---|
| 6 tarjetas (Cards) | `Total Créditos` · `% Bad` · `Monto Total DM` · `Monto Medio DM` · `Plazo Medio Meses` · `Cuota Media DM` |
| Dona o barras 100 % | Leyenda `riesgo_credito_cat`, valores `Total Créditos` |
| Columnas | Eje `Rango Monto`, valores `Total Créditos` |

Cifras de control: 1 000 créditos · 30.0 % bad · 3 271 248 DM totales · 3 271 DM medio ·
20.9 meses · 167.7 DM/mes.

### Página 2 · ¿Quién incumple? (Q1 y Q3)

| Visual | Campos |
|---|---|
| Barras agrupadas | Eje `historial_crediticio`, valor `% Bad`, orden descendente |
| Matriz | Filas `estado_cuenta`, columnas `ahorros`, valores `% Bad`; formato condicional (escala de color) |
| Tarjeta de contraste | Filtro `estado_cuenta = no_checking` + `ahorros = unknown` → 52.1 %; `estado_cuenta = ge200_or_salary` + `ahorros = ge1000` → 9.1 % (regla ×5.7) |

### Página 3 · ¿Cuánta exposición? (Q5, Q2 y Q4)

| Visual | Campos |
|---|---|
| Columnas | Eje `Rango Monto`, valor `% Bad` (28.8 → 23.9 → 38.1 → 54.3 %) |
| Barras | Eje `proposito`, valor `Monto Medio DM`, orden descendente (`business` 8 209 DM) |
| Tabla top-10 | `sk_credito`, `proposito`, `monto_dm`, `cuota_aprox_mensual`, `riesgo_credito_cat`; filtro Top N 10 por `cuota_aprox_mensual`; color condicional: bad en rojo |

### Página 4 · Modelos y segmentos (Unidades III y IV)

| Visual | Campos |
|---|---|
| Tarjetas | `metricas_modelos`: filtro `conjunto = test` → `roc_auc` 0.835 · `accuracy` 0.725 · `recall_bad` 0.767 · `r2` 0.596 |
| Matriz | `matriz_confusion`: filas `real`, columnas `prediccion`, valores `creditos` (46/14/41/99) |
| Dispersión (Scatter) | X `pc1`, Y `pc2`, leyenda `cluster` (0 azul / 1 naranja) |
| Columnas | Eje `segmento`, valor `% Bad Segmento` (43.7 % vs 25.3 %) |
| Línea (opcional) | `seleccion_k`: eje `k`, valor `silhouette` (máximo en k = 2) |

## 5. Formato y estilo

- Tema claro, tipografía **Segoe UI**, títulos de página `1 · Panorama de la cartera`, etc.
- Paleta: azul `#1D3F5C` (estructura), rojo `#B03A2E` (bad), verde `#2E9464` (good),
  gris `#5D6D7E` (texto secundario), fondo de tarjetas `#EEF3F7`.
- Etiquetas de datos activadas en barras y tarjetas; sin decimales en conteos, 1 decimal en %.
- Cada página con una caja de texto corta al pie: la lectura de negocio (misma que el dashboard
  HTML: "vigilar la exposición, no el perfil superficial").

## 6. Guardar y publicar

1. Guardar como **`powerbi/SouthGermanCredit.pbix`** (dentro del repo, para versionarlo).
2. Capturas: *Archivo → Exportar → Exportar a PDF* no sirve para el informe; usar
   **Recortes (Win + Shift + S)** o `Alt + Impr. Pant` por página, guardando como:
   - `docs/resultados/capturas_powerbi/01_panorama.png`
   - `docs/resultados/capturas_powerbi/02_riesgo.png`
   - `docs/resultados/capturas_powerbi/03_exposicion.png`
   - `docs/resultados/capturas_powerbi/04_modelos_segmentos.png`
3. Avisar para integrar la subsección **7.5 "Dashboard alternativo en Power BI"** del informe
   y rehacer el HTML con pandoc.

## 7. Checklist de aceptación (contra el dashboard HTML)

- [ ] Página 1: 1 000 créditos, 30.0 % bad, 3 271 248 DM, 3 271 DM, 20.9 meses, 167.7 DM/mes.
- [ ] Página 2: gradiente 62.5 % → 17.1 %; matriz con 52.1 % vs 9.1 % y regla ×5.7.
- [ ] Página 3: 54.3 % en ≥ 8 000 DM; `business` 8 209 DM; top-10 con 40 % bad.
- [ ] Página 4: AUC 0.835, accuracy 0.725, recall 76.7 %, R² 0.596; matriz 46/14/41/99;
      clústeres 254 (43.7 %) vs 746 (25.3 %).
