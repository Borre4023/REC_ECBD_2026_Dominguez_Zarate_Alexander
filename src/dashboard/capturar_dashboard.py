"""
Capturas del dashboard HTML — South German Credit (Fase 6)
Toma capturas del dashboard autocontenido con un navegador headless
(Chrome o Edge, el que exista) y recorta espacios en blanco con Pillow.

Estrategia: se generan variantes temporales del HTML mostrando solo una
sección a la vez (las demás se ocultan con CSS), se captura cada una y se
recorta. Sin dependencias nuevas (no requiere Playwright/Selenium).

Uso:
    py src/dashboard/capturar_dashboard.py
Salidas:
    docs/resultados/capturas/00_problema_preparacion.png
    docs/resultados/capturas/01_panorama.png
    docs/resultados/capturas/02_riesgo.png
    docs/resultados/capturas/03_exposicion.png
    docs/resultados/capturas/04_clasificacion.png
    docs/resultados/capturas/05_regresion.png
    docs/resultados/capturas/06_segmentos.png
    docs/resultados/capturas/07_conocimiento_recomendaciones.png
"""
import os
import shutil
import subprocess
import tempfile

from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML = os.path.join(BASE_DIR, 'dashboard', 'index.html')
SALIDA_DIR = os.path.join(BASE_DIR, 'docs', 'resultados', 'capturas')

# (nombre de salida, índices de <section> visibles 1-based, alto de ventana)
CAPTURAS = [
    ('00_problema_preparacion.png', [1, 2], 1100),
    ('01_panorama.png', [3], 780),
    ('02_riesgo.png', [4, 5], 1500),
    ('03_exposicion.png', [6, 7, 8], 1800),
    ('04_clasificacion.png', [9], 1300),
    ('05_regresion.png', [10], 1300),
    ('06_segmentos.png', [11], 1900),
    ('07_conocimiento_recomendaciones.png', [12], 1100),
]

NAVEGADORES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]


def encontrar_navegador():
    for ruta in NAVEGADORES:
        if os.path.exists(ruta):
            return ruta
    raise FileNotFoundError('No se encontró Chrome ni Edge para las capturas')


def capturar(navegador, ruta_html, ruta_png, alto):
    """Captura el HTML con headless a un PNG de ancho fijo."""
    tmp = ruta_png + '.tmp.png'
    cmd = [
        navegador,
        '--headless=new',
        '--disable-gpu',
        '--hide-scrollbars',
        '--force-device-scale-factor=1.4',
        f'--window-size=1180,{alto}',
        f'--screenshot={tmp}',
        'file:///' + ruta_html.replace('\\', '/'),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120,
                   creationflags=subprocess.CREATE_NO_WINDOW)
    shutil.move(tmp, ruta_png)


def recortar_blanco(ruta_png, margen=14):
    """Recorta el fondo blanco excedente dejando un margen."""
    img = Image.open(ruta_png).convert('RGB')
    gris = Image.new('RGB', img.size, (255, 255, 255))
    diff = __import__('PIL.ImageChops', fromlist=['difference']).difference(img, gris)
    bbox = diff.getbbox()
    if bbox:
        l, t, r, b = bbox
        l = max(0, l - margen)
        t = max(0, t - margen)
        r = min(img.width, r + margen)
        b = min(img.height, b + margen)
        img.crop((l, t, r, b)).save(ruta_png)


def main():
    navegador = encontrar_navegador()
    print('navegador headless:', navegador)
    os.makedirs(SALIDA_DIR, exist_ok=True)

    with open(HTML, encoding='utf-8') as f:
        html = f.read()

    # regla CSS para mostrar solo las secciones indicadas
    with tempfile.TemporaryDirectory() as tmp_dir:
        for nombre, secciones, alto in CAPTURAS:
            vis = ' '.join(f'main > section:nth-of-type({s}){{display:block}}'
                           for s in secciones)
            regla = (f'<style>header{{display:none}} footer{{display:none}} '
                     f'main{{padding:10px}} main > section{{display:none}} '
                     f'{vis} body{{background:#fff}}</style>')
            variante = html.replace('</head>', regla + '</head>')
            ruta_var = os.path.join(tmp_dir, 'var.html')
            with open(ruta_var, 'w', encoding='utf-8') as f:
                f.write(variante)
            ruta_out = os.path.join(SALIDA_DIR, nombre)
            capturar(navegador, ruta_var, ruta_out, alto)
            recortar_blanco(ruta_out)
            w, h = Image.open(ruta_out).size
            print(f'{nombre}: {w} x {h} px')
    print('capturas en:', SALIDA_DIR)


if __name__ == '__main__':
    main()
