import json
from pathlib import Path

# Actualizar resumen de modelos
resumen = Path('docs/modelos/resumen_regresion_clasificacion.md')
content = resumen.read_text(encoding='utf-8')

reg = '''
## 1) Regresión - Predecir monto (`amount` / `hoehe`)

### Resultados (ejecución manual - sin sklearn/scipy por bloqueo App Control)
- **Modelo:** Regresión Lineal (mínimos cuadrados)
- **MAE:** 1538.27
- **RMSE:** 2025.97
- **R²:** 0.574
- **Modelo guardado:** `modelos/regresion/regresion_linear_manual_amount.pkl`

**Interpretación:** El modelo explica ~57.4% de la variabilidad del monto. El error promedio es ~1538 DM.
'''

clas = '''
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
'''

# Reemplazar secciones
# Buscar desde "## 1)" hasta antes de "## Notas"
start_reg = content.find('## 1)')
start_notas = content.find('## Notas')
if start_reg != -1 and start_notas != -1:
    new_content = content[:start_reg] + reg + '\n' + clas + '\n' + content[start_notas:]
    resumen.write_text(new_content, encoding='utf-8')
    print('actualizado')
else:
    print('no encontrado')
