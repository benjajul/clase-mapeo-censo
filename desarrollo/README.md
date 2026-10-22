# Herramientas de desarrollo (no las usan los estudiantes)

Fuentes únicas desde donde se generan los notebooks, la página del ejercicio y las ilustraciones.
Las rutas dentro de los scripts son las del entorno donde se desarrollaron (`/home/claude/...`): ajústalas antes de usarlos.

| Archivo | Genera |
|---|---|
| `bloques.py` + `build.py` | `codigo/clase_censo_rm.ipynb` y `02-ejercicio.qmd` (21 bloques de la clase) |
| `tarea_bloques.py` + `tarea_build.py` | `codigo/tarea_cartografia.ipynb` (tarea en 2 bloques) y notebooks de prueba |
| `ilustraciones.py` | `img/guia/*.svg` (ilustraciones de la guía de Colab y Gemini) |
| `datos_prueba3.py`, `datos_tarea.py` | Datos sintéticos para probar los notebooks sin descargar el Censo |

Prueba: `python tarea_build.py` y luego `jupyter nbconvert --to notebook --execute prueba_tarea/c1.ipynb`.
