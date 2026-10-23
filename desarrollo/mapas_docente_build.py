"""Genera codigo/mapas_ejercicio_docente.ipynb: crea los 6 mapas del ejercicio aplicado de una vez."""
import sys, re, nbformat
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tarea_bloques as T

REPO = Path(__file__).resolve().parent.parent

INTRO = """# Mapas del ejercicio aplicado (docente)
Genera los **6 mapas por manzana** del ejercicio «Después de la clase» y los descarga en un zip:
3 variables × 2 territorios (Gran Santiago y comuna de Recoleta).

**Cómo usarlo:** *Entorno de ejecución → Ejecutar todas* (o `Ctrl + F9`). Tarda entre 10 y 20 minutos.
Al final se descarga `mapas_ejercicio.zip` con `gran_santiago_1.jpg` … `recoleta_3.jpg`, listos para `img/ejercicio/`."""

PARAMS = '''#@title 1 · Configuración (puedes cambiar estos valores)
VARIABLES = [
    # (variable, denominador, nombre en el mapa)
    ("n_inmigrantes", "n_per", "Población inmigrante internacional"),
    ("n_viv_hacinadas", "n_vp_ocupada", "Viviendas hacinadas"),
    ("n_jefatura_mujer", "n_hog", "Hogares con jefatura femenina"),
]
TERRITORIOS = [
    # (territorio, escala, prefijo del archivo)
    ("Gran Santiago", "Provincial", "gran_santiago"),
    ("13127", "Comunal", "recoleta"),
]
AREA = "Solo urbana"          #@param ["Solo urbana", "Urbana y rural"]
AUTOR = "Benjamín Julio"      #@param {type:"string"}
'''

LOTE = '''#@title 3 · Crear los 6 mapas y descargarlos en un zip
import zipfile

# Revisión rápida: cómo viene codificada el área urbana/rural en la base
if "AREA_C" in COLUMNAS:
    print("Valores de AREA_C en la base:",
          dict(pd.read_parquet(RUTA_MANZANAS, columns=["AREA_C"])["AREA_C"].value_counts().head()))

destino = CARPETA_SALIDA / "mapas_ejercicio.zip"
listos = []
with zipfile.ZipFile(destino, "w") as z:
    for i, (variable, denominador, nombre) in enumerate(VARIABLES, start=1):
        for territorio, escala, prefijo in TERRITORIOS:
            archivo = f"{prefijo}_{i}"
            print(f"\\n===== {archivo}: {nombre} · {territorio} =====")
            try:
                hacer_mapa(escala=escala, territorio=territorio, variable_1=variable,
                           denominador_1=denominador, nombre_1=nombre, unidad="Manzana",
                           area=AREA, autor=AUTOR, archivo=archivo, descargar="no")
            except Revisa:
                print(f"⚠️  {archivo} no se generó: revisa el recuadro amarillo de arriba.")
                continue
            z.write(CARPETA_SALIDA / f"mapa_{archivo}.jpg", arcname=f"{archivo}.jpg")
            listos.append(f"{archivo}.jpg")

caja("ok" if len(listos) == 6 else "revisa", f"{len(listos)} de 6 mapas listos", ", ".join(listos) or "ninguno")
try:
    from google.colab import files
    files.download(str(destino))
except ImportError:
    pass
'''

def preparar_bloque1():
    import desafio_bloques as D
    return ('#@title 2 · Preparar el entorno, cargar los datos y definir hacer_mapa() { display-mode: "form" }\n'
            + D.PREPARAR + '\ncaja("ok", "Datos y herramienta listos.", "Sigue con el bloque 3.")\n')

def nb(path, reemplazos=None):
    n = nbformat.v4.new_notebook()
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    n.metadata["colab"] = {"provenance": []}
    n.cells.append(nbformat.v4.new_markdown_cell(INTRO))
    for code in (PARAMS, preparar_bloque1(), LOTE):
        for a, z in (reemplazos or {}).items():
            code = code.replace(a, z)
        c = nbformat.v4.new_code_cell(code); c.metadata["cellView"] = "form"
        n.cells.append(c)
    nbformat.write(n, path)

if __name__ == "__main__":
    nb(REPO / "codigo" / "mapas_ejercicio_docente.ipynb")
    if len(sys.argv) > 1:   # prueba local: python mapas_docente_build.py <carpeta_prueba>
        base = Path(sys.argv[1])
        nb(base / "docente.ipynb", {'FUENTE = "docente"': 'FUENTE = "local"',
            'Path("/content/datos")': f'Path("{base}/datos")', 'Path("/content/resultados")': f'Path("{base}/res")',
            'subprocess.run(': 'None and subprocess.run(',
            'Path("diccionario_para_IA.txt")': f'Path("{base}/diccionario_para_IA.txt")'})
    print("ok")
