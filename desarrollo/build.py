import sys, nbformat
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bloques import BLOQUES

REPO = Path("/home/claude/clase-mapeo-censo")

INTRO_NB = """# Mapeo de variables censales en el Gran Santiago
**¿Dónde se concentran las personas mayores (60 años y más) en el Gran Santiago y qué patrón territorial muestran?**

Clase aplicada · Magíster en Metodologías Críticas para la Investigación Social · 21 de octubre de 2026 · Datos: INE, Censo de Población y Vivienda 2024 (cartografía y base por manzana).

**Docente:** Benjamín Julio · Ingeniería Civil en Geografía, Minor en Ciencia de Datos · Universidad de Santiago de Chile

**Cómo usar este notebook en Google Colab**
1. *Archivo → Guardar una copia en Drive* para trabajar en tu propia copia.
2. Ejecuta los bloques **en orden** con el botón ▶ o `Shift + Enter`. El **Bloque 2** descarga los datos desde la carpeta compartida del docente.
3. Al final, el **Bloque 20** descarga todos los resultados en un zip.
"""

def build_notebook(path, reemplazos=None):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.cells.append(nbformat.v4.new_markdown_cell(INTRO_NB))
    for b in BLOQUES:
        nb.cells.append(nbformat.v4.new_markdown_cell(f"## {b['titulo']}\n\n{b['explicacion']}"))
        code = b["codigo"]
        for a, z in (reemplazos or {}).items():
            code = code.replace(a, z)
        nb.cells.append(nbformat.v4.new_code_cell(code))
    nbformat.write(nb, path)

def build_qmd(path):
    partes = ["""---
title: "Ejercicio aplicado en Python"
subtitle: "Del GeoParquet del INE al mapa, bloque a bloque"
---

[Abrir en Google Colab](https://colab.research.google.com/github/USUARIO/REPOSITORIO/blob/main/codigo/clase_censo_rm.ipynb){.btn .btn-warning role="button"}

::: {.callout-tip}
## Antes de empezar
1. Ten una cuenta de Google y **habilita Colab** en tu Google Drive (ver [Recursos](recursos.qmd#antes-de-la-clase)).
2. Abre el notebook con el botón **Abrir en Google Colab** y guarda una copia en tu Drive (*Archivo → Guardar una copia en Drive*).
3. Ejecuta los bloques en orden. El **Bloque 2** descarga los datos del Censo 2024 desde la [carpeta compartida del docente](https://drive.google.com/drive/folders/1qzYq0RzuFlMieopEV03JyfpTOxxxWjij); no necesitas subir nada.
:::

::: {.callout-note collapse="true"}
## ¿Prefieres R? (opcional, de referencia)
El script [`clase_censo_rm.R`](codigo/clase_censo_rm.R) reproduce los mismos bloques en RStudio. No se usa en clase.
:::

```{mermaid}
flowchart LR
  A[GeoParquet INE<br>manzanas] --> B[Filtrar Gran Santiago<br>y limpiar]
  B --> C[Tasa % 60+<br>por manzana]
  C --> D[Agregar<br>por comuna]
  D --> E[Gráfico]
  C --> BI[Clasificación<br>bivariada]
  D --> BI
  BI --> F[Mapas HTML]
  BI --> G[Mapas PNG/JPG]
  BI --> H[SHP · GPKG · KMZ]
  F --> Z[ZIP descargable]
  G --> Z
  H --> Z
```
"""]
    for b in BLOQUES:
        cab = f"## {b['titulo']}" + (" {.opcional}" if b["opcional"] else "")
        texto = f"{cab}\n\n{b['explicacion']}\n\n```python\n{b['codigo']}\n```\n"
        if b.get("imagen") and (REPO / b["imagen"][0]).exists():
            texto += f"\n![{b['imagen'][1]}]({b['imagen'][0]}){{.lightbox}}\n"
        partes.append(texto)
    Path(path).write_text("\n".join(partes), encoding="utf-8")

if __name__ == "__main__":
    (REPO / "codigo").mkdir(parents=True, exist_ok=True)
    build_notebook(REPO / "codigo" / "clase_censo_rm.ipynb")
    build_qmd(REPO / "02-ejercicio.qmd")
    # Notebook de prueba con datos sintéticos
    s = Path(__file__).parent
    build_notebook(s / "prueba" / "test.ipynb", {
        'FUENTE          = "docente"': 'FUENTE          = "local"',
        '"/content/drive/MyDrive/censo2024"': f'"{s}/prueba/datos3"',
        "%pip install -q mapclassify contextily gdown adjustText": "# %pip (omitido en prueba)",
        "%pip install -q esda libpysal": "# %pip (omitido en prueba)",
    })
    print("ok")
