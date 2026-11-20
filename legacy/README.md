# legacy/ — scripts de la fase manual (pre-sklearn)

Scripts de la primera versión de la Unidad III (23 oct), escritos cuando el entorno bloqueaba
sklearn/scipy. Se conservan solo como referencia histórica; **no forman parte del pipeline**.
Los modelos finales se generan con `src/models/entrenar_regresion.py` y
`src/models/entrenar_clasificacion.py` (ver `docs/modelos/evaluacion_modelos.md`).

Usan rutas relativas a la raíz del repositorio, así que, si se quieren ejecutar, hay que
hacerlo desde la raíz: `py legacy/run_reg_manual.py`.
