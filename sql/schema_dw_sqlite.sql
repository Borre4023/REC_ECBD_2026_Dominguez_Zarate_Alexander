-- Schema Data Warehouse / Data Mart — adaptado a SQLite
-- Proyecto: Análisis de riesgo crediticio — South German Credit (UTTT)
-- Origen del diseño: sql/schema_dw.sql (PostgreSQL); este dialecto permite
-- implementar y validar el DW sin servidor. Creador: src/etl/build_dw_sqlite.py

PRAGMA foreign_keys = ON;

-- ============ DIMENSIONES ============

CREATE TABLE IF NOT EXISTS dim_cliente (
  sk_cliente           INTEGER PRIMARY KEY AUTOINCREMENT,
  edad                 INTEGER,
  estado_civil_sexo    TEXT,
  personas_a_cargo     TEXT,
  telefono             TEXT,
  trabajador_extranjero TEXT,
  empleo_calidad       TEXT
);

CREATE TABLE IF NOT EXISTS dim_cuenta (
  sk_cuenta       INTEGER PRIMARY KEY AUTOINCREMENT,
  estado_cuenta   TEXT,
  ahorros         TEXT
);

CREATE TABLE IF NOT EXISTS dim_hist_credito (
  sk_hist               INTEGER PRIMARY KEY AUTOINCREMENT,
  historial_crediticio  TEXT
);

CREATE TABLE IF NOT EXISTS dim_proposito (
  sk_proposito INTEGER PRIMARY KEY AUTOINCREMENT,
  proposito    TEXT
);

CREATE TABLE IF NOT EXISTS dim_bien (
  sk_bien   INTEGER PRIMARY KEY AUTOINCREMENT,
  propiedad TEXT
);

CREATE TABLE IF NOT EXISTS dim_planes (
  sk_plan             INTEGER PRIMARY KEY AUTOINCREMENT,
  otros_planes_cuota  TEXT
);

CREATE TABLE IF NOT EXISTS dim_deudor (
  sk_deudor      INTEGER PRIMARY KEY AUTOINCREMENT,
  otros_deudores TEXT
);

CREATE TABLE IF NOT EXISTS dim_vivienda (
  sk_vivienda  INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo_vivienda TEXT
);

-- ============ HECHOS ============

CREATE TABLE IF NOT EXISTS fact_credito (
  sk_credito           INTEGER PRIMARY KEY AUTOINCREMENT,
  sk_cliente           INTEGER REFERENCES dim_cliente(sk_cliente),
  sk_cuenta            INTEGER REFERENCES dim_cuenta(sk_cuenta),
  sk_hist              INTEGER REFERENCES dim_hist_credito(sk_hist),
  sk_proposito         INTEGER REFERENCES dim_proposito(sk_proposito),
  sk_bien              INTEGER REFERENCES dim_bien(sk_bien),
  sk_plan              INTEGER REFERENCES dim_planes(sk_plan),
  sk_deudor            INTEGER REFERENCES dim_deudor(sk_deudor),
  sk_vivienda          INTEGER REFERENCES dim_vivienda(sk_vivienda),
  duracion_meses       INTEGER,
  monto_dm             INTEGER,
  tasa_cuota           TEXT,
  tiempo_residencia    TEXT,
  num_creditos_banco   TEXT,
  riesgo_credito       INTEGER,
  riesgo_credito_cat   TEXT
);

CREATE INDEX IF NOT EXISTS ix_fact_cliente   ON fact_credito(sk_cliente);
CREATE INDEX IF NOT EXISTS ix_fact_cuenta    ON fact_credito(sk_cuenta);
CREATE INDEX IF NOT EXISTS ix_fact_hist      ON fact_credito(sk_hist);
CREATE INDEX IF NOT EXISTS ix_fact_proposito ON fact_credito(sk_proposito);

-- ============ DATA MART (vista de consumo) ============

CREATE VIEW IF NOT EXISTS dm_riesgo_crediticio AS
SELECT
  f.sk_credito,
  c.edad, c.estado_civil_sexo, c.personas_a_cargo, c.telefono,
  c.trabajador_extranjero, c.empleo_calidad,
  cu.estado_cuenta, cu.ahorros,
  h.historial_crediticio,
  p.proposito,
  b.propiedad,
  pl.otros_planes_cuota,
  d.otros_deudores,
  v.tipo_vivienda,
  f.duracion_meses, f.monto_dm, f.tasa_cuota, f.tiempo_residencia,
  f.num_creditos_banco,
  f.riesgo_credito, f.riesgo_credito_cat,
  ROUND(f.monto_dm * 1.0 / NULLIF(f.duracion_meses, 0), 2) AS cuota_aprox_mensual
FROM fact_credito f
LEFT JOIN dim_cliente     c  ON c.sk_cliente   = f.sk_cliente
LEFT JOIN dim_cuenta      cu ON cu.sk_cuenta   = f.sk_cuenta
LEFT JOIN dim_hist_credito h ON h.sk_hist     = f.sk_hist
LEFT JOIN dim_proposito   p  ON p.sk_proposito = f.sk_proposito
LEFT JOIN dim_bien        b  ON b.sk_bien      = f.sk_bien
LEFT JOIN dim_planes      pl ON pl.sk_plan     = f.sk_plan
LEFT JOIN dim_deudor      d  ON d.sk_deudor    = f.sk_deudor
LEFT JOIN dim_vivienda    v  ON v.sk_vivienda  = f.sk_vivienda;
