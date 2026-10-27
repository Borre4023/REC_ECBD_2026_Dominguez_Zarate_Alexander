# Propuesta de Data Warehouse / Data Mart

## Enfoque
Modelo estrella (star schema) apropiado para análisis OLAP: hechos de crédito con dimensiones de cliente, tiempo (implícita), propósito, cuenta/ahorros, empleo, vivienda, etc.

## Esquema propuesto

### Dimensiones
- dim_cliente (sk_cliente PK, edad, estado_civil_sexo, personas_a_cargo, telefono, trabajador_extranjero, empleo, antiguedad_empleo, vivienda)
- dim_cuenta (sk_cuenta PK, estado_cuenta, ahorros)
- dim_credito_hist (sk_hist PK, historial_crediticio)
- dim_proposito (sk_proposito PK, proposito)
- dim_bien (sk_bien PK, propiedad)
- dim_plan (sk_plan PK, otros_planes_cuota)
- dim_deudor (sk_deudor PK, otros_deudores/aval)
- dim_trabajo (sk_trabajo PK, calidad_empleo)

### Tabla de hechos
- fact_credito (sk_credito PK, sk_cliente FK, sk_cuenta FK, sk_hist FK, sk_proposito FK, sk_bien FK, sk_plan FK, sk_deudor FK, sk_trabajo FK, fecha_solicitud (opcional), duracion_meses, monto_dm, tasa_cuota, tiempo_residencia, num_creditos_banco, riesgo_credito (0/1), riesgo_credito_cat (bad/good), monto_cuota_aprox)

## Data Mart sugerido
**dm_riesgo_crediticio**: vista/materialización para dashboard con variables clave, indicadores (ratio monto/duración), banderas y dimensión de riesgo.

## Justificación
- Desnormalización para rendimiento en BI
- Separación por dimensiones facilita filtrado
- Soporta análisis por segmentos (vivienda, empleo, propósito) y objetivo de clasificación/regresión
