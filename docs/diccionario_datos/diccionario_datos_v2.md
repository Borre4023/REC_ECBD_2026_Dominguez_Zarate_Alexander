# Diccionario de datos — South German Credit

**Fuente:** UCI Machine Learning Repository — South German Credit (dataset 573, CC BY 4.0)
**Versión:** 2.0 (alineada a la Unidad II; la v1 queda como registro de cambios en `diccionario_datos_v1.md`)
**Fecha:** 2026-11-09 · **Registros:** 1000 · **Variables:** 21 · Codificación de referencia: `data/raw/codetable.txt`

| Nombre de la variable | Descripción (qué representa) | Tipo de dato en Python | Tipo de variable | Clasificación | Unidad de medida | Posible utilidad en el proyecto |
|---|---|---|---|---|---|---|
| `laufkont` (status) | Estado de la cuenta corriente del deudor en el banco (1 sin cuenta; 2 < 0 DM; 3 de 0 a 200 DM; 4 ≥ 200 DM con salario ≥ 1 año) | int | Cualitativa | Ordinal | DM (intervalos de saldo) | Proxy de liquidez/capacidad de pago; candidata fuerte para clasificación y clustering |
| `laufzeit` (duration) | Duración del contrato de crédito | int | Cuantitativa | Discreta | meses | Correlaciona 0.625 con el monto (regresión); plazos largos se asocian a riesgo (clasificación) |
| `moral` (credit_history) | Historial de cumplimiento de créditos previos o concurrentes (0 retraso en el pasado; 1 cuenta crítica/otros bancos; 2 sin créditos o pagados al día; 3 existentes pagados al día; 4 todos los de este banco al día) | int | Cualitativa | Ordinal | — | La variable más discriminante del riesgo (fig. 8.2 del informe); núcleo de la clasificación |
| `verw` (purpose) | Propósito del crédito (0 otros; 1 auto nuevo; 2 auto usado; 3 muebles; 4 TV/radio; 5 electrodomésticos; 6 reparaciones; 7 educación; 8 vacaciones; 9 recualificación; 10 negocio). Nota: el código 7 no aparece en los datos | int | Cualitativa | Nominal | — | Segmentación de cartera; entrada One-Hot para modelos y dimensión `dim_proposito` del DW |
| `hoehe` (amount) | Monto del crédito; resultado de una transformación monótona del monto original (no documentada) | int | Cuantitativa | Discreta | DM (aproximado; transformado) | **Objetivo de regresión**; monto medio por cluster/servicio para el Data Mart |
| `sparkont` (savings) | Ahorros del deudor (1 desconocido/ sin cuenta; 2 < 100 DM; 3 de 100 a 500; 4 de 500 a 1000; 5 ≥ 1000) | int | Cualitativa | Ordinal | DM (intervalos) | Colchón financiero; clasificación y clustering de perfiles |
| `beszeit` (employment_duration) | Antigüedad con el empleador actual (1 desempleado; 2 < 1 año; 3 de 1 a 4; 4 de 4 a 7; 5 ≥ 7) | int | Cualitativa | Ordinal | años (intervalos) | Estabilidad laboral; clasificación y clustering |
| `rate` (installment_rate) | Cuota como porcentaje del ingreso disponible. **Codificación invertida**: 1 = ≥ 35 %; 2 = 25–35; 3 = 20–25; 4 = < 20 | int | Cualitativa | Ordinal (invertida) | % del ingreso | Carga financiera del hogar; clasificación. Verificar dirección antes de modelar |
| `famges` (personal_status_sex) | Estado civil y sexo combinados (1 varón divorciado/separado; 2 mujer no soltera o varón soltero; 3 varón casado/viudo; 4 mujer soltera). Limitación: el sexo no es recuperable por el código | int | Cualitativa | Nominal | — | Perfil demográfico para clustering; documentar limitación y uso ético |
| `buerge` (other_debtors) | Existencia de otro deudor o avalista (1 ninguno; 2 co-solicitante; 3 avalista) | int | Cualitativa | Nominal | — | Riesgo compartido/garantizado; clasificación |
| `wohnzeit` (present_residence) | Tiempo en la residencia actual (1 < 1 año; 2 de 1 a 4; 3 de 4 a 7; 4 ≥ 7) | int | Cualitativa | Ordinal | años (intervalos) | Estabilidad domiciliaria; clasificación |
| `verm` (property) | Bien más valioso del deudor (1 desconocido/sin propiedad; 2 auto u otro; 3 ahorro para vivienda/seguro de vida; 4 bienes raíces) | int | Cualitativa | Ordinal | — | Garantía implícita; clasificación y clustering; dimensión `dim_bien` |
| `alter` (age) | Edad del deudor | int | Cuantitativa | Discreta | años | Perfil demográfico; candidatos a outliers 65–75 (no eliminar); clustering |
| `weitkred` (other_installment_plans) | Planes de pago con acreedores distintos al banco (1 banco; 2 tiendas; 3 ninguno) | int | Cualitativa | Nominal | — | Indicador de sobreendeudamiento externo; clasificación |
| `wohn` (housing) | Tipo de vivienda (1 cedida/gratuita; 2 alquilada; 3 propia) | int | Cualitativa | Nominal | — | Clustering y Data Mart; dimensión `dim_vivienda` |
| `bishkred` (number_credits) | Número de créditos (incluido el actual) en este banco (1 uno; 2 dos-tres; 3 cuatro-cinco; 4 ≥ seis) | int | Cualitativa | Ordinal | créditos (intervalos) | Historial con la institución; clasificación |
| `beruf` (job) | Calidad del empleo (1 desempleado/no calificado – no residente; 2 no calificado – residente; 3 calificado/oficial; 4 directivo/autónomo/alta calificación) | int | Cualitativa | Ordinal | — | Perfil socioeconómico; clustering |
| `pers` (people_liable) | Personas Económicamente dependientes del deudor. **Codificación invertida**: 1 = "3 o más"; 2 = "0 a 2" | int | Cualitativa | Ordinal (invertida) | personas | Carga familiar; clasificación. Recodificar antes de modelar |
| `telef` (telephone) | Línea telefónica registrada a nombre del deudor (1 = no; 2 = sí). Dirección opuesta a `gastarb` | int | Cualitativa | Binaria | — | Variable histórica de trazabilidad (años 70); homogeneizar a 0/1 |
| `gastarb` (foreign_worker) | ¿Es trabajador extranjero? (1 = sí; 2 = no) | int | Cualitativa | Binaria | — | Atributo sensible: uso ético/académico y documentado; homogeneizar a 0/1 |
| `kredit` (credit_risk) | Resultado del contrato: ¿se cumplió? (0 = bad, no cumplido; 1 = good, cumplido). Muestra desbalanceada 700/300 por diseño | int | Cualitativa | Binaria (objetivo) | — | **Objetivo de clasificación**; métrica de validación de negocio por cluster |

## Notas globales

1. **18 de las 21 variables** (incluido el objetivo `kredit`) son categóricas codificadas: enteros que representan categorías; en la preparación se decodifican con `codetable.txt` y se agregan columnas `*_cat` legibles.
2. **Orden de inicio de códigos:** `moral` inicia en 0; el resto de las ordinales inicia en 1. Ignorar esto en una recodificación automática (p. ej. `LabelEncoder` implícito) causaría un desplazamiento silencioso de significados.
3. **Direcciones de binarias:** `telef` (1 = no) y `gastarb` (1 = sí) van en sentidos contrarios; previo a modelos lineales se homogeneizan a 0/1 con significado único "1 = sí".
4. **Ordinales invertidas:** `rate` (mayor código = menor % de cuota) y `pers` (mayor código = menos personas a cargo). Una interpretación ascendente ingenua invierte su sentido de negocio.
5. **Transformación:** `hoehe` es resultado de una transformación monótona sin documentar; las comparaciones de orden son válidas, pero el valor absoluto no es el monto exacto en DM.
6. **Base para el DW/Data Mart:** este diccionario alimenta directamente las dimensiones propuestas (`dim_cliente`, `dim_cuenta`, `dim_hist_credito`, `dim_proposito`, `dim_bien`, `dim_planes`, `dim_deudor`, `dim_vivienda`) y la tabla de hechos `fact_credito` (ver `docs/analisis/propuesta_dw_datamart.md` y `sql/schema_dw.sql`).
