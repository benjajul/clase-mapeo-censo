# Generar los 6 mapas del ejercicio aplicado (docente)

Variables (universos distintos: personas, viviendas y hogares):

| N.º | Variable | Denominador | Nombre en el mapa |
|---|---|---|---|
| 1 | `n_inmigrantes` | `n_per` | Población inmigrante internacional |
| 2 | `n_viv_hacinadas` | `n_vp_ocupada` | Viviendas hacinadas |
| 3 | `n_jefatura_mujer` | `n_hog` | Hogares con jefatura femenina |

1. Abrir `codigo/desafio_cartografia.ipynb` en Colab y ejecutar el Bloque 1.
2. Pegar en Gemini (Colab) el prompt de abajo, o ejecutar directamente la celda de respaldo.
3. Descomprimir `mapas_ejercicio.zip` y copiar los 6 JPEG en `img/ejercicio/` (mismos nombres).

## Prompt para Gemini

```text
Hola Gemini. Ya ejecuté el Bloque 1 de este notebook: cargó los datos del Censo 2024 y definió la función hacer_mapa(). No instales nada, no cargues datos y no escribas tu propio código de mapas: usa solo hacer_mapa().

Necesito UNA celda de código que genere 6 mapas por manzana y los descargue juntos en un zip.

Variables (numeradas 1, 2 y 3, en este orden):
1. variable_1="n_inmigrantes", denominador_1="n_per", nombre_1="Población inmigrante internacional"
2. variable_1="n_viv_hacinadas", denominador_1="n_vp_ocupada", nombre_1="Viviendas hacinadas"
3. variable_1="n_jefatura_mujer", denominador_1="n_hog", nombre_1="Hogares con jefatura femenina"

Territorios:
a) Gran Santiago: escala="Provincial", territorio="Gran Santiago"
b) Pudahuel: escala="Comunal", territorio="13124"

En todas las llamadas usa además: unidad="Manzana", area="Solo urbana", autor="Benjamín Julio", descargar="no" y archivo="gran_santiago_N" o "pudahuel_N" (N = número de la variable).

Cada llamada guarda el mapa en CARPETA_SALIDA / f"mapa_{archivo}.jpg". Agrega cada mapa a un zip llamado mapas_ejercicio.zip con el nombre gran_santiago_N.jpg o pudahuel_N.jpg (sin el prefijo "mapa_") y, al final, descarga el zip con google.colab.files.download. Muéstrame la celda antes de ejecutarla.
```

## Celda de respaldo (lo que Gemini debería entregar)

```python
import zipfile
from google.colab import files

VARIABLES = [
    ("n_inmigrantes", "n_per", "Población inmigrante internacional"),
    ("n_viv_hacinadas", "n_vp_ocupada", "Viviendas hacinadas"),
    ("n_jefatura_mujer", "n_hog", "Hogares con jefatura femenina"),
]
TERRITORIOS = [("Gran Santiago", "Provincial", "gran_santiago"), ("13124", "Comunal", "pudahuel")]

destino = CARPETA_SALIDA / "mapas_ejercicio.zip"
with zipfile.ZipFile(destino, "w") as z:
    for i, (variable, denominador, nombre) in enumerate(VARIABLES, start=1):
        for territorio, escala, prefijo in TERRITORIOS:
            hacer_mapa(escala=escala, territorio=territorio, variable_1=variable, denominador_1=denominador,
                       nombre_1=nombre, unidad="Manzana", area="Solo urbana", autor="Benjamín Julio",
                       archivo=f"{prefijo}_{i}", descargar="no")
            z.write(CARPETA_SALIDA / f"mapa_{prefijo}_{i}.jpg", arcname=f"{prefijo}_{i}.jpg")
files.download(str(destino))
```
