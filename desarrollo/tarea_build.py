import sys, re, nbformat
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tarea_bloques as T
from armador import widget
REPO = Path("/home/claude/clase-mapeo-censo")
EJEMPLO_B5 = 'hacer_mapa(escala="Comunal", territorio="13101", variable_1="n_edad_60_mas", autor="Ejemplo")'

def nb(path, reemplazos=None, params=None, extra=None, con_ejemplo=False):
    import desafio_bloques as D
    n = nbformat.v4.new_notebook()
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    n.metadata["colab"] = {"provenance": [], "toc_visible": True}
    n.cells.append(nbformat.v4.new_markdown_cell(D.INTRO))
    pruebas = reemplazos is not None
    for clave, code, formulario in D.BLOQUES:
        n.cells.append(nbformat.v4.new_markdown_cell(D.MD[clave]))
        code = code.replace("__ARMADOR_HTML__", widget())
        if pruebas and clave == "B5" and not con_ejemplo:
            code = code.replace(EJEMPLO_B5, "pass")
        for a, z in (reemplazos or {}).items(): code = code.replace(a, z)
        for k, v in (params or {}).items():
            code = re.sub(rf'^{k} = "[^"]*"', f'{k} = "{v}"', code, flags=re.M)
        c = nbformat.v4.new_code_cell(code)
        if formulario:
            c.metadata["cellView"] = "form"
        n.cells.append(c)
    if extra:
        n.cells.append(nbformat.v4.new_code_cell(extra))
    nbformat.write(n, path)

if __name__ == "__main__":
    nb(REPO / "codigo" / "desafio_cartografia.ipynb")
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
     "c10": dict(ESCALA="Provincial", TERRITORIO="Santiago"),
     "c11": dict(ESCALA="Comunal", TERRITORIO="13101"),
     "c12": dict(ESCALA="Provincial", TERRITORIO="51"),
     "e4": dict(ESCALA="Provincial", TERRITORIO="13101"),
     "e3": dict(ESCALA="Comunal", TERRITORIO="Santiago", DENOMINADOR_1="n_per-n_edad_0_"),
    }
    for k, p in casos.items():
        nb(base / f"{k}.ipynb", R, p)
    nb(base / "ej.ipynb", {**R, "\nhacer_mapa(escala=ESCALA": "\n0 and hacer_mapa(escala=ESCALA"}, None, None, con_ejemplo=True)
    # Línea como la que entrega Gemini (sin usar el formulario)
    nb(base / "g1.ipynb", {**R, "\nhacer_mapa(escala=ESCALA": "\n0 and hacer_mapa(escala=ESCALA"}, None,
       'hacer_mapa(escala="Regional", territorio="05", variable_1="n_edad_60_mas", denominador_1="n_per", '
       'nombre_1="Personas de 60 años y más", variable_2="prom_escolaridad18", denominador_2="", '
       'nombre_2="Escolaridad promedio (18+)", titulo="¿Envejecimiento y escolaridad van juntos?", autor="Camila Rojas")')
    nb(base / "g2.ipynb", {**R, "\nhacer_mapa(escala=ESCALA": "\n0 and hacer_mapa(escala=ESCALA"}, None,
       'hacer_mapa(Escala="comunal", TERRITORIO="13101", variable_1="n_viv_hacinadas")')
