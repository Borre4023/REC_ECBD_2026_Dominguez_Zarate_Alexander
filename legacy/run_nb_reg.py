import json, sys
from pathlib import Path

nb_path = Path("notebooks/03_regresion.ipynb")
with nb_path.open(encoding="utf-8-sig") as f:
    nb = json.load(f)

ns = {}
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        if not src.strip():
            continue
        print(f"=== Ejecutando celda {i} ===")
        try:
            exec(compile(src, f"<cell_{i}>", "exec"), ns)
        except Exception as e:
            print("ERROR:", e)
            raise
print("=== REGRESION COMPLETADO ===")
