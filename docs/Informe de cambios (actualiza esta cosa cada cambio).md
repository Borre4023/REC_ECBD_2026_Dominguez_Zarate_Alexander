# Informe detallado del procedimiento - Proyecto South German Credit

**Alumno:** Alexander Domínguez Zárate  
**Matrícula:** 23301324  
**Materia:** Extracción de Conocimiento en Bases de Datos  
**Fecha:** 2026-10-27
**Última actualización:** 2026-11-20  

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
Se elaboró `docs/diccionario_datos/diccionario_datos_v2.md` con mapeo completo basado en `data/raw/codetable.txt` (la versión inicial se conserva como `diccionario_datos_v1.md`):
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
- Diccionario: `docs/diccionario_datos/diccionario_datos_v2.md`
- ETL: `src/etl/etl_south_german_credit.py`
- Datos procesados: `data/processed/south_german_credit_processed.csv`
- DW/DM: `docs/analisis/propuesta_dw_datamart.md`, `sql/schema_dw.sql`
- Notebooks: `notebooks/01_exploracion.ipynb` ... `04_clasificacion.ipynb`
- Modelos: `modelos/regresion/`, `modelos/clasificacion/`
- Resumen: `docs/modelos/resumen_regresion_clasificacion.md`
- README actualizado

## 10. Registro de cambios (bitácora)

> Apartado que registra cada actualización del proyecto a partir del 9 de noviembre de 2026.

### 2026-11-09 — Unidad II: exploración técnica

- **Diccionario de datos v2** (`docs/diccionario_datos/diccionario_datos_v2.md`): alineado a los 8 campos solicitados (nombre, descripción, tipo Python, tipo de variable, clasificación, unidad, utilidad); la versión anterior se conserva como evidencia en `diccionario_datos_v1.md`.
- **Informe de exploración técnica** (`docs/analisis/exploracion_tecnica.md` + versión HTML autocontenida `exploracion_tecnica.html`): 10 secciones — herramientas, carga con las 6 instrucciones Pandas interpretadas, diccionario, tipo/fuente de los datos, diagnóstico de calidad (nulos 0, duplicados 0, 7 inconsistencias de codificación), estadísticos de `laufzeit`/`hoehe`/`alter`, atípicos por IQR (70/72/23), 4 visualizaciones, propuestas de regresión/clasificación/clustering y las 10 preguntas de conclusión.
- **Figuras** (`docs/analisis/figuras/fig1..fig5.png`): histograma del monto, boxplots de las numéricas, barras de % good por historial, dispersión monto–plazo y matriz de correlación.
- **Scripts** (`src/preprocessing/`): `exploracion_tecnica.py` (estadísticos y generación de figuras) y `figuras_fuente.py` (fuente canónica de las figuras, con comentarios en los 7 puntos de traspaso Pandas → Matplotlib).
- **Documentación del código de las figuras** (`docs/analisis/codigo_fuente_figuras.md`): código completo por figura, lectura Pandas → Matplotlib y fichas de preservación con SHA-256. Verificado: regenerar las figuras produce PNG idénticos byte a byte.
- **Notebook** `notebooks/01_exploracion.ipynb` reescrito con enfoque didáctico: instrucción → salida → interpretación escrita.
- **README**: sección "Avance actual" reconstruida, cronograma con columna Estado, badge y rutas corregidos.
- **Limpieza**: eliminación de `.gitkeep` obsoletos (`data/processed/`, `modelos/`).
- **Commits:** `b750806` (diccionario v2), `f9f2e8d` (scripts), `658aac8` (figuras), `b650907` (código fuente de figuras), `457ca1a` (informe), `715fd2a` (notebook), `ce7f998` (README), `e740228` (limpieza).

### 2026-11-16 — Trazabilidad y repositorio

- **`.gitignore` agregado** (`0a2d081`): corrige la omisión del commit `e740228`, cuyo mensaje lo anunciaba pero no lo incluía. Ignora `__pycache__/`, `.ipynb_checkpoints/` y temporales de Office/OneDrive.
- **Referencias actualizadas al diccionario v2** en README, informe de exploración técnica y esta bitácora (el archivo pasó de `diccionario_datos.md` a `diccionario_datos_v2.md`).
- **Estructura de Carpetas.md** sincronizada con el árbol real del repositorio.
- **Estado de sincronización:** los commits del 9 nov ya estaban publicados en `origin/main`; los de esta fecha quedan locales a la espera de push.

### 2026-11-16 — Fase 1: ETL consolidado

- **`src/etl/etl_south_german_credit.py` mejorado:** función `validate()` con contrato de calidad de 7
  chequeos (filas conservadas, nulos, duplicados, códigos en catálogo, decodificación completa, consistencia
  de la derivada y rangos lógicos) + reporte auditable `data/processed/reporte_calidad_etl.json`.
- **Variable derivada** `cuota_aprox_mensual = hoehe / laufzeit` (media 167.69, mediana 130.33 DM/mes,
  máximo 2482.67 en crédito grande de plazo corto).
- **Dataset procesado regenerado:** 1000 × 40 (21 crudas + 18 `*_cat` + 1 derivada); CSV (205 KB),
  Parquet (45 KB) y reporte JSON.
- **`notebooks/02_preparacion_etl.ipynb` reescrito con enfoque didáctico** (19 celdas, 7 de código, 0
  errores, ejecución secuencial): reutiliza `MAPPINGS`/`validate()` del script ETL en lugar de duplicar
  lógica, e incluye interpretación escrita por apartado.
- **`docs/analisis/etl_documentacion.md` ampliada:** flujo, tabla de mapeos completa, validaciones,
  artefactos de carga y relación con las fases siguientes.
- **Cierre de Unidad II publicado:** commit `749d067` (notebook 01 reejecutado 1→16, 0 errores) y tag
  `v0.2-unidad2` en `origin`.

### 2026-11-16 — Fase 2: Data Mart implementado en SQLite

- **`sql/schema_dw_sqlite.sql`:** DDL adaptado del diseño PostgreSQL (`schema_dw.sql` se conserva como
  entrega teórica): 8 dimensiones, `fact_credito` con 8 FKs + índices, y vista `dm_riesgo_crediticio`
  con `cuota_aprox_mensual` recalculada en SQL.
- **`src/etl/build_dw_sqlite.py`:** carga el dataset procesado (Fase 1), desduplica las dimensiones
  (SCD tipo 0), resuelve surrogate keys y valida con `PRAGMA foreign_key_check`.
- **`data/processed/dw_south_german_credit.db`** (192 KB): `fact_credito` 1000 filas = dataset procesado;
  vista 1000 filas; sin violaciones FK; dimensiones: cliente 508, cuenta 20, historial 5, propósito 10,
  bien 4, planes 3, deudor 3, vivienda 3.
- **`sql/queries_dm.sql` + `dm_consultas_resultados.json`:** 5 consultas analíticas con resultados reales:
  historial de atraso 62.5 % bad vs. historial limpio 17.1 %; sin cuenta + sin ahorros 52.1 % bad;
  créditos ≥ 8000 DM 54.3 % bad; top-10 de exposición mensual con 40 % bad (2 de los 2 mayores son bad).
- **`docs/analisis/dw_datamart_implementacion.md`:** esquema, validaciones, resultados y lectura de
  negocio de cada consulta.

### 2026-11-16 — Fase 3: Unidad III (modelos supervisados con sklearn)

- **`src/models/entrenar_regresion.py`:** pipeline sklearn (OneHot + StandardScaler) con comparación
  KFold 5-fold de 4 candidatos (baseline mediana, OLS, Ridge α=1, RidgeCV). Ganó `ridge_cv`
  (α=31.62): CV R² 0.55, test **R² 0.596** / RMSE 1798 DM / MAE 1139 DM vs. monto medio 3271 DM.
  Coeficientes estandarizados interpretables (`laufzeit` +1488 DM/σ; cuotas ligeras −1043; business
  +615). Excluye leakage: `kredit`, `kredit_cat`, `cuota_aprox_mensual`.
- **`src/models/entrenar_clasificacion.py`:** clase positiva = bad, `class_weight='balanced'`,
  CV estratificada 5-fold por ROC-AUC (baseline, logística C=1/C=0.1, RandomForest 300). Ganó la
  logística C=0.1: CV AUC **0.772±0.044**, test **AUC 0.835** (meta >0.70 superada; U2 manual 0.703).
  Umbral óptimo por F1-bad ajustado solo en train (0.49): recall bad 0.767 (46/60), precisión 0.529.
  Matriz de confusión con bad primero (`labels=[1,0]`).
- **`docs/modelos/figuras/`:** `reg_pred_vs_real.png`, `reg_residuos.png`, `roc_curvas.png` (AUC por
  modelo), `matriz_confusion.png`.
- **Artefactos:** `modelos/regresion/ridge_amount.pkl` + `metricas.json`; `modelos/clasificacion/
  mejor_riesgo.pkl` + `metricas.json` (los .pkl manuales antiguos se conservan como evidencia histórica).
- **`notebooks/03_regresion.ipynb` y `04_clasificacion.ipynb` reescritos didácticos** (21 y 24 celdas;
  8 y 9 de código; 0 errores; ejecución secuencial): reutilizan las funciones de los scripts vía
  `sys.path` y documentan la interpretación de cada apartado (comparación CV, test, coeficientes/
  importancias, diagnóstico gráfico, reproducibilidad end-to-end).
- **`docs/modelos/evaluacion_modelos.md`:** diseño experimental, tablas de métricas reales,
  lectura operativa de la matriz de confusión, comparación entre problemas, 5 limitaciones y
  reproducibilidad.
- **Consistencia con el Data Mart:** las variables dominantes del clasificador (`laufkont`, `moral`,
  `sparkont`) coinciden con los gradientes de riesgo de las consultas Q1/Q3; la regresión reproduce
  la relación monto-cuota-plazo y el patrón no lineal de Q5.

### 2026-11-16 — Fase 4: Unidad IV (clustering y PCA)

- **`src/models/clustering_pca.py`:** segmentación no supervisada sin ver la respuesta (excluye
  `kredit`, `kredit_cat`, `cuota_aprox_mensual`); matriz 1000×71 (3 numéricas estandarizadas +
  17 `*_cat` one-hot); PCA completo, K-means k=2..8 con codo + silhouette y perfil de clústeres
  con validación post-hoc del % bad.
- **PCA:** varianza muy repartida (PC1 = 15 %); 23 componentes para 80 %, 31 para 90 %. PC1 es el
  **eje de exposición**: loadings `hoehe` 0.674 y `laufzeit` 0.643.
- **Clustering:** mejor k = **2** (silhouette 0.131, bajo en absoluto = solape esperado con dummies):
  clúster 0 "exposición alta" (254 clientes, monto medio 6895 DM, plazo 36 meses, **43.7 % bad**) vs.
  clúster 1 "exposición baja" (746, 2037 DM, 16 meses, 25.3 % bad). Validación post-hoc: sin ver
  `kredit`, los segmentos casi triplican el gradiente de riesgo (base 30 %).
- **Perfil cualitativo:** el segmento riesgoso es el *cliente solvente sobreexpuesto*
  (`telef_yes` +0.20, `beruf_high_qual_selfemp` +0.16, `verm_real_estate` +0.15, `verw_car_new` +0.13),
  no el marginal.
- **Figuras:** `pca_varianza.png`, `kmeans_seleccion_k.png`, `pca_clusters.png`, `clu_perfil_bad.png`.
- **Artefactos:** `modelos/clustering/kmeans_credit.pkl` (preprocesador + kmeans + pca) + `metricas.json`.
- **`notebooks/05_clustering_pca.ipynb` didáctico** (23 celdas, 9 de código, 0 errores, secuencial):
  reutiliza el script y documenta interpretación de cada apartado.
- **`docs/modelos/clustering_pca.md`:** diseño, tablas reales de PCA/silhouette/perfiles, lectura de
  negocio, uso recomendado (2 políticas por exposición) y 4 limitaciones.

### 2026-11-16 — Fase 5: dashboard y cierre del proyecto

- **`src/dashboard/plantilla.html` + `src/dashboard/generar_dashboard.py`:** dashboard HTML estático
  **autocontenido** (jinja2 + matplotlib en base64): se abre en cualquier navegador sin servidor ni
  internet. Alimentado directamente por el Data Mart SQLite (`dw_south_german_credit.db`).
- **`dashboard/index.html`** (376 KB): 9 secciones — KPIs de cartera (1000 créditos, 30.0% bad,
  3 271 248 DM totales, cuota media 167.7 DM/mes); consultas Q1 (historial 62.5%→17.1% bad),
  Q3 (cuenta+ahorros, regla ×5.7), Q5 (monto: patrón no lineal hasta 54.3%), Q2 (propósitos por
  monto/cuota), Q4 (top-10 exposición, 40% bad); resultados de la Unidad III (AUC 0.835, recall
  76.7%, R² 0.596 con figuras ROC/matriz incrustadas) y Unidad IV (tabla de segmentos + figuras
  PCA/perfil); pipeline de reproducibilidad y limitaciones.
- **README.md actualizado para el cierre:** estado completado, avance con entregables reales por
  fase, cronograma cerrado, estructura de repositorio fiel, instrucciones de reproducción por
  pipeline (5 comandos), tabla de documentación y 4 hallazgos principales.
- **Bitácora:** esta entrada. Con esto se cierra el plan Fase 0→5.

### 2026-11-16 — Fase 6: cierre de la entrega final

- **Diagrama del Data Mart** (`src/etl/diagrama_dw.py` → `docs/analisis/figuras/diagrama_dw.png`):
  esquema estrella simple (8 dimensiones desduplicadas → `fact_credito` → vista
  `dm_riesgo_crediticio`) con conteos de filas leídos en vivo de la base SQLite; incrustado
  como Figura 1 en `docs/analisis/dw_datamart_implementacion.md`.
- **Capturas del dashboard** (`src/dashboard/capturar_dashboard.py` → `docs/resultados/capturas/`):
  4 imágenes por sección (01_panorama, 02_riesgo, 03_exposicion, 04_modelos_segmentos) con
  Chrome headless (`--headless=new`) + recorte de bordes con Pillow; sin dependencias nuevas.
- **Corrección de datos en el dashboard:** el "mejor segmento" de Q3 tomaba la última fila del
  top-8 (24.4 %) en vez del segmento real "cuenta ≥ 200 + ahorros ≥ 1000" (9.1 %, regla ×5.7);
  `generar_dashboard.py` corregido para mostrar todas las combinaciones ≥ 10 créditos y regenerado
  (377 013 bytes). Capturas rehechas.
- **Informe final borrador** (`docs/resultados/informe_final_borrador.md` + `.html`, APA 7):
  resumen, marco teórico KDD/CRISP-DM, materiales y métodos, Unidades II–IV con figuras y
  tablas reales, dashboard con 4 capturas y cita del dashboard en GitHub, discusión integrada,
  limitaciones, conclusiones por objetivo, referencias (Fayyad, Groemping, Kimball, sklearn,
  UCI…) y 4 anexos; HTML autocontenido con pandoc (2.17 MB, 13 imágenes base64).
- **`data/README.md`:** separación raw/processed (inmutable vs. regenerable) y comandos de
  regeneración.
- **Material de defensa:** elaborado y mantenido fuera del repositorio (no se publica).
- **Pulido documental:** subsección 1.1 "Selección de variables" en `docs/modelos/clustering_pca.md`;
  nota histórica en `docs/modelos/resumen_regresion_clasificacion.md` (remitir a
  `evaluacion_modelos.md`); README con enlaces al informe, capturas, guía y diagrama.
- **Verificación final:** pipeline completo reejecutado en secuencia (ETL 7/7, DW 0 FK,
  R² 0.596, AUC 0.835, k=2) con cifras coincidentes con el informe.
- **Tag de cierre:** `v1.0-entrega-final` (creado tras el push).

### 2026-11-20 — Cierre de rúbrica: accuracy y recomendaciones de negocio

- **Auditoría contra la rúbrica oficial** (Unidades II–V): 26/28 viñetas ya cubiertas; se
  detectaron dos huecos: (a) la rúbrica pide **accuracy** explícitamente y solo se reportaban
  precision/recall/F1/matriz; (b) las recomendaciones estaban implícitas en la discusión.
- **`src/models/entrenar_clasificacion.py`:** se agrega `accuracy_test` a `metricas_test`
  (desde las predicciones con el umbral 0.49). Resultado: **0.725** (145/200), coherente con
  la matriz de confusión; el resto de métricas se mantiene idéntico (AUC 0.835, recall 0.767,
  F1 0.626).
- **`docs/modelos/evaluacion_modelos.md`:** fila de accuracy con lectura crítica (solo 2.5 pp
  sobre el 70 % del baseline trivial; métrica secundaria dependiente de la prevalencia).
- **Informe final:** accuracy en §2.2 (justificación de por qué no es criterio principal),
  Tabla 6 y Anexo D; nueva **§8.1 Recomendaciones de negocio** (control de exposición,
  semáforo cuenta+ahorros, punto de operación por costos, monitoreo/reentrenamiento);
  Captura 4 actualizada. HTML re-exportado (2.18 MB, 13 imágenes).
- **Dashboard:** nueva métrica "accuracy 72.5 % (no principal: base 70 %)" en la sección de
  modelos; dashboard regenerado (377 127 B) y captura 04 recapturada (1520×2930).
- **Entorno:** el Python 3.11 del sistema fue reemplazado por 3.15; un bloqueo transitorio de
  App Control impidió cargar scipy. Se instaló 3.11.9 vía `py install 3.11` como respaldo y
  se verificó que el pipeline corre tanto con `py` (3.15) como con `py -3.11`, con cifras
  idénticas.
- **Material de defensa:** se mantiene fuera del repositorio.

### 2026-11-20 — Dashboard alternativo en Power BI y limpieza del repositorio

- **`src/dashboard/exportar_powerbi.py`:** exporta 7 CSV a `powerbi/datos/` (vista plana del
  Data Mart, segmentos, PCA, selección de k, métricas y matriz de confusión) en UTF-8 con BOM
  y separador `;`.
- **`docs/resultados/guia_powerbi.md`:** guía de construcción del `.pbix` (importación, DAX,
  4 páginas, estilo y checklist). La columna `Rango Monto` usa los mismos cortes que Q5
  (1 500 / 4 000 / 8 000 DM) para reproducir 28.8 → 23.9 → 38.1 → 54.3 % bad.
- **Segmentos por monto medio:** `generar_dashboard.py` y `exportar_powerbi.py` ya no asumen
  que el clúster 0 es el de exposición alta; lo deciden por el monto medio de cada clúster.
- **Limpieza:** los scripts de la fase manual pre-sklearn (`run_*.py`,
  `test_modelos_manual.py`, `update_docs.py`) se movieron a `legacy/`.
- **README:** cronograma aclarado (modelos rehechos con sklearn), Power BI y `legacy/` en la
  estructura; se retira la referencia al material de defensa.

### 2026-11-20 — Corrección del F1 de bad en la comparación por CV

- **Error:** en `comparar_cv` de `src/models/entrenar_clasificacion.py` el scorer `'f1'` de
  sklearn medía la etiqueta 1 (**good**), no bad (`kredit = 0`). Por eso el baseline
  mayoritario aparecía con "F1 bad" 0.824.
- **Corrección:** `make_scorer(f1_score, pos_label=0, zero_division=0)`. F1 de bad en CV
  (umbral 0.5): logística C=0.1 **0.597**, logística C=1 0.565, RandomForest 0.552,
  baseline 0.000 (antes 0.779 / 0.767 / 0.805 / 0.824).
- **Sin impacto en la selección ni en test:** el modelo se elige por ROC-AUC (simétrico) y las
  métricas de test ya usaban bad como positiva. AUC 0.835, accuracy 0.725, recall 0.767,
  F1 0.626, umbral 0.49 y figuras sin cambios. Con el F1 corregido la logística C=0.1
  también lidera por F1.
- **Actualizados:** `modelos/clasificacion/metricas.json`, notebook 04 (re-ejecutado, 0 errores;
  interpretación de §2 y §3 reescrita), `docs/modelos/evaluacion_modelos.md` §3.1, informe
  final Tabla 5 (+ HTML regenerado con pandoc) y `powerbi/datos/metricas_modelos.csv`.

### 2026-11-20 — Dashboard en Power BI terminado e integrado al informe

- **`powerbi/SouthGermanCredit.pbix`:** 4 páginas (panorama, ¿quién incumple?, ¿cuánta
  exposición?, modelos y segmentos) construidas en Power BI Desktop a partir de los CSV de
  `powerbi/datos/`. Las cifras de control coinciden con el dashboard HTML (1 000 créditos,
  30.0 % bad, 52.1 % vs 9.1 %, 28.8 → 23.9 → 38.1 → 54.3 %, AUC 0.835, 46/14/41/99, 254 vs 746).
- **Capturas:** `docs/resultados/capturas_powerbi/01–04`.
- **Guía:** `Orden Rango Monto` ahora se calcula con los cortes numéricos (comparar el texto de
  la etiqueta rompía el orden si un guion o espacio no coincidía) y `Créditos Bad` suma `+ 0`
  para que la matriz muestre 0 % en las combinaciones sin ningún bad.
- **Informe final:** nueva §7.5 "Dashboard alternativo en Power BI" (capturas 5–8) y
  entradas en los Anexos A, B y C; HTML regenerado con pandoc.
- **README:** Power BI marcado como completado; capturas y `.pbix` en la tabla de documentación.
