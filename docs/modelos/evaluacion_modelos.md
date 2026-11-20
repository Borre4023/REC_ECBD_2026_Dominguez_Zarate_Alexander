# Evaluación de modelos supervisados — Unidad III

**Proyecto:** Análisis de riesgo crediticio — South German Credit (UTTT)
**Alumno:** Alexander Domínguez Zárate · Matrícula 23301324
**Fecha:** 2026-11-16 · **Fase 3**
**Scripts:** `src/models/entrenar_regresion.py` · `src/models/entrenar_clasificacion.py`
**Notebooks:** `notebooks/03_regresion.ipynb` · `notebooks/04_clasificacion.ipynb`
**Artefactos:** `modelos/regresion/` · `modelos/clasificacion/` (`.pkl` + `metricas.json`)

---

## 1. Diseño experimental común

| Aspecto | Regresión | Clasificación |
|---|---|---|
| Objetivo | `hoehe` (monto, DM 1994) | `kredit` (0 = bad, clase positiva) |
| Split | 80/20 (`random_state=42`) | 80/20 estratificado |
| Validación | KFold 5, shuffle | StratifiedKFold 5 |
| Preprocesamiento | OneHot (categóricas) + StandardScaler (numéricas) | idéntico |
| Baseline | DummyRegressor (mediana) | DummyClassifier (mayoritaria) |

**Prevención de fuga de información (leakage).** En ambos problemas se excluyen
`kredit`, `kredit_cat` (resultado posterior al contrato) y `cuota_aprox_mensual`
(función determinista de `hoehe/laufzeit`). En clasificación, además, el umbral de
decisión se ajusta **solo con train** (`cross_val_predict` out-of-fold).

Dataset fuente: `data/processed/south_german_credit_processed.csv` (1000 × 40, contrato
de calidad 7/7 OK de la Fase 1).

## 2. Regresión del monto (`hoehe`)

### 2.1 Comparación por CV 5-fold (train, 800 créditos)

| Modelo | RMSE (DM) | MAE (DM) | R² |
|---|---:|---:|---:|
| **RidgeCV** (α interno) | **1887.1 ± 217.0** | **1317.6** | **0.550** |
| Ridge α=1 | 1902.5 | 1356.3 | 0.543 |
| OLS | 1909.0 | 1361.7 | 0.540 |
| Baseline (mediana) | 2974.7 | 1916.8 | −0.121 |

**Lectura:** los tres modelos lineales empatan dentro del error (±0.01 R²): el techo
lo pone la información disponible, no la complejidad. El baseline con R² negativo
confirma que las features aportan señal real. Gana `ridge_cv` (α seleccionado = 31.62,
regularización moderada que estabiliza las ~60 dummies).

### 2.2 Evaluación en test (200 créditos nunca vistos)

| Métrica | Valor | Lectura |
|---|---:|---|
| R² | **0.596** | explica ≈ 60 % de la varianza del monto |
| RMSE | **1798 DM** | error típico vs. monto medio de 3271 DM (≈ 55 %) |
| MAE | **1139 DM** | < RMSE ⇒ errores grandes concentrados en pocos casos |

### 2.3 Coeficientes estandarizados (top)

| Variable | Efecto (DM) | Lectura de negocio |
|---|---:|---|
| `laufzeit` (por σ) | +1488 | el plazo es el gran determinante del monto |
| `rate_cat_lt20` | −1043 | cuota ligera ⇒ créditos grandes de plazo largo |
| `rate_cat_ge35` | +925 | cuota pesada ⇒ créditos chicos de plazo corto |
| `beruf_high_qual_selfemp` | +725 | perfil calificado pide más |
| `verw_business` / `verw_car_new` | +615 / +538 | propósitos de monto alto (Q2 del DW) |
| `moral_delay` | +397 | el segmento con atrasos pide montos mayores |

Diagnóstico (`docs/modelos/figuras/reg_pred_vs_real.png`, `reg_residuos.png`): buen
ajuste en 2000–6000 DM con **saturación en los extremos** (predice máximos ≈ 8000 DM
cuando existen créditos de 18000+). Recomendación: usar el modelo por rango y tratar
la exposición extrema con reglas aparte (Data Mart Q4: el top-10 de cuota tiene 40 % bad).

**Veredicto:** modelo útil para *presupuestar exposición agregada*, no para fijar
montos individuales.

## 3. Clasificación del riesgo (`kredit`)

### 3.1 Comparación por CV estratificada 5-fold (train)

| Modelo | ROC-AUC | F1 (bad) |
|---|---:|---:|
| **Logística balanceada C=0.1** | **0.772 ± 0.044** | **0.597** |
| RandomForest 300 árboles balanceado | 0.771 ± 0.033 | 0.552 |
| Logística balanceada C=1.0 | 0.763 ± 0.036 | 0.565 |
| Baseline (mayoritaria) | 0.500 | 0.000* |

F1 (bad) con umbral 0.5 y clase positiva = bad (`make_scorer(f1_score, pos_label=0)`).
\* El baseline predice todo "good": nunca detecta un bad (F1 = 0) y su AUC 0.50 = azar.
Su accuracy (0.70) parecería aceptable, por eso no se usa como criterio.

**Lectura:** los tres modelos reales empatan (AUC ≈ 0.77): con 800 filas y variables
mayormente ordinales, la parsimonia de la logística regularizada basta y el ensemble
no aporta. El F1 de bad confirma el orden: la logística C=0.1 lidera (0.597) y el
RandomForest queda último (0.552). Empata también con el hallazgo de la Unidad II (AUC manual 0.703) y lo
supera con holgura gracias al one-hot + balanceo + CV estratificada.

### 3.2 Umbral de decisión (ajustado solo en train)

Umbral óptimo por F1-bad: **0.49** (F1 out-of-fold = 0.599). Prácticamente el neutro:
el `class_weight='balanced'` ya compensa el desbalance 700/300 internamente.

### 3.3 Evaluación en test (umbral 0.49)

| Métrica | Valor | Lectura |
|---|---:|---|
| ROC-AUC | **0.835** | supera la meta (>0.70) y al modelo manual de U2 (0.703) |
| Accuracy | 0.725 | 72.5 %: solo 2.5 pp sobre el 70 % de predecir todo "good"; se reporta por completitud, no como criterio (depende de la prevalencia) |
| Recall bad | **0.767** | detecta 46 de los 60 bad del test |
| Precisión bad | 0.529 | 47 de cada 100 alertas son falsa alarma |
| F1 (bad) | 0.626 | balance recall/precisión |

Matriz de confusión (bad = positiva, `labels=[1,0]`):

|  | pred bad | pred good |
|---|---:|---:|
| **real bad** | 46 (TP) | 14 (FN) |
| **real good** | 41 (FP) | 99 (TN) |

**Lectura operativa:** el modelo filtra el **77 % de los morosos potenciales** a cambio
de marcar para revisión el 29 % de los buenos (41/140). En banca, escapa-un-bad cuesta
más que falsa-alarma-un-good, por lo que este punto de operación es defendible; el
umbral puede recalibrarse según el costo real de la cartera.

**Caveat de reporte:** AUC test (0.835) > AUC CV (0.772 ± 0.044). La partición de test
resultó favorable; el número conservador para reportar es el de CV (≈ 0.77).

### 3.4 Variables que explican el riesgo (logística, top)

| Variable | Importancia (\|coef\|) | Consonancia con el Data Mart |
|---|---:|---|
| `laufkont_ge200_or_salary` | 0.709 | Q3: 9.1 % bad en el mejor segmento de cuenta |
| `laufkont_no_checking` | 0.636 | Q3: 52.1 % bad sin cuenta corriente |
| `verw_car_new` | 0.543 | Q2: monto promedio alto (5370 DM) |
| `moral_all_bank_paid` | 0.518 | Q1: 17.1 % bad, historial limpio |
| `sparkont_unknown` | 0.466 | ahorros desconocidos = incertidumbre |
| `moral_critical` | 0.333 | Q1: 57.1 % bad, cuenta crítica |
| `laufzeit` (numérica) | 0.331 | plazos largos → más tiempo de exposición |

La coincidencia con las consultas Q1–Q3 del Data Mart valida que el modelo aprendió
señales de negocio reales y no artefactos del split.

## 4. Comparación entre los dos problemas

| | Regresión (`hoehe`) | Clasificación (`kredit`) |
|---|---|---|
| Mejor modelo | RidgeCV (α = 31.62) | Logística balanceada C=0.1 |
| Métrica principal | R² test **0.596** | ROC-AUC test **0.835** (CV 0.772) |
| vs. baseline | R² −0.12 → 0.60 | AUC 0.50 → 0.84 |
| Variables dominantes | plazo + estructura de cuota | cuenta + historial + ahorros |
| Uso recomendado | presupuesto de exposición | preselección de solicitantes |

Ambos comparten el patrón "los modelos lineales bastan": las relaciones en los datos
son mayormente monotónicas y aditivas, y con n=1000 la regularización evita el sobreajuste.

## 5. Limitaciones

1. **n = 1000** (800 train): intervalos amplios (±0.04 de AUC en CV); los extremos del
   monto quedan mal cubiertos.
2. **Época:** créditos de 1973–1975 en marcos alemanes (DM); el peso de las variables
   (p. ej. `gastarb`, `telef`) no es trasladable a carteras actuales sin re-entrenar.
3. **`hoehe` transformada:** es una transformación monótona no documentada del monto
   (no DM exactos); las unidades absolutas de la regresión son orientativas.
4. **Umbral y costos:** el punto de operación (umbral 0.49) asume costes simétricos de
   FP/FN; en la práctica el banco debería calibrarlo con su matriz de costos real.
5. **Selección de variables:** no se hizo ingeniería de features más allá del one-hot;
   interacciones (p. ej. cuenta × historial) podrían subir el techo predictivo.

## 6. Reproducibilidad

```bash
py src/models/entrenar_regresion.py        # pkl + metricas.json + 2 figuras
py src/models/entrenar_clasificacion.py    # pkl + metricas.json + 2 figuras
```

Versión didáctica paso a paso (reutiliza las funciones de los scripts):
`notebooks/03_regresion.ipynb` y `notebooks/04_clasificacion.ipynb` (ejecutados
secuencialmente, 0 errores).

**Siguiente fase:** Unidad IV — clustering y PCA sobre el mismo dataset procesado.
