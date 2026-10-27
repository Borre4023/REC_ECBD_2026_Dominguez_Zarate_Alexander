# ETL - South German Credit

## Objetivo
Documentar el proceso ETL: Extracción, Transformación, Carga hacia Data Warehouse/Data Mart.

## Extracción
- Origen: `data/raw/SouthGermanCredit.asc` (separado por espacios)
- Archivos complementarios: `codetable.txt`, `read_SouthGermanCredit.R`

## Transformación
1. **Carga**: Leer con pandas, validar shape (1000x21)
2. **Decodificación**: Mapear códigos a etiquetas legibles según `codetable.txt`
3. **Tipificación**: Identificar numéricas (duration, amount, age), categóricas/ordinales/binarías
4. **Normalización**: Generar variables categoricas decodificadas (`*_cat`)
5. **Calidad**: Sin nulos reportados. Validar rangos básicos
6. **Derivadas (opcional)**: `cuota_aprox_mensual = amount / duration`

## Carga
- **Staging/Processed**: `data/processed/south_german_credit_processed.csv` y `.parquet`
- **DW**: Carga a esquema estrella (dimensiones + fact_credito) via SQL/ETL script
- **Data Mart**: Vista `dm_riesgo_crediticio` para consumo en dashboard/analítica

## Script ETL (referencia)
Ver `src/etl/etl_south_german_credit.py` (a crear)
