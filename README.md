# Mapeo de variables censales en la Región Metropolitana

Material de la clase aplicada **Introducción al análisis espacial cuantitativo para las ciencias sociales**.

**Pregunta guía:** ¿dónde se concentran las personas mayores (60 años y más) en la RM, y qué patrón territorial muestran?
Datos: INE, Censo de Población y Vivienda 2024 (cartografía y base por manzana).

## Contenido

```
├── index.qmd            Inicio: pregunta, agenda, productos
├── 01-conceptos.qmd     Conceptos geoespaciales + ecosistema técnico
├── 02-ejercicio.qmd     Ejercicio en Python, por bloques
├── 03-cartografia.qmd   Elementos cartográficos y lectura crítica
├── 04-tarea.qmd         Ejercicio aplicado y rúbrica
├── recursos.qmd         Datos, software, lecturas
├── codigo/
│   ├── clase_censo_rm.ipynb   Notebook Python para Google Colab (19 bloques)
│   └── clase_censo_rm.R       Script R para RStudio (opcional, de referencia)
├── datos/               Vacía: los datos se descargan del INE
└── .github/workflows/publish.yml   Publicación automática en GitHub Pages
```

## Para estudiantes

La clase se trabaja en **Google Colab** (no requiere instalar nada).

1. Descarga la cartografía del Censo 2024 (ver `recursos.qmd` o el sitio) y súbela a Google Drive en `Mi unidad/censo2024`.
2. Abre el notebook en Colab:
   `https://colab.research.google.com/github/USUARIO/REPOSITORIO/blob/main/codigo/clase_censo_rm.ipynb`
3. Ejecuta los bloques en orden. El Bloque 18 descarga los resultados en un zip.

## Publicar el sitio en GitHub Pages

El sitio se publica **solo**: cada vez que se guarda un cambio en la rama `main`, GitHub Actions
(`.github/workflows/publish.yml`) construye el sitio con Quarto y lo sube a GitHub Pages.
Para activarlo, una sola vez: *Settings → Pages → Source: GitHub Actions*.

El sitio quedará en `https://<usuario>.github.io/<repositorio>/`.
Ver el manual paso a paso `manual_publicar_github.html` (entregado aparte).

Vista previa local (opcional, requiere [Quarto](https://quarto.org/docs/get-started/)): `quarto preview`

## Notas para el docente

- Los botones "Abrir en Colab" del sitio se completan solos con tu usuario y repositorio (`colab-link.html`). El repositorio debe ser **público** para que funcionen.
- Si consigues un enlace de descarga directa del INE, ponlo en `URL_DESCARGA` del Bloque 2 y cambia `FUENTE = "url"`: los estudiantes no tendrán que subir nada a Drive.
- El sitio **no ejecuta código** al renderizar: muestra los bloques como texto. Así se publica sin necesitar los datos.
- `02-ejercicio.qmd` y el notebook comparten los mismos bloques; si editas uno, actualiza el otro.
- El script R fue probado en sus bloques de procesamiento, gráfico, exportación y KMZ; la lectura con `arrow`, el mapa `leaflet` y el mapa base de `ggspatial` deben probarse con los datos reales.
