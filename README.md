# Análisis de riesgo crediticio de clientes

Proyecto Integrador de Recursamiento — **Extracción de Conocimiento en Bases de Datos**
Universidad Tecnológica de Tula-Tepeji (UTTT)

**Alumno:** Alexander Domínguez Zárate · **Matrícula:** 23301324

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Metodología](https://img.shields.io/badge/Metodolog%C3%ADa-CRISP--DM-informational) ![Estado](https://img.shields.io/badge/Estado-en%20desarrollo-yellow)

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

Python · Pandas · NumPy · Matplotlib · Seaborn · Scikit-learn · PostgreSQL / SQL · Jupyter Notebook · Git y GitHub · Dashboard (Power BI, Tableau o Streamlit; por definir)

## Estructura del repositorio

```text
south-german-credit/
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_preparacion.ipynb
│   ├── 03_regresion.ipynb
│   ├── 04_clasificacion.ipynb
│   ├── 05_clustering.ipynb
│   └── 06_pca.ipynb
├── src/
│   ├── etl/
│   ├── preprocessing/
│   └── models/
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── modelos/
│   ├── regresion/
│   ├── clasificacion/
│   └── clustering/
├── dashboard/
└── docs/
    ├── planeacion/
    ├── diccionario_datos/
    ├── analisis/
    ├── modelos/
    └── resultados/
```

## Cronograma

| Fecha | Actividad | Producto esperado |
|---|---|---|
| 2 oct | Documento de planeación | Informe inicial |
| 9 oct | Diccionario de datos, exploración y limpieza inicial | Diccionario + notebook EDA + propuesta DW/Data Mart |
| 16 oct | ETL, datos procesados, DW/Data Mart y repositorio | Pipeline ETL + dataset procesado + estructura de BD |
| 23 oct | Modelos de regresión y clasificación | Primeros modelos funcionando |
| 30 oct | Análisis supervisado | Modelos + métricas + evaluación + optimización + informe |
| 6 nov | Clustering y reducción de dimensionalidad | Modelos no supervisados funcionando |
| 13 nov | Análisis no supervisado | Modelos + evaluación + interpretación + informe |
| 17 nov | Dashboard y storytelling | Dashboard revisado + narrativa preliminar |
| 20 nov | Entrega final | Dashboard + repositorio + informe + defensa |

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
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
jupyter notebook notebooks/
```

> Este apartado se completará (dependencias exactas, carga a PostgreSQL y ejecución del dashboard) conforme avance el proyecto.

## Documentación

El informe completo de planeación está en `docs/planeacion/`.
