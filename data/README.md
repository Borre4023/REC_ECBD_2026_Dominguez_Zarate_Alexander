# Datos — South German Credit

Este proyecto separa estrictamente los **datos originales** de los **datos generados**.
Nada en `raw/` se modifica nunca; todo lo que hay en `processed/` se puede regenerar
con los scripts del pipeline.

## `raw/` — Dataset original (inmutable)

| Archivo | Contenido |
|---|---|
| `SouthGermanCredit.asc` | Dataset original de UCI (id 573): 1 000 créditos, 21 variables codificadas en enteros, separadas por espacios |
| `codetable.txt` | Catálogo oficial de códigos de las 17 variables categóricas/ordinales/binarias |
| `read_SouthGermanCredit.R` | Código oficial de lectura (referencia de la decodificación) |

Fuente: *South German Credit* [Dataset]. (2020). UCI Machine Learning Repository.
https://doi.org/10.24432/C5QG88 (licencia CC BY 4.0). **No editar estos archivos.**

## `processed/` — Dataset y artefactos generados (regenerables)

| Archivo | Generado por | Contenido |
|---|---|---|
| `south_german_credit_processed.csv` | `py src/etl/etl_south_german_credit.py` | 1 000 × 40: 21 crudas + 17 `*_cat` decodificadas + `kredit_cat` + `cuota_aprox_mensual` |
| `south_german_credit_processed.parquet` | idem | Misma tabla en formato columnar |
| `reporte_calidad_etl.json` | idem | Contrato de calidad post-ETL (7 chequeos) |
| `dw_south_german_credit.db` | `py src/etl/build_dw_sqlite.py` | Data Mart SQLite: 8 dimensiones + `fact_credito` (1 000) + vista `dm_riesgo_crediticio` |
| `dm_consultas_resultados.json` | ejecución de `sql/queries_dm.sql` | Resultados de las 5 consultas analíticas |

## Cómo regenerar

```bash
py src/etl/etl_south_german_credit.py    # regenera el dataset procesado + reporte
py src/etl/build_dw_sqlite.py            # reconstruye el Data Mart desde el dataset procesado
```

Ver también `sql/schema_dw_sqlite.sql` (DDL) y `docs/analisis/etl_documentacion.md` (documentación completa del ETL).
