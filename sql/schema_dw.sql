-- Schema SQL para Data Warehouse / Data Mart (Propuesta)
-- Proyecto: Análisis de riesgo crediticio - South German Credit

-- Dimensiones
CREATE TABLE IF NOT EXISTS dim_cliente (
  sk_cliente SERIAL PRIMARY KEY,
  edad INT,
  estado_civil_sexo VARCHAR(50),
  personas_a_cargo VARCHAR(10),
  telefono VARCHAR(10),
  trabajador_extranjero VARCHAR(10),
  empleo_calidad VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_cuenta (
  sk_cuenta SERIAL PRIMARY KEY,
  estado_cuenta VARCHAR(30),
  ahorros VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS dim_hist_credito (
  sk_hist SERIAL PRIMARY KEY,
  historial_crediticio VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_proposito (
  sk_proposito SERIAL PRIMARY KEY,
  proposito VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS dim_bien (
  sk_bien SERIAL PRIMARY KEY,
  propiedad VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS dim_planes (
  sk_plan SERIAL PRIMARY KEY,
  otros_planes_cuota VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS dim_deudor (
  sk_deudor SERIAL PRIMARY KEY,
  otros_deudores VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS dim_vivienda (
  sk_vivienda SERIAL PRIMARY KEY,
  tipo_vivienda VARCHAR(20)
);

-- Hechos
CREATE TABLE IF NOT EXISTS fact_credito (
  sk_credito BIGSERIAL PRIMARY KEY,
  sk_cliente INT REFERENCES dim_cliente(sk_cliente),
  sk_cuenta INT REFERENCES dim_cuenta(sk_cuenta),
  sk_hist INT REFERENCES dim_hist_credito(sk_hist),
  sk_proposito INT REFERENCES dim_proposito(sk_proposito),
  sk_bien INT REFERENCES dim_bien(sk_bien),
  sk_plan INT REFERENCES dim_planes(sk_plan),
  sk_deudor INT REFERENCES dim_deudor(sk_deudor),
  sk_vivienda INT REFERENCES dim_vivienda(sk_vivienda),
  duracion_meses INT,
  monto_dm INT,
  tasa_cuota VARCHAR(10),
  tiempo_residencia VARCHAR(10),
  num_creditos_banco VARCHAR(10),
  riesgo_credito INT,
  riesgo_credito_cat VARCHAR(10)
);

-- Data Mart (vista)
CREATE OR REPLACE VIEW dm_riesgo_crediticio AS
SELECT 
  f.sk_credito,
  c.edad, c.estado_civil_sexo, c.personas_a_cargo, c.telefono, c.trabajador_extranjero, c.empleo_calidad,
  cu.estado_cuenta, cu.ahorros,
  h.historial_crediticio,
  p.proposito,
  b.propiedad,
  pl.otros_planes_cuota,
  d.otros_deudores,
  v.tipo_vivienda,
  f.duracion_meses, f.monto_dm, f.tasa_cuota, f.tiempo_residencia, f.num_creditos_banco,
  f.riesgo_credito, f.riesgo_credito_cat,
  ROUND(f.monto_dm::numeric / NULLIF(f.duracion_meses,0), 2) AS cuota_aprox_mensual
FROM fact_credito f
LEFT JOIN dim_cliente c ON c.sk_cliente = f.sk_cliente
LEFT JOIN dim_cuenta cu ON cu.sk_cuenta = f.sk_cuenta
LEFT JOIN dim_hist_credito h ON h.sk_hist = f.sk_hist
LEFT JOIN dim_proposito p ON p.sk_proposito = f.sk_proposito
LEFT JOIN dim_bien b ON b.sk_bien = f.sk_bien
LEFT JOIN dim_planes pl ON pl.sk_plan = f.sk_plan
LEFT JOIN dim_deudor d ON d.sk_deudor = f.sk_deudor
LEFT JOIN dim_vivienda v ON v.sk_vivienda = f.sk_vivienda;
