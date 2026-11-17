# Documentación del proceso ETL — South German Credit

**Proyecto:** Análisis de riesgo crediticio (Proyecto Integrador, UTTT)
**Alumno:** Alexander Domínguez Zárate · Matrícula 23301324
**Última actualización:** 2026-11-16 (Fase 1: validaciones, variable derivada y reporte de calidad)
**Script:** `src/etl/etl_south_german_credit.py` · **Notebook didáctico:** `notebooks/02_preparacion_etl.ipynb`

---

## 1. Objetivo

Documentar el proceso **E**xtracción, **T**ransformación y **C**arga (ETL) que convierte el archivo crudo
`SouthGermanCredit.asc` en el dataset procesado que alimenta los modelos supervisados (Unidad III), los
modelos no supervisados (Unidad IV) y el Data Warehouse/Data Mart.

## 2. Flujo general

```text
data/raw/SouthGermanCredit.asc        (1000 x 21, enteros codificados)
        │  Extract: pd.read_csv(sep=' ')
        ▼
DataFrame crudo ──── validate() ────▶ contrato de calidad (7 chequeos)
        │  Transform:
        │   • 18 mapeos codetable  →  columnas *_cat
        │   • cuota_aprox_mensual  =  hoehe / laufzeit
        ▼
DataFrame decodificado (1000 x 40)
        │  Load
        ▼
data/processed/south_german_credit_processed.csv       (205 KB)
data/processed/south_german_credit_processed.parquet   (45 KB)
data/processed/reporte_calidad_etl.json                (evidencia auditable)
```

## 3. Extracción

| Aspecto | Detalle |
|---|---|
| Origen | `data/raw/SouthGermanCredit.asc` (UCI id 573, CC BY 4.0) |
| Formato | Texto plano delimitado por **espacios**, sin encabezados decorativos |
| Shape esperado | `(1000, 21)` — 1000 créditos, 21 variables |
| Complementos | `codetable.txt` (catálogo de códigos), `read_SouthGermanCredit.R` (lectura oficial) |
| Particularidad | Datos 100 % codificados en enteros; la muestra está ordenada por la clase objetivo (no es serie temporal) |

## 4. Transformación

### 4.1 Decodificación `*_cat` (18 variables)

Se agregan columnas `*_cat` con las etiquetas de `codetable.txt`, **conservando** los códigos originales
(trazabilidad y compatibilidad con los notebooks 03–04). Fuente de verdad: diccionario `MAPPINGS` del script.

| Variable | Códigos → etiquetas |
|---|---|
| `laufkont` | 1 `no_checking` · 2 `lt0` · 3 `0_to_200` · 4 `ge200_or_salary` |
| `moral` | 0 `delay` · 1 `critical` · 2 `no_credits_or_paid` · 3 `existing_paid` · 4 `all_bank_paid` |
| `verw` | 0 `others` · 1 `car_new` · 2 `car_used` · 3 `furniture` · 4 `radio_tv` · 5 `appliances` · 6 `repairs` · 7 `education` · 8 `vacation` · 9 `retraining` · 10 `business` |
| `sparkont` | 1 `unknown` · 2 `lt100` · 3 `100_to_500` · 4 `500_to_1000` · 5 `ge1000` |
| `beszeit` | 1 `unemployed` · 2 `lt1` · 3 `1_to_4` · 4 `4_to_7` · 5 `ge7` |
| `rate` *(invertida)* | 1 `ge35` · 2 `25_to_35` · 3 `20_to_25` · 4 `lt20` |
| `famges` *(mezcla)* | 1 `male_divorced_sep` · 2 `female_nonsingle_or_male_single` · 3 `male_married_widowed` · 4 `female_single` |
| `buerge` | 1 `none` · 2 `coapplicant` · 3 `guarantor` |
| `wohnzeit` | 1 `lt1` · 2 `1_to_4` · 3 `4_to_7` · 4 `ge7` |
| `verm` | 1 `unknown` · 2 `car_other` · 3 `life_insurance` · 4 `real_estate` |
| `weitkred` | 1 `bank` · 2 `stores` · 3 `none` |
| `wohn` | 1 `free` · 2 `rent` · 3 `own` |
| `bishkred` | 1 `1` · 2 `2_3` · 3 `4_5` · 4 `ge6` |
| `beruf` | 1 `unskilled_nonresident` · 2 `unskilled_resident` · 3 `skilled_official` · 4 `high_qual_selfemp` |
| `pers` *(invertida)* | 1 `ge3` · 2 `0_to_2` |
| `telef` *(1 = no)* | 1 `no` · 2 `yes` |
| `gastarb` *(1 = sí)* | 1 `yes` · 2 `no` |
| `kredit` *(objetivo)* | 0 `bad` · 1 `good` |

**Notas de codificación** (ver U2, sección 5.3): `moral` inicia en 0; `rate` y `pers` son ordinales
**invertidas**; `telef` y `gastarb` usan direcciones opuestas; `verw = 7 (education)` existe en el catálogo
pero no en los datos (categoría vacía, sin registros); `famges` mezcla sexo y estado civil.

### 4.2 Variable derivada

| Variable | Fórmula | Estadísticos (1000 créditos) |
|---|---|---|
| `cuota_aprox_mensual` | `hoehe / laufzeit`, redondeo 2 decimales | media 167.69 · mediana 130.33 · Q1 89.33 · Q3 206.18 · min 24.06 · max 2482.67 |

Es un **proxy** de la carga mensual, no la cuota real del contrato (que depende de `rate`, el % del ingreso
disponible). La misma métrica se recalcula en SQL en la vista `dm_riesgo_crediticio`, lo que permite
validar la consistencia entre ETL y Data Warehouse.

## 5. Validaciones de calidad (contrato post-ETL)

La función `validate(df_raw, df_dec)` ejecuta 7 chequeos y produce el reporte JSON. Resultado de la última
ejecución: **7/7 OK**.

| # | Chequeo | Resultado | Riesgo que cubre |
|---|---|---|---|
| 1 | `filas_conservadas` | OK — 1000 = 1000 | Pérdida/duplicación de filas en el proceso |
| 2 | `sin_nulos` | OK — 0 | Faltantes introducidos por transformaciones |
| 3 | `sin_duplicados` | OK — 0 | Duplicados inducidos por `merge` o cargas dobles |
| 4 | `codigos_en_catalogo` | OK — ninguno fuera | Códigos inválidos no contemplados por `codetable.txt` |
| 5 | `decodificacion_completa` | OK — ninguna `*_cat` con `NaN` | Código nuevo sin mapeo (sustituye a la imputación) |
| 6 | `cuota_aprox_consistente` | OK — recálculo idéntico | Errores de redondeo/deriva en la derivada |
| 7 | `rangos_logicos_ok` | OK — plazo 1–120, monto > 0, edad 18–100 | Valores absurdos en cuantitativas |

Si una fase posterior rompe el contrato, `reporte_calidad_etl.json` indica exactamente qué cheque falló.

## 6. Carga

| Artefacto | Ruta | Tamaño | Uso principal |
|---|---|---|---|
| CSV | `data/processed/south_german_credit_processed.csv` | 205 409 bytes | Notebooks, carga a SQLite |
| Parquet | `data/processed/south_german_credit_processed.parquet` | 45 356 bytes | Recargas rápidas (columnar) |
| Reporte | `data/processed/reporte_calidad_etl.json` | 1 486 bytes | Auditoría de calidad |

Shape final: **1000 × 40** (21 crudas + 18 `*_cat` + 1 derivada).

## 7. Cómo reproducir

```bash
# desde la raíz del repositorio (rutas relativas a la raíz)
py src/etl/etl_south_german_credit.py

# versión didáctica paso a paso (rutas relativas a notebooks/)
jupyter notebook notebooks/02_preparacion_etl.ipynb
```

Salida esperada: los 3 archivos de `data/processed/` y la impresión de los 7 chequeos `OK`.

## 8. Relación con las siguientes fases

- **Data Warehouse/Data Mart (Fase 2):** las etiquetas `*_cat` alimentan las dimensiones; `fact_credito`
  toma `laufzeit`, `hoehe`, `rate`, `wohnzeit`, `bishkred` y `kredit`.
- **Unidad III (modelos supervisados):** `hoehe` como objetivo de regresión; `kredit`/`kredit_cat` como
  objetivo de clasificación.
- **Unidad IV (clustering/PCA):** numéricas + `*_cat` estandarizadas para segmentar clientes.
