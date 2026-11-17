# Implementación del Data Warehouse / Data Mart en SQLite

**Proyecto:** Análisis de riesgo crediticio — South German Credit (UTTT)
**Alumno:** Alexander Domínguez Zárate · Matrícula 23301324
**Fecha:** 2026-11-16 · **Fase 2**
**Diseño de origen:** `docs/analisis/propuesta_dw_datamart.md` + `sql/schema_dw.sql` (PostgreSQL)
**Implementación:** `sql/schema_dw_sqlite.sql` + `src/etl/build_dw_sqlite.py`
**Base generada:** `data/processed/dw_south_german_credit.db` (192 512 bytes)

---

## 1. Objetivo y decisión técnica

El diseño modelo-estrella se propuso en PostgreSQL (`schema_dw.sql`, dialecto con `SERIAL`/`::numeric`).
Para **implementarlo y validarlo** en este entorno (sin servidor de base de datos instalado), se adaptó a
**SQLite**, que está disponible en Python sin dependencias externas. El script PostgreSQL se conserva como
entrega teórica para un despliegue real; el DDL de SQLite mantiene la misma estructura lógica
(8 dimensiones + hechos + vista del Data Mart) con tipos equivalentes (`INTEGER PRIMARY KEY AUTOINCREMENT`).

## 2. Esquema implementado

```text
                        ┌────────────────────┐
  dim_cliente      (508)│                    │
  dim_cuenta        (20)│   fact_credito     │
  dim_hist_credito   (5)│       (1000)       │  ← 8 FKs, medidas de crédito
  dim_proposito     (10)│                    │     y resultado (riesgo)
  dim_bien           (4)│                    │
  dim_planes         (3)│                    │
  dim_deudor         (3)│                    │
  dim_vivienda       (3)│                    │
                        └─────────┬──────────┘
                                  ▼
                    dm_riesgo_crediticio (vista, 1000 filas)
                    + cuota_aprox_mensual recalculada en SQL
```

**Dimensiones** (con desduplicación SCD tipo 0 — cada combinación única de atributos es una fila):

| Dimensión | Atributos | Filas |
|---|---|---:|
| `dim_cliente` | edad, estado civil/sexo, personas a cargo, teléfono, trabajador extranjero, calidad de empleo | 508 |
| `dim_cuenta` | estado de cuenta corriente, ahorros | 20 |
| `dim_hist_credito` | historial crediticio | 5 |
| `dim_proposito` | propósito del crédito | 10 |
| `dim_bien` | bien más valioso | 4 |
| `dim_planes` | otros planes de cuotas | 3 |
| `dim_deudor` | otros deudores/aval | 3 |
| `dim_vivienda` | tipo de vivienda | 3 |

**`fact_credito`** (1000 filas = 1 fila por crédito, granularidad correcta): 8 FKs + medidas
`duracion_meses`, `monto_dm`, `tasa_cuota`, `tiempo_residencia`, `num_creditos_banco`, `riesgo_credito`
(0/1) y `riesgo_credito_cat` (bad/good). Índices en las 4 FKs más usadas.

**Vista `dm_riesgo_crediticio`**: desnormaliza el modelo estrella en una sola tabla plana para el
dashboard/BI, y recalcula `cuota_aprox_mensual = ROUND(monto_dm * 1.0 / duracion_meses, 2)` — el mismo
cálculo del ETL, servido desde SQL.

## 3. Carga y validaciones

El script `src/etl/build_dw_sqlite.py` lee el dataset procesado de la Fase 1 (1000 × 40), desduplica las
dimensiones, resuelve las surrogate keys y carga los hechos. Validaciones ejecutadas:

| Chequeo | Resultado |
|---|---|
| `fact_credito` = filas del dataset procesado | ✅ 1000 = 1000 |
| Vista `dm_riesgo_crediticio` sin pérdida | ✅ 1000 filas |
| `PRAGMA foreign_key_check` | ✅ Sin violaciones |
| FKs nulas en los hechos | ✅ 0 (todas las 8 FKs resueltas) |
| Dimensiones desduplicadas | ✅ `dim_cuenta` 20 = 4 estados × 5 ahorros, etc. |

Los conteos exactos quedan impresos por el script y en `data/processed/dm_consultas_resultados.json`.

## 4. Consultas analíticas (`sql/queries_dm.sql`)

Cinco preguntas de negocio respondidas contra el Data Mart (resultados reales de la ejecución):

### Q1. ¿Qué historial crediticio concentra el mayor riesgo?

| historial | créditos | bad | % bad |
|---|---:|---:|---:|
| delay (atraso) | 40 | 25 | **62.5** |
| critical (cuenta crítica) | 49 | 28 | **57.1** |
| no_credits_or_paid | 530 | 169 | 31.9 |
| existing_paid | 88 | 28 | 31.8 |
| all_bank_paid | 293 | 50 | **17.1** |

**Lectura:** gradiente de riesgo monotónico: de 62.5 % bad con historial de atraso a 17.1 % con historial
limpio en el banco. Confirma la señal vista en la fig. 3 de la Unidad II y anticipa la variable más
predictiva para la clasificación (Unidad III).

### Q2. ¿En qué propósitos se pide más dinero y mayor carga mensual?

| proposito | créditos | monto prom. | cuota prom. |
|---|---:|---:|---:|
| business | 12 | 8209 | 248.32 |
| car_new | 103 | 5370 | 216.40 |
| retraining | 97 | 4158 | 155.41 |
| repairs | 50 | 3180 | 150.24 |
| car_used | 181 | 3067 | 170.41 |
| others | 234 | 3063 | 196.72 |
| appliances | 22 | 2728 | 136.91 |
| furniture | 280 | 2488 | 134.61 |
| radio_tv | 12 | 1498 | 99.15 |
| vacation | 9 | 1206 | 117.90 |

**Lectura:** los créditos de **negocio** son los más grandes en promedio (8 209 DM) aunque poco frecuentes
(12); los de **mobilhome/furniture** son los más frecuentes (280) y pequeños. Interesante: `others` tiene
cuota promedio alta (196.72) pese a montos medianos — plazos cortos.

### Q3. ¿Cómo cambia el riesgo según la situación de la cuenta y los ahorros?

| estado_cuenta | ahorros | créditos | % bad |
|---|---|---:|---:|
| no_checking | unknown | 219 | **52.1** |
| lt0 (cuenta en rojo) | lt100 | 47 | 51.1 |
| no_checking | ge1000 | 29 | 48.3 |
| lt0 | unknown | 152 | 44.1 |
| 0_to_200 | 100_to_500 | 4 | 25.0 |
| lt0 | ge1000 | 45 | 15.6 |
| ge200_or_salary | unknown | 191 | 13.6 |
| ge200_or_salary | ge1000 | 99 | **9.1** |

**Lectura:** la combinación "sin cuenta corriente + sin ahorros conocidos" (52.1 % bad) multiplica ×5.7 el
riesgo de "cuenta ≥ 200 DM con salario + ahorros ≥ 1000" (9.1 %). Es el segmento de mayor riesgo del
dataset y candidato directo a regla de negocio en el dashboard.

### Q4. ¿Cuáles son los créditos de mayor exposición mensual? (top 10)

| sk_credito | monto | plazo | cuota/mes | historial | propósito | resultado |
|---:|---:|---:|---:|---|---|---|
| 978 | 14 896 | 6 | **2482.67** | no_credits_or_paid | others | **bad** |
| 755 | 14 555 | 6 | **2425.83** | no_credits_or_paid | others | **bad** |
| 197 | 6761 | 6 | 1126.83 | all_bank_paid | others | good |
| 537 | 3380 | 4 | 845.00 | all_bank_paid | others | good |
| 25 | 4716 | 6 | 786.00 | all_bank_paid | others | good |
| 835 | 4611 | 6 | 768.50 | no_credits_or_paid | car_used | **bad** |
| 453 | 7308 | 10 | 730.80 | no_credits_or_paid | others | good |
| 896 | 12 976 | 18 | 720.89 | no_credits_or_paid | car_new | **bad** |
| 260 | 3448 | 5 | 689.60 | all_bank_paid | others | good |
| 20 | 7228 | 11 | 657.09 | all_bank_paid | others | good |

**Lectura:** los dos créditos con mayor carga mensual (≈2 400–2 500 DM/mes) resultaron **bad**: la
exposición extrema y el incumplimiento coinciden. De los 10, 4 son bad (40 %), muy por encima del 30 %
base: la lista de top-exposición es en sí misma una cola de riesgo.

### Q5. ¿Cómo cambia el riesgo por rango de monto solicitado?

| rango de monto | créditos | monto prom. | bad | % bad |
|---|---:|---:|---:|---:|
| a. < 1500 DM | 306 | 1069 | 88 | 28.8 |
| b. 1500–3999 | 448 | 2568 | 107 | 23.9 |
| c. 4000–7999 | 176 | 5806 | 67 | 38.1 |
| d. ≥ 8000 | 70 | 11 025 | 38 | **54.3** |

**Lectura:** el riesgo cae primero (28.8 % → 23.9 %) y luego escala con el monto hasta **54.3 % bad** en
créditos ≥ 8000 DM. El patrón no es lineal: los créditos chicos fallan por perfil (cuenta/historial) y los
grandes por exposición. Ambos hallazgos alimentarán las reglas del dashboard.

## 5. Cómo reproducir

```bash
# 1) Dataset procesado (Fase 1)
py src/etl/etl_south_german_credit.py

# 2) Data Warehouse / Data Mart en SQLite
py src/etl/build_dw_sqlite.py

# 3) Consultas analíticas (requiere sqlite3 CLI) o desde Python:
sqlite3 data/processed/dw_south_german_credit.db < sql/queries_dm.sql
```

## 6. Relación con las siguientes fases

- **Unidad III:** el Data Mart es la fuente "limpia y desnormalizada" ideal para entrenar los modelos
  (regresión sobre `monto_dm`, clasificación sobre `riesgo_credito`).
- **Unidad IV:** los perfiles de cliente (dimensiones) son la base natural para el clustering.
- **Dashboard (Fase 5):** `dm_riesgo_crediticio` es la tabla plana de consumo; las consultas Q1–Q5 son los
  KPIs candidatos.
