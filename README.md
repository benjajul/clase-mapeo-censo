# Mapeo de variables censales en el Gran Santiago

Material de la clase aplicada **Introducción al análisis espacial cuantitativo para las ciencias sociales**.

**Pregunta guía:** ¿dónde se concentran las personas mayores (60 años y más) en el Gran Santiago, y qué patrón territorial muestran?

**Docente:** Benjamín Julio · Ingeniería Civil en Geografía, Minor en Ciencia de Datos · Universidad de Santiago de Chile
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
│   ├── clase_censo_rm.ipynb   Notebook Python para Google Colab (21 bloques)
│   └── clase_censo_rm.R       Script R para RStudio (opcional, de referencia)
├── img/                 Imágenes de conceptos y resultados (resultado_*.png/jpg)
├── datos/               Vacía: los datos se descargan del INE
└── .github/workflows/publish.yml   Publicación automática en GitHub Pages
```

## Para estudiantes

La clase se trabaja en **Google Colab** (no requiere instalar nada).

1. Habilita Google Colab en tu cuenta de Google (ver `recursos.qmd`).
2. Abre el notebook en Colab (descarga los datos solo desde la carpeta compartida del docente):
   `https://colab.research.google.com/github/USUARIO/REPOSITORIO/blob/main/codigo/clase_censo_rm.ipynb`
3. Ejecuta los bloques en orden. El Bloque 20 descarga los resultados en un zip.

## Publicar el sitio en GitHub Pages

El sitio se publica **solo**: cada vez que se guarda un cambio en la rama `main`, GitHub Actions
(`.github/workflows/publish.yml`) construye el sitio con Quarto y lo sube a GitHub Pages.
Para activarlo, una sola vez: *Settings → Pages → Source: GitHub Actions*.

El sitio quedará en `https://<usuario>.github.io/<repositorio>/`.
Ver el manual paso a paso `manual_publicar_github.html` (entregado aparte).

Vista previa local (opcional, requiere [Quarto](https://quarto.org/docs/get-started/)): `quarto preview`

## Notas para el docente

- Los botones "Abrir en Colab" del sitio se completan solos con tu usuario y repositorio (`colab-link.html`). El repositorio debe ser **público** para que funcionen.
- Los datos se descargan desde la carpeta pública de Drive del docente (`FUENTE = "docente"` en el Bloque 2). La carpeta debe seguir compartida como "Cualquier persona con el enlace".
- El sitio **no ejecuta código** al renderizar: muestra los bloques como texto. Así se publica sin necesitar los datos.
- `02-ejercicio.qmd` y el notebook comparten los mismos bloques; si editas uno, actualiza el otro.
- El script R fue probado en sus bloques de procesamiento, gráfico, exportación y KMZ; la lectura con `arrow`, el mapa `leaflet` y el mapa base de `ggspatial` deben probarse con los datos reales.
