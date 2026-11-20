# Análisis de riesgo crediticio de clientes

Proyecto Integrador de Recursamiento — **Extracción de Conocimiento en Bases de Datos**
Universidad Tecnológica de Tula-Tepeji (UTTT)

**Alumno:** Alexander Domínguez Zárate · **Matrícula:** 23301324

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Metodología](https://img.shields.io/badge/Metodolog%C3%ADa-CRISP--DM-informational) ![Estado](https://img.shields.io/badge/Estado-completado-brightgreen)

---

## Descripción

Análisis integral del dataset **South German Credit** (UCI Machine Learning Repository): 1,000 casos de crédito y 21 variables financieras, crediticias, laborales, personales y habitacionales. La variable principal es `credit_risk` (`good` / `bad`).

El proyecto se desarrolla como un ejercicio de **KDD** que incluye análisis exploratorio, ETL, almacenamiento en Data Warehouse/Data Mart, aprendizaje supervisado (clasificación y regresión), aprendizaje no supervisado (clustering y PCA) y un dashboard para comunicar los hallazgos.

> **Pregunta principal:** ¿Qué patrones presentes en las características financieras, crediticias y personales de los clientes permiten explicar y modelar el comportamiento observado de los créditos en el dataset South German Credit?

| Enfoque | Pregunta específica |
|---|---|
| Clasificación | ¿Es posible clasificar un crédito como `good` o `bad` con las características disponibles? |
| Regresión | ¿Es posible estimar el monto del crédito (`amount`) a partir de las demás características? |
| No supervisado | ¿Es posible identificar grupos de clientes con perfiles financieros y crediticios similares? |

## Dataset

| Característica | Información |
|---|---|
| Fuente | [UCI Machine Learning Repository – South German Credit](https://archive.ics.uci.edu/dataset/573/south+german+credit) |
| Registros | 1,000 |
| Variables | 21 (20 predictoras potenciales) |
| Objetivo de clasificación | `credit_risk` |
| Objetivo de regresión | `amount` |
| Valores faltantes | No reportados |

**Tipos de variables**

| Tipo | Ejemplos |
|---|---|
| Cuantitativas | `duration`, `amount`, `age` |
| Categóricas | `status`, `credit_history`, `purpose`, `savings`, `housing` |
| Ordinales | `employment_duration`, `installment_rate`, `present_residence`, `number_credits`, `job` |
| Binarias | `people_liable`, `telephone`, `foreign_worker` |

## Objetivos

**General:** analizar y transformar los datos mediante técnicas de KDD para identificar patrones relacionados con el riesgo crediticio, desarrollar modelos supervisados y no supervisados, y comunicar los resultados mediante visualización.

**Específicos**

1. Documentar estructura, características y calidad del dataset (diccionario de datos y EDA).
2. Diseñar e implementar la preparación y transformación de datos (ETL).
3. Diseñar un Data Warehouse o Data Mart para organizar la información.
4. Desarrollar y evaluar modelos de clasificación (`credit_risk`) y regresión (`amount`).
5. Aplicar clustering y reducción de dimensionalidad para identificar perfiles de clientes.
6. Construir un dashboard que comunique los principales hallazgos.

## Avance actual

- [x] Diccionario de datos v2 con los 8 campos de la Unidad II (`docs/diccionario_datos/diccionario_datos_v2.md`; versión anterior respaldada en `diccionario_datos_v1.md`)
- [x] Exploración y limpieza inicial (`notebooks/01_exploracion.ipynb`, `notebooks/02_preparacion_etl.ipynb`)
- [x] ETL implementado con contrato de calidad (`src/etl/etl_south_german_credit.py`, 7/7 chequeos OK) y datos procesados (`data/processed/`)
- [x] Propuesta de Data Warehouse/Data Mart (`docs/analisis/propuesta_dw_datamart.md`)
- [x] Esquema SQL para DW/DM (`sql/schema_dw.sql`, diseño PostgreSQL teórico)
- [x] **Data Mart implementado en SQLite** (`sql/schema_dw_sqlite.sql` + `src/etl/build_dw_sqlite.py`): modelo estrella con 8 dimensiones, `fact_credito` (1000 filas), vista `dm_riesgo_crediticio` y 5 consultas analíticas (`sql/queries_dm.sql`); 0 violaciones de integridad
- [x] **Unidad III — modelos supervisados con sklearn** (`src/models/entrenar_regresion.py`, `entrenar_clasificacion.py`): regresión del monto R² test 0.596 (RidgeCV); clasificación del riesgo ROC-AUC test 0.835 (logística balanceada), recall de bads 76.7%; evaluación en `docs/modelos/evaluacion_modelos.md`; notebooks 03–04 didácticos ejecutados sin errores
- [x] **Informe de exploración técnica (Unidad II)** con 10 secciones, diagnóstico de calidad y visualizaciones (`docs/analisis/exploracion_tecnica.md` + versión HTML autocontenida `exploracion_tecnica.html`); gráficas en `docs/analisis/figuras/` (reproducibles con `py src/preprocessing/exploracion_tecnica.py`)
- [x] **Unidad IV — clustering y PCA** (`src/models/clustering_pca.py`, `notebooks/05_clustering_pca.ipynb`): PCA (PC1 = eje exposición, 23 CP para 80% de varianza) y K-means k=2 con validación post-hoc (segmento de exposición alta: 43.7% bad); evaluación en `docs/modelos/clustering_pca.md`
- [x] **Dashboard HTML autocontenido** (`dashboard/index.html`): KPIs + consultas Q1–Q5 del Data Mart + resultados de modelos y segmentos; figuras en base64, generado con `py src/dashboard/generar_dashboard.py`
- [x] **Cierre (Fase 6):** diagrama del esquema estrella (`docs/analisis/figuras/diagrama_dw.png`), 4 capturas del dashboard (`docs/resultados/capturas/`) e informe final borrador APA 7 (`docs/resultados/informe_final_borrador.md` + `.html`)
- [x] **Dashboard alternativo en Power BI** (`powerbi/SouthGermanCredit.pbix`): 4 páginas con las mismas cifras del dashboard HTML, alimentadas por los CSV que exporta `py src/dashboard/exportar_powerbi.py`; guía en `docs/resultados/guia_powerbi.md`, capturas en `docs/resultados/capturas_powerbi/` e integración en la §7.5 del informe final

## Metodología

Se toma como referencia **KDD** y se organiza con **CRISP-DM**:

| Fase | Aplicación al proyecto |
|---|---|
| Comprensión del negocio | Definir el problema de riesgo crediticio |
| Comprensión de los datos | Diccionario de datos, EDA y análisis de calidad |
| Preparación | `raw` → ETL → `processed` → Data Warehouse / Data Mart |
| Modelado | Regresión, clasificación, clustering y PCA |
| Evaluación | Métricas, comparación e interpretación de modelos |
| Despliegue | Dashboard, documentación y repositorio |

Debido al desbalance de clases, la clasificación no se evalúa solo con *accuracy*: también se usan precision, recall, F1-score, matriz de confusión y ROC-AUC.

## Herramientas

Python 3 · Pandas · NumPy · Matplotlib · Seaborn · Scikit-learn · SQLite (+ PostgreSQL como diseño teórico) · Jupyter Notebook · Jinja2 (dashboard) · Git y GitHub

## Estructura del repositorio

```text
south-german-credit/
├── README.md
├── data/
│   ├── raw/
│   └── processed/          # dataset ETL + dw_south_german_credit.db + reportes JSON
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_preparacion_etl.ipynb
│   ├── 03_regresion.ipynb
│   ├── 04_clasificacion.ipynb
│   └── 05_clustering_pca.ipynb
├── src/
│   ├── etl/                # etl_south_german_credit.py, build_dw_sqlite.py
│   ├── preprocessing/      # exploracion_tecnica.py, figuras_fuente.py
│   ├── models/             # entrenar_regresion.py, entrenar_clasificacion.py, clustering_pca.py
│   └── dashboard/          # generar_dashboard.py + plantilla.html + exportar_powerbi.py
├── sql/
│   ├── schema_dw.sql       # diseño PostgreSQL (teórico)
│   ├── schema_dw_sqlite.sql
│   └── queries_dm.sql
├── modelos/                # .pkl + metricas.json por problema
│   ├── regresion/
│   ├── clasificacion/
│   └── clustering/
├── dashboard/
│   └── index.html          # dashboard autocontenido (abrir en navegador)
├── powerbi/                # versión alternativa en Power BI (datos/*.csv + .pbix)
├── legacy/                 # scripts de la fase manual pre-sklearn (solo referencia histórica)
└── docs/
    ├── planeacion/
    ├── diccionario_datos/
    ├── analisis/
    ├── modelos/            # evaluacion_modelos.md, clustering_pca.md, figuras/
    └── resultados/
```

## Cronograma

| Fecha | Actividad | Producto esperado | Estado |
|---|---|---|---|
| 2 oct | Documento de planeación | Informe inicial | ✅ Completado |
| 9 oct | Diccionario de datos, exploración y limpieza inicial | Diccionario + notebook EDA + propuesta DW/Data Mart | ✅ Completado |
| 16 oct | ETL, datos procesados, DW/Data Mart y repositorio | Pipeline ETL + dataset procesado + estructura de BD | ✅ Completado |
| 23 oct | Modelos de regresión y clasificación | Primeros modelos funcionando | ✅ Completado (primera versión manual por restricciones del entorno; rehecho con sklearn el 16 nov) |
| 6 nov | Clustering y reducción de dimensionalidad | Modelos no supervisados funcionando | ✅ Completado |
| 13 nov | Análisis no supervisado | Modelos + evaluación + interpretación + informe | ✅ Completado |
| 17 nov | Dashboard y storytelling | Dashboard revisado + narrativa preliminar | ✅ Completado (dashboard autocontenido + consultas del Data Mart) |
| 20 nov | Entrega final | Dashboard + repositorio + informe + defensa | ✅ Completado |

**Nota (16 nov):** el proyecto quedó completo con sklearn (desbloqueado desde el 9 nov): ETL con contrato de calidad 7/7, Data Mart SQLite validado, modelos supervisados (R² 0.596 / AUC 0.835), clustering con validación post-hoc (43.7% vs 25.3% bad) y dashboard autocontenido. La bitácora completa está en `docs/Informe de cambios (actualiza esta cosa cada cambio).md`.

## Limitaciones

- **Antigüedad:** los datos corresponden a créditos de aproximadamente 1973–1975.
- **Tamaño:** 1,000 registros; adecuado para ejercicios académicos, pero pequeño para representar una población amplia.
- **Muestreo:** los créditos `bad` están sobrerrepresentados, por lo que su proporción no equivale a una tasa real de incumplimiento.
- **Variables codificadas:** requieren distinguir entre numéricas, categóricas, ordinales y binarias.
- **Inferencia:** los modelos tienen finalidad académica y analítica; no sirven para aprobar o rechazar créditos reales. Los resultados son hallazgos de este dataset, no reglas universales.

## Cómo reproducir el análisis

```bash
git clone <url-del-repositorio>
cd south-german-credit
pip install pandas numpy matplotlib seaborn scikit-learn jinja2 jupyter pyarrow

# 1) ETL: dataset procesado + reporte de calidad (7/7 chequeos OK)
py src/etl/etl_south_german_credit.py

# 2) Data Warehouse / Data Mart en SQLite (0 violaciones FK)
py src/etl/build_dw_sqlite.py

# 3) Modelos supervisados (pkl + metricas.json + figuras)
py src/models/entrenar_regresion.py        # RidgeCV, R2 test 0.596
py src/models/entrenar_clasificacion.py    # logistica balanceada, AUC 0.835

# 4) Unidad IV: PCA + K-means (k=2, validacion post-hoc)
py src/models/clustering_pca.py

# 5) Dashboard autocontenido -> dashboard/index.html (abrir en navegador)
py src/dashboard/generar_dashboard.py

# versión didáctica paso a paso (notebooks ejecutados, 0 errores)
jupyter notebook notebooks/
```

Todos los scripts usan rutas relativas a la raíz del repositorio y `random_state=42`
para reproducibilidad completa.

## Documentación

| Documento | Ruta |
|---|---|
| Informe de planeación | `docs/planeacion/` |
| Diccionario de datos v2 | `docs/diccionario_datos/diccionario_datos_v2.md` |
| Exploración técnica (Unidad II) | `docs/analisis/exploracion_tecnica.md` (+ `.html`) |
| Documentación del ETL | `docs/analisis/etl_documentacion.md` |
| Propuesta DW/Data Mart | `docs/analisis/propuesta_dw_datamart.md` |
| Implementación del Data Mart (SQLite) | `docs/analisis/dw_datamart_implementacion.md` |
| Evaluación de modelos (Unidad III) | `docs/modelos/evaluacion_modelos.md` |
| Clustering y PCA (Unidad IV) | `docs/modelos/clustering_pca.md` |
| **Informe final (borrador, APA 7)** | `docs/resultados/informe_final_borrador.md` (+ `.html` autocontenida) |
| **Capturas del dashboard** | `docs/resultados/capturas/` (HTML) · `docs/resultados/capturas_powerbi/` (Power BI) |
| Guía del dashboard en Power BI | `docs/resultados/guia_powerbi.md` (+ `powerbi/README.md`) |
| Diagrama del Data Mart | `docs/analisis/figuras/diagrama_dw.png` (generable con `py src/etl/diagrama_dw.py`) |
| Separación de datos y regeneración | `data/README.md` |
| Bitácora de cambios | `docs/Informe de cambios (actualiza esta cosa cada cambio).md` |
| Dashboard | `dashboard/index.html` · alternativo en Power BI: `powerbi/SouthGermanCredit.pbix` |

## Hallazgos principales

1. **El historial crediticio es la señal más fuerte:** 62.5% bad con atraso previo vs. 17.1% con historial limpio en el banco (gradiente monotónico).
2. **La exposición escala el riesgo de forma no lineal:** el riesgo cae (28.8% → 23.9%) y luego sube hasta 54.3% en créditos ≥ 8000 DM.
3. **El segmento riesgoso es el cliente solvente sobreexpuesto:** sin usar la respuesta, K-means separa dos economías del crédito — 254 clientes de exposición alta (6 895 DM, 36 meses) con 43.7% bad vs. 746 de exposición baja con 25.3%.
4. **Una logística balanceada detecta el 77% de los morosos** (ROC-AUC 0.835 en test) a cambio de un 29% de falsas alarmas; las variables dominantes (`laufkont`, `moral`, `sparkont`) coinciden con las consultas del Data Mart.
