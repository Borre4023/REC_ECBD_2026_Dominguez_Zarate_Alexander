# Diccionario de Datos - South German Credit

**Fuente:** UCI Machine Learning Repository - South German Credit (Dataset 573)  
**Fecha:** 2026-10-27  
**Registros:** 1000  
**Variables:** 21  

## Mapeo de variables

| Columna original (archivo) | Nombre semántico | Tipo | Descripción | Valores/Codificación | Notas |
|----------------------------|-------------------|------|-------------|---------------------|-------|
| laufkont | status | Categórica (ordinal) | Estado de la cuenta corriente del cliente | 1: sin cuenta corriente / 2: < 0 DM / 3: 0 <= ... < 200 DM / 4: >= 200 DM / salario por >=1 año | - |
| laufzeit | duration | Cuantitativa | Duración del crédito en meses | Numérico (entero) | - |
| moral | credit_history | Categórica (ordinal) | Historial crediticio / cumplimiento previo | 0: retraso en pagos / 1: cuenta crítica/créditos en otros bancos / 2: sin créditos o todos pagados puntualmente / 3: créditos existentes pagados puntualmente hasta ahora / 4: todos los créditos en este banco pagados puntualmente | - |
| verw | purpose | Categórica (nominal) | Propósito del crédito | 0: otros / 1: coche nuevo / 2: coche usado / 3: muebles/equipamiento / 4: radio/televisión / 5: electrodomésticos / 6: reparaciones / 7: educación / 8: vacaciones / 9: reciclaje/formación / 10: negocio | - |
| hoehe | amount | Cuantitativa | Monto del crédito en marcos alemanes (DM) | Numérico (entero). Transformación monotónica (valor exacto/tipo desconocidos) | Variable objetivo para regresión |
| sparkont | savings | Categórica (ordinal) | Ahorros del cliente | 1: desconocido/sin cuenta de ahorros / 2: < 100 DM / 3: 100 <= ... < 500 DM / 4: 500 <= ... < 1000 DM / 5: >= 1000 DM | - |
| beszeit | employment_duration | Categórica (ordinal) | Antigüedad en empleo actual | 1: desempleado / 2: < 1 año / 3: 1 <= ... < 4 años / 4: 4 <= ... < 7 años / 5: >= 7 años | - |
| rate | installment_rate | Categórica (ordinal) | Cuota como porcentaje del ingreso disponible | 1: >= 35% / 2: 25 <= ... < 35% / 3: 20 <= ... < 25% / 4: < 20% | Discretizado |
| famges | personal_status_sex | Categórica (nominal) | Estado civil y sexo (combinados) | 1: hombre: divorciado/separado / 2: mujer: no soltera o hombre: soltero / 3: hombre: casado/viudo / 4: mujer: soltera | Sexo no recuperable completamente por codificación |
| buerge | other_debtors | Categórica (nominal) | Avales/otros deudores | 1: ninguno / 2: co-solicitante / 3: aval (garante) | - |
| wohnzeit | present_residence | Categórica (ordinal) | Tiempo en residencia actual | 1: < 1 año / 2: 1 <= ... < 4 años / 3: 4 <= ... < 7 años / 4: >= 7 años | Discretizado |
| verm | property | Categórica (ordinal) | Bien más valioso del cliente | 1: desconocido/sin propiedad / 2: coche u otro / 3: seguro de vida/ahorro para vivienda / 4: bienes inmuebles | Se toma el código más alto |
| alter | age | Cuantitativa | Edad en años | Numérico (entero) | - |
| weitkred | other_installment_plans | Categórica (nominal) | Planes de cuota con otros acreedores | 1: banco / 2: tiendas / 3: ninguno | - |
| wohn | housing | Categórica (nominal) | Tipo de vivienda | 1: gratis / 2: alquilada / 3: propia | - |
| bishkred | number_credits | Categórica (ordinal) | Número de créditos (incluido el actual) en este banco | 1: 1 / 2: 2-3 / 3: 4-5 / 4: >= 6 | Discretizado |
| beruf | job | Categórica (ordinal) | Calidad del empleo | 1: desempleado/no cualificado - no residente / 2: no cualificado - residente / 3: empleado cualificado/funcionario / 4: directivo/autónomo/alta cualificación | - |
| pers | people_liable | Binaria/Ordinal | Personas a cargo (derecho a manutención) | 1: >= 3 / 2: 0 a 2 | Discretizado |
| telef | telephone | Binaria | Teléfono registrado a nombre del cliente | 1: no / 2: sí (a nombre del cliente) | Datos de los años 1970 |
| gastarb | foreign_worker | Binaria | Trabajador extranjero | 1: sí / 2: no | - |
| kredit | credit_risk | Binaria (objetivo) | Cumplimiento del contrato | 0: malo (bad) / 1: bueno (good) | Variable objetivo para clasificación |

## Observaciones
- Sin valores faltantes reportados
- Variables codificadas (requieren decodificación para análisis legible)
- `amount` es el resultado de una transformación monotónica (tipo exacto desconocido)
- Desbalance de clases: 700 buenos / 300 malos (según descripción UCI)
- Datos de 1973-1975
