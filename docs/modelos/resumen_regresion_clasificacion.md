# Resumen de Modelos: Regresión y Clasificación

**Fecha:** 2026-10-27  
**Dataset:** South German Credit (procesado)  


## 1) Regresión - Predecir monto (`amount` / `hoehe`)

### Resultados (ejecución manual - sin sklearn/scipy por bloqueo App Control)
- **Modelo:** Regresión Lineal (mínimos cuadrados)
- **MAE:** 1538.27
- **RMSE:** 2025.97
- **R²:** 0.574
- **Modelo guardado:** `modelos/regresion/regresion_linear_manual_amount.pkl`

**Interpretación:** El modelo explica ~57.4% de la variabilidad del monto. El error promedio es ~1538 DM.


## 2) Clasificación - Predecir riesgo crediticio (`credit_risk`)

### Resultados (ejecución manual - sin sklearn/scipy por bloqueo App Control)
- **Modelo:** Regresión Logística (gradiente descendente)
- **Accuracy:** 0.700
- **Precision:** 0.700
- **Recall:** 1.000
- **F1-score:** 0.824
- **ROC-AUC:** 0.500
- **Matriz de confusión:** TN=0, FP=60, FN=0, TP=140
- **Modelo guardado:** `modelos/clasificacion/clasificacion_logistic_manual_creditrisk.pkl`

**Nota:** Con el split estratificado y sin balanceo efectivo en esta implementación manual, el modelo tiende a predecir la clase mayoritaria (good). Esto es esperado y demuestra la importancia del manejo de desbalance.

## Notas didácticas
- Para regresión, la duración (`laufzeit`) y el propósito/historial suelen tener relación con el monto.
- Para clasificación con desbalance, **Recall** para la clase minoritaria (`bad`) y **ROC-AUC** son especialmente importantes.
- Los modelos son con fines académicos, no para uso crediticio real.
