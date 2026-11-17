# Clustering y PCA — Unidad IV

**Proyecto:** Análisis de riesgo crediticio — South German Credit (UTTT)
**Alumno:** Alexander Domínguez Zárate · Matrícula 23301324
**Fecha:** 2026-11-16 · **Fase 4**
**Script:** `src/models/clustering_pca.py` · **Notebook:** `notebooks/05_clustering_pca.ipynb`
**Artefactos:** `modelos/clustering/kmeans_credit.pkl` + `metricas.json`

---

## 1. Objetivo y diseño

Segmentar los solicitantes **sin usar la respuesta** (`kredit`) y validar post-hoc si los
segmentos discriminan riesgo real. Es un análisis de conocimiento de negocio (KDD: fase de
minería no supervisada), no un predictor.

### 1.1 Selección de variables

De las 41 columnas del dataset procesado se retiene una matriz de entrada de **20
variables** que produce 71 columnas tras el one-hot:

- **Entran 3 numéricas** — `laufzeit` (plazo), `hoehe` (monto), `alter` (edad) —
  **estandarizadas** con StandardScaler: sin escalado, K-means usaría el monto (miles de
  DM) para dominar la distancia frente a la edad (decenas de años).
- **Entran las 17 categóricas/ordinales/binarias como dummies one-hot**: en un algoritmo
  basado en distancias euclidianas, codificar las categorías con enteros impondría órdenes
  falsos (p. ej. `moral = 4` "no estaría más cerca de" `moral = 3` que de `moral = 0`).
  Las dummies tratan cada categoría como presencia/ausencia.
- **Se excluyen `kredit` y `kredit_cat`**: el clustering no debe ver la respuesta; la
  validación del perfil por % bad (§ 4) solo tiene valor si la respuesta quedó fuera.
- **Se excluye `cuota_aprox_mensual`**: es una función determinista de `hoehe/laufzeit`,
  así que duplicaría esas dos variables triplicando su peso efectivo en la distancia.

| Decisión | Justificación |
|---|---|
| Excluir `kredit`, `kredit_cat` | el clustering no debe ver la respuesta (evita circularidad) |
| Excluir `cuota_aprox_mensual` | duplica `hoehe`/`laufzeit` |
| 3 numéricas estandarizadas + 17 `*_cat` one-hot | trata el espacio nominal sin ordenar categorías |
| `random_state=42`, `n_init=10` | reproducibilidad de K-means |

Matriz resultante: **1000 × 71** (71 columnas por las ~58 dummies).

## 2. PCA — estructura de varianza

| Métrica | Valor |
|---|---|
| Componentes totales | 70 |
| Varianza PC1 / PC2 / PC3 | 15.0 % / 10.3 % / 5.7 % |
| Componentes para 80 % | **23** |
| Componentes para 90 % | **31** |

**Lectura:** la varianza está muy repartida — no existe un "eje del riesgo" único. El
comportamiento es el esperado con muchas dummies casi independientes. Lo relevante es el
**contenido de PC1**: loadings dominantes `hoehe` (0.674) y `laufzeit` (0.643), ambos
positivos ⇒ **PC1 es el eje de exposición** (créditos grandes y largos vs. chicos y cortos).

Figura: `docs/modelos/figuras/pca_varianza.png` (scree + acumulada con marcas de 80/90 %).

## 3. Selección de k (codo + silhouette)

| k | Inercia | Silhouette |
|---:|---:|---:|
| **2** | 10 728 | **0.131** |
| 3 | 10 013 | 0.086 |
| 4 | 9 644 | 0.070 |
| 5 | 9 407 | 0.062 |
| 6 | 9 206 | 0.053 |
| 7 | 9 028 | 0.055 |
| 8 | 8 876 | 0.054 |

**Lectura:** silhouette máximo en **k=2** con caída monótona después; el codo también se
dobla en k≈2–3. Un silhouette de 0.13 es **bajo en absoluto**: en un espacio de 71
dimensiones con dummies, los grupos se solapan. La partición binaria no describe "islas"
sino el **gradiente principal** de los datos.

Figura: `docs/modelos/figuras/kmeans_seleccion_k.png` (inercia + silhouette vs. k).

## 4. Perfil de los clústeres (k=2)

| | Clúster 0 — exposición alta | Clúster 1 — exposición baja |
|---|---:|---:|
| Tamaño | 254 (25.4 %) | 746 (74.6 %) |
| Monto medio | **6 895 DM** | 2 037 DM |
| Plazo medio | **36.0 meses** | 15.8 meses |
| Edad media | 36.4 | 35.2 |
| % bad (real) | **43.7 %** | 25.3 % |

**Validación post-hoc (clave):** el clustering nunca vio `kredit`, y aun así el segmento
de alta exposición **casi triplica** el riesgo del de baja (43.7 % vs. 25.3 %; base 30 %).
La exposición — no la demografía — es la variable maestra. Converge con:

- **Q5 del Data Mart:** ≥ 8000 DM → 54.3 % bad.
- **Q4 del Data Mart:** top-10 de cuota mensual con 40 % bad.
- **Regresión (U3):** saturación/subestimación en montos altos.

Figuras: `pca_clusters.png` (separación por PC1 con solape en la frontera) y
`clu_perfil_bad.png` (riesgo real por clúster vs. línea base 30 %).

## 5. Categorías distintivas (desvío de dummies vs. global)

| Clúster 0 (exposición alta) | desvío | Clúster 1 (exposición baja) | desvío |
|---|---:|---|---:|
| `telef_yes` | +0.20 | `telef_no` | +0.07 |
| `beruf_high_qual_selfemp` | +0.16 | `verm_unknown` | +0.06 |
| `verm_real_estate` | +0.15 | `beruf_unskilled_resident` | +0.04 |
| `famges_male_married_widowed` | +0.13 | `moral_no_credits_or_paid` | +0.04 |
| `verw_car_new` | +0.13 | `rate_lt20` | +0.03 |

**Lectura de negocio:** el segmento de mayor riesgo no es el cliente "marginal" sino el
**cliente solvente sobreexpuesto**: empleo calificado o cuenta propia, inmueble en propiedad,
teléfono registrado y auto nuevo — pidiendo montos grandes a plazos largos. El clúster bajo
concentra perfiles con menos patrimonio documentado y créditos pequeños/cortos.

## 6. Uso recomendado y limitaciones

**Uso:** segmentación gerencial en dos políticas diferenciadas — límites y revisión
reforzada para créditos grandes/largos (regla simple: monto × plazo), tarifas y flujo
ágil para el resto. Es la contraparte no supervisada de las reglas del dashboard (Fase 5).

**Limitaciones:**

1. **Silhouette bajo (0.131):** los clústeres se solapan; no identificar clientes de forma
   rígida, usar como tasa/régimen.
2. **k=2 domina por las numéricas:** `hoehe` y `laufzeit` estandarizadas concentran la
   separación; un clustering con re-ponderación de bloques (numéricas vs. dummies) podría
   revelar otros cortes (p. ej. por cuenta/historial).
3. **K-means asume clústeres esféricos:** con dummies, la geometría real es distinta;
   alternativas (GMM, K-prototypes) podrían matizar el resultado.
4. **Época y muestra:** 1973–1975, n=1000; los perfiles (teléfono, trabajador extranjero)
   envejecieron mal para uso literal.

## 7. Reproducibilidad

```bash
py src/models/clustering_pca.py      # pkl + metricas.json + 4 figuras
```

Versión didáctica: `notebooks/05_clustering_pca.ipynb` (ejecutado secuencial, 0 errores).

**Siguiente fase:** dashboard HTML estático + README final (Fase 5).
