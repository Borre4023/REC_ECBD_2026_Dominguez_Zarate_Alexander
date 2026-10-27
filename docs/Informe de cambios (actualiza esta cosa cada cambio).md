# Informe detallado del procedimiento - Proyecto South German Credit

**Alumno:** Alexander Domínguez Zárate  
**Matrícula:** 23301324  
**Materia:** Extracción de Conocimiento en Bases de Datos  
**Fecha:** 2026-10-27  

## 1. Objetivo general
Analizar el dataset South German Credit (UCI) mediante metodología KDD/CRISP-DM para identificar patrones de riesgo crediticio, preparar los datos (ETL), proponer un DW/Data Mart, y desarrollar modelos de regresión y clasificación, con fines académicos y formativos.

## 2. Metodología empleada
- **KDD (Knowledge Discovery in Databases):** Selección, preprocesamiento, transformación, minería de datos, interpretación/evaluación.
- **CRISP-DM:** Comprensión del negocio, comprensión de los datos, preparación, modelado, evaluación, despliegue (documentado).
- **Spec-Driven Development:** Se parte de especificación (README/cronograma), se diseña (diccionario, DW), se implementa (ETL, notebooks), se valida y documenta.

## 3. Datos
- **Fuente:** UCI Machine Learning Repository - South German Credit (ID 573)
- **Tamaño:** 1000 registros, 21 variables
- **Objetivo clasificación:** `credit_risk` (0=bad, 1=good). Distribución: 700 buenos / 300 malos (desbalance)
- **Objetivo regresión:** `amount` (`hoehe`) - monto del crédito en DM
- **Valores faltantes:** No reportados
- **Periodo:** 1973-1975

### 3.1. Diccionario de datos
Se elaboró `docs/diccionario_datos/diccionario_datos.md` con mapeo completo basado en `data/raw/codetable.txt`:
- Variables numéricas: `duration` (laufzeit), `amount` (hoehe), `age` (alter)
- Categóricas/ordinales/binarías decodificadas: `status`, `credit_history`, `purpose`, `savings`, `employment_duration`, `installment_rate`, `personal_status_sex`, `other_debtors`, `present_residence`, `property`, `other_installment_plans`, `housing`, `number_credits`, `job`, `people_liable`, `telephone`, `foreign_worker`
- Variable objetivo: `credit_risk` (0 bad / 1 good)

## 4. Comprensión y preparación de datos (Exploración y limpieza)
**Notebooks:** `notebooks/01_exploracion.ipynb`, `notebooks/02_preparacion_etl.ipynb`

**Análisis realizado:**
- Carga de datos crudos (`data/raw/SouthGermanCredit.asc`, separador espacio)
- Inspección: shape (1000x21), tipos, valores únicos
- Calidad: revisión de nulos (sin nulos reportados/detectados)
- Distribución del objetivo: desbalance 70% good / 30% bad
- Decodificación de códigos a etiquetas legibles según codetable
- Generación de versiones decodificadas (`*_cat`)

**Resultado:** Datos limpios y comprensibles para modelado.

## 5. ETL y Data Warehouse / Data Mart
### 5.1. ETL
**Script:** `src/etl/etl_south_german_credit.py`  
**Documentación:** `docs/analisis/etl_documentacion.md`

**Flujo:**
1. **Extract:** Lectura desde `data/raw/SouthGermanCredit.asc`
2. **Transform:** Mapeo de códigos a categorías, creación de columnas decodificadas
3. **Load:** Guardado en `data/processed/south_german_credit_processed.csv` (y `.parquet`)

### 5.2. Propuesta DW/Data Mart
**Documento:** `docs/analisis/propuesta_dw_datamart.md`  
**Esquema SQL:** `sql/schema_dw.sql`

**Modelo estrella propuesto:**
- **Dimensiones:** `dim_cliente`, `dim_cuenta`, `dim_hist_credito`, `dim_proposito`, `dim_bien`, `dim_planes`, `dim_deudor`, `dim_vivienda`
- **Hechos:** `fact_credito` (duración, monto, tasa_cuota, tiempo_residencia, num_creditos, riesgo)
- **Data Mart:** Vista `dm_riesgo_crediticio` con indicadores derivados (ej. cuota aproximada mensual = monto/duración)

**Justificación:** Optimiza consultas analíticas para dashboard/BI, permite segmentación por perfil y facilita análisis de riesgo.

## 6. Modelado - Regresión y Clasificación
**Notebooks:** `notebooks/03_regresion.ipynb`, `notebooks/04_clasificacion.ipynb`  
**Resumen:** `docs/modelos/resumen_regresion_clasificacion.md`

### 6.1. Regresión (predecir monto `amount`)
**Enfoque:** ¿Es posible estimar el monto del crédito a partir de las demás características?

**Features:** `laufzeit`, `alter`, + variables categóricas decodificadas  
**Metodología:** One-hot encoding, split train/test, regresión lineal por mínimos cuadrados (implementación manual por restricciones de entorno)

**Resultados:**
- MAE: 1538.27 DM
- RMSE: 2025.97 DM
- R²: 0.574
- Modelo: `modelos/regresion/regresion_linear_manual_amount.pkl`

**Conclusión:** Explica ~57% de la variabilidad. Duración del crédito (`laufzeit`) es un predictor importante.

### 6.2. Clasificación (predecir riesgo crediticio)
**Enfoque:** ¿Es posible clasificar un crédito como good/bad?

**Consideraciones:** Desbalance 700/300. Se usa split estratificado.  
**Metodología:** Regresión logística con gradiente descendente (implementación manual)

**Resultados:**
- Accuracy: 0.700
- Precision: 0.700
- Recall: 1.000
- F1: 0.824
- ROC-AUC: 0.500
- Confusión: TN=0, FP=60, FN=0, TP=140

**Conclusión:** En esta implementación manual el modelo muestra sesgo hacia la clase mayoritaria debido a configuración; se evidencia la necesidad de técnicas para desbalance (SMOTE, class_weight, ajuste de umbral) - tema a profundizar.

## 7. Gestión del proyecto y trazabilidad
- **Repositorio Git:** Commits realizados con avance (diccionario, ETL, DW, modelos)
- **Documentación:** Organizada en `docs/` (planeacion, diccionario_datos, analisis, modelos, resultados)
- **Notebooks:** Numerados por fase (01-04)
- **Modelos guardados:** `modelos/regresion/`, `modelos/clasificacion/`
- **README actualizado:** Estado, avance, cronograma con seguimiento, instrucciones de reproducción

## 8. Limitaciones
- **Entorno:** Bloqueo de App Control impidió usar scipy/scikit-learn con extensiones nativas; se implementaron algoritmos manualmente con numpy/pandas
- **Datos históricos:** 1973-1975, no representativos de contexto actual
- **Desbalance:** Sobrerrepresentación de buenos créditos
- **Codificación compleja:** Algunas variables combinadas (ej. sexo/estado civil)
- **Fines académicos:** Modelos no aptos para decisiones crediticias reales

## 9. Próximos pasos
- Clustering (K-means) y PCA para segmentación de clientes
- Técnicas para desbalance (class_weight, SMOTE)
- Optimización de hiperparámetros
- Dashboard (Streamlit/Power BI) para visualización
- Evaluación integral con métricas robustas

**Archivos clave generados hasta el momento:**
- Diccionario: `docs/diccionario_datos/diccionario_datos.md`
- ETL: `src/etl/etl_south_german_credit.py`
- Datos procesados: `data/processed/south_german_credit_processed.csv`
- DW/DM: `docs/analisis/propuesta_dw_datamart.md`, `sql/schema_dw.sql`
- Notebooks: `notebooks/01_exploracion.ipynb` ... `04_clasificacion.ipynb`
- Modelos: `modelos/regresion/`, `modelos/clasificacion/`
- Resumen: `docs/modelos/resumen_regresion_clasificacion.md`
- README actualizado
