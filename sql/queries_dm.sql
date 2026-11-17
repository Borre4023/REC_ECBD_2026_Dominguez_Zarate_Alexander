-- Consultas analíticas del Data Mart (SQLite) — South German Credit
-- Base: data/processed/dw_south_german_credit.db
-- Uso: sqlite3 data/processed/dw_south_german_credit.db < sql/queries_dm.sql
-- Cada consulta responde una pregunta de negocio del proyecto.

-- Q1. ¿Qué historial crediticio concentra el mayor riesgo?
--     Tasa de incumplimiento (% bad) por categoría de 'moral'.
SELECT h.historial_crediticio        AS historial,
       COUNT(*)                      AS creditos,
       SUM(f.riesgo_credito = 0)     AS bad,
       ROUND(100.0 * SUM(f.riesgo_credito = 0) / COUNT(*), 1) AS pct_bad
FROM fact_credito f
JOIN dim_hist_credito h ON h.sk_hist = f.sk_hist
GROUP BY h.historial_crediticio
ORDER BY pct_bad DESC;

-- Q2. ¿En qué propósitos se pide más dinero y con mayor carga mensual?
--     Monto y cuota promedio por propósito del crédito.
SELECT p.proposito                                   AS proposito,
       COUNT(*)                                      AS creditos,
       ROUND(AVG(f.monto_dm), 0)                     AS monto_prom,
       ROUND(AVG(f.monto_dm * 1.0 / f.duracion_meses), 2) AS cuota_prom
FROM fact_credito f
JOIN dim_proposito p ON p.sk_proposito = f.sk_proposito
GROUP BY p.proposito
ORDER BY monto_prom DESC;

-- Q3. ¿Cómo se comporta el riesgo según la situación de la cuenta del deudor?
--     % bad por estado de cuenta y nivel de ahorros.
SELECT cu.estado_cuenta AS estado_cuenta,
       cu.ahorros       AS ahorros,
       COUNT(*)         AS creditos,
       SUM(f.riesgo_credito = 0) AS bad,
       ROUND(100.0 * SUM(f.riesgo_credito = 0) / COUNT(*), 1) AS pct_bad
FROM fact_credito f
JOIN dim_cuenta cu ON cu.sk_cuenta = f.sk_cuenta
GROUP BY cu.estado_cuenta, cu.ahorros
ORDER BY pct_bad DESC;

-- Q4. ¿Cuáles son los créditos con mayor carga mensual (exposición)?
--     Top 10 por cuota aproximada, con su perfil y resultado.
SELECT dm.sk_credito,
       dm.monto_dm,
       dm.duracion_meses,
       dm.cuota_aprox_mensual,
       dm.historial_crediticio,
       dm.proposito,
       dm.riesgo_credito_cat
FROM dm_riesgo_crediticio dm
ORDER BY dm.cuota_aprox_mensual DESC
LIMIT 10;

-- Q5. ¿Cómo cambia el riesgo por rango de monto solicitado?
--     Segmentación en 4 rangos con % bad por rango.
SELECT CASE
         WHEN f.monto_dm <  1500 THEN 'a. <1500'
         WHEN f.monto_dm <  4000 THEN 'b. 1500-3999'
         WHEN f.monto_dm <  8000 THEN 'c. 4000-7999'
         ELSE 'd. >=8000'
       END                                      AS rango_monto,
       COUNT(*)                                 AS creditos,
       ROUND(AVG(f.monto_dm), 0)                AS monto_prom,
       SUM(f.riesgo_credito = 0)                AS bad,
       ROUND(100.0 * SUM(f.riesgo_credito = 0) / COUNT(*), 1) AS pct_bad
FROM fact_credito f
GROUP BY rango_monto
ORDER BY rango_monto;
