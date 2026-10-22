import sys, re, nbformat
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tarea_bloques as T
REPO = Path("/home/claude/clase-mapeo-censo")
def nb(path, reemplazos=None, params=None):
    n = nbformat.v4.new_notebook()
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    n.metadata["colab"] = {"provenance": [], "toc_visible": True}
    n.cells.append(nbformat.v4.new_markdown_cell(T.INTRO))
    for tit, ex, code in ((T.TITULO_1, T.EXPL_1, T.CODIGO_1), (T.TITULO_2, T.EXPL_2, T.CODIGO_2)):
        n.cells.append(nbformat.v4.new_markdown_cell(f"## {tit}\n\n{ex}"))
        for a, z in (reemplazos or {}).items(): code = code.replace(a, z)
        for k, v in (params or {}).items():
            code = re.sub(rf'^{k} = "[^"]*"', f'{k} = "{v}"', code, flags=re.M)
        c = nbformat.v4.new_code_cell(code); c.metadata["cellView"] = "form"
        n.cells.append(c)
    nbformat.write(n, path)
if __name__ == "__main__":
    nb(REPO / "codigo" / "tarea_cartografia.ipynb")
    base = Path(__file__).parent / "prueba_tarea"
    R = {'FUENTE = "docente"': 'FUENTE = "local"',
         'Path("/content/datos")': f'Path("{base}/datos")',
         'Path("/content/resultados")': f'Path("{base}/res")',
         'subprocess.run(': 'None and subprocess.run(',
         "display(": "print("}
    casos = {
     "c1": dict(ESCALA="Comunal", TERRITORIO="valparaiso"),
     "c2": dict(ESCALA="Regional", TERRITORIO="Valparaíso", VARIABLE_2="prom_escolaridad18", NOMBRE_2="Escolaridad promedio (18+)"),
     "c3": dict(ESCALA="Provincial", TERRITORIO="Santiago", VARIABLE_1="n_viv_hacinadas", DENOMINADOR_1="n_vp", NOMBRE_1="Viviendas hacinadas"),
     "c4": dict(ESCALA="Provincial", TERRITORIO="Cordillera", VARIABLE_2="prom_escolaridad18", NOMBRE_2="Escolaridad promedio (18+)"),
     "c5": dict(ESCALA="Comunal", TERRITORIO="Nunoa", VARIABLE_1="prom_escolaridad18", DENOMINADOR_1="", NOMBRE_1="Escolaridad promedio (18+)"),
     "c6": dict(ESCALA="Comunal", TERRITORIO="Viña"),
     "e1": dict(ESCALA="Comunal", TERRITORIO="Valparaizo"),
     "e2": dict(ESCALA="Comunal", TERRITORIO="Santiago", VARIABLE_1="n_edad_60mas"),
     "c7": dict(ESCALA="Regional", TERRITORIO="Metropolitana"),
     "c8": dict(ESCALA="Regional", TERRITORIO="Valparaiso", VARIABLE_1="n_analfabet", DENOMINADOR_1="n_ocupado+n_desocupado+n_fuera_fuerza_trabajo", NOMBRE_1="Analfabetismo (15+)", VARIABLE_2="prom_escolaridad18", DENOMINADOR_2="n_edad_18_24+n_edad_25_44+n_edad_45_59+n_edad_60_mas", NOMBRE_2="Escolaridad promedio (18+)"),
     "c9": dict(ESCALA="Comunal", TERRITORIO="Valparaíso", AREA="Solo urbana", VARIABLE_1="n_jefatura_mujer", DENOMINADOR_1="n_hog", NOMBRE_1="Hogares con jefatura femenina"),
     "e3": dict(ESCALA="Comunal", TERRITORIO="Santiago", DENOMINADOR_1="n_per-n_edad_0_"),
    }
    for k, p in casos.items():
        nb(base / f"{k}.ipynb", R, p)
