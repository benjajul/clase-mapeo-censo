"""Notebook del desafío en 7 bloques cortos, con explicaciones paso a paso.

El código base vive en tarea_bloques.py (CODIGO_1 y CODIGO_2); aquí se divide en bloques
más pequeños y se agregan las tarjetas explicativas para quien nunca ha usado Colab.
"""
import tarea_bloques as T

C1 = T.CODIGO_1


def entre(inicio, fin=None):
    i = C1.index(inicio)
    j = C1.index(fin, i) if fin else len(C1)
    return C1[i:j]


# ---------------------------------------------------------------- piezas del código original
importaciones = entre("import subprocess, sys", "# 1. Descargar los datos")
descarga = entre("# 1. Descargar los datos", "def normalizar(texto):")
ayudantes = entre("def normalizar(texto):", "# 3. Catálogo territorial")
catalogo = entre("# 3. Catálogo territorial", "# 4. Diccionario de variables")
diccionario = entre("# 4. Diccionario de variables", "# 5. Resumen en pantalla")
funcion = entre("# 6. La función que hace el mapa", "# 7. Armador del mensaje")
armador = entre("# 7. Armador del mensaje")


def requiere(variable, bloque):
    # Revisa que el bloque anterior se haya ejecutado; si no, avisa con un recuadro amarillo
    return (f'if "{variable}" not in globals():\n'
            f'    if "avisar" in globals():\n'
            f'        avisar("Antes de este bloque ejecuta <b>{bloque}</b> (botón ▶) y espera su recuadro verde.")\n'
            f'    raise SystemExit("⚠️ Antes de este bloque ejecuta {bloque} (botón ▶).")\n\n')


# ---------------------------------------------------------------- bloques
B1 = ('#@title ▶ Bloque 1 · Preparar Colab { display-mode: "form" }\n'
      '# No necesitas modificar nada: solo presiona ▶.\n'
      + importaciones + ayudantes +
      '\ncaja("ok", "Bloque 1 listo: Colab está preparado.", "Sigue con el <b>Bloque 2</b>.")\n')

B2 = ('#@title ▶ Bloque 2 · Descargar los datos del Censo 2024 { display-mode: "form" }\n'
      + requiere("caja", "el Bloque 1")
      + 'caja("info", "Descargando y abriendo los datos…", "La primera vez tarda entre 1 y 3 minutos. No cierres la pestaña.")\n'
      + descarga + catalogo +
      '''
caja("ok", f"Bloque 2 listo: {CATALOGO['manzanas'].sum():,} manzanas y entidades en {CATALOGO['CUT'].nunique()} comunas.",
     "Sigue con el <b>Bloque 3</b>.")
caja("info", "Dato útil: nombres repetidos",
     f"{len(AMBIGUOS)} nombres existen como comuna y también como provincia o región (por ejemplo: "
     + ", ".join(v[0][1].title() for v in list(AMBIGUOS.values())[:5])
     + "). Por eso Gemini usará <b>códigos</b> para el territorio.")
''')

B3 = ('#@title ▶ Bloque 3 · Preparar el diccionario y la herramienta de mapas { display-mode: "form" }\n'
      + requiere("CATALOGO", "el Bloque 2")
      + diccionario + funcion +
      '''
if DICCIONARIO is None:
    caja("revisa", "No encontré el diccionario del INE",
         "El mensaje para Gemini solo tendrá la lista de columnas. Avísale al docente.")
caja("ok", "Bloque 3 listo: diccionario cargado y herramienta de mapas preparada.", "Sigue con el <b>Bloque 4</b>.")
''')

B4 = ('#@title ▶ Bloque 4 · Arma tu mensaje para Gemini { display-mode: "form" }\n'
      + requiere("hacer_mapa", "el Bloque 3")
      + armador)

B5 = '''# ▶ Bloque 5 · Tu mapa
# 1) Borra la línea de ejemplo de abajo.
# 2) Pega en su lugar la línea hacer_mapa(...) que te dio Gemini.
# 3) Presiona ▶ (a la izquierda de este bloque).
# ¿Aún no tienes tu línea? Presiona ▶ igual: se hará un mapa de ejemplo para que veas cómo funciona.

hacer_mapa(escala="Comunal", territorio="13101", variable_1="n_edad_60_mas", autor="Ejemplo")
'''

B6 = T.CODIGO_2.replace(
    "#@title Bloque 2 · Formulario del mapa (si no usas la línea de Gemini)",
    "#@title ▶ Bloque 6 · (Opcional) Formulario: hace lo mismo que el Bloque 5, sin escribir código")
B6 = B6.replace("#@markdown Copia aquí la tabla que te entregó Gemini.",
                "#@markdown Copia aquí los valores de la línea que te entregó Gemini (sin comillas).")

B7 = ('#@title ▶ Bloque 7 · Descargar todos tus mapas en un zip { display-mode: "form" }\n'
      + requiere("hacer_mapa", "el Bloque 3") + '''import zipfile
imagenes = sorted(CARPETA_SALIDA.glob("*.jpg"))
if not imagenes:
    avisar("Todavía no hay mapas. Ejecuta el <b>Bloque 5</b> (o el 6) para crear uno.")
destino = CARPETA_SALIDA.parent / "mis_mapas.zip"
with zipfile.ZipFile(destino, "w") as z:
    for img in imagenes:
        z.write(img, arcname=img.name)
caja("ok", f"{len(imagenes)} archivos en mis_mapas.zip", "<br>".join(i.name for i in imagenes))
try:
    from google.colab import files
    files.download(str(destino))
except ImportError:
    pass
''')

# ---------------------------------------------------------------- textos (markdown)
INTRO = """# 🗺️ Desafío para seguir aprendiendo
## Tu propio mapa del Censo 2024, con ayuda de Gemini

**Magíster en Metodologías Críticas para la Investigación Social** · Docente: Benjamín Julio · Datos: INE, Censo 2024

No necesitas saber programar. Vas a avanzar **bloque por bloque**, de arriba hacia abajo:

| Bloque | Qué hace | Tiempo |
|:--:|---|:--:|
| **1** | Prepara Colab | 30 s |
| **2** | Descarga los datos del Censo | 1–3 min |
| **3** | Prepara el diccionario y la herramienta de mapas | 10 s |
| **4** | Te ayuda a armar tu mensaje para **Gemini** | 5 min |
| **5** | Hace **tu mapa** con la línea que te da Gemini | 1–2 min |
| 6 | *(Opcional)* Formulario: lo mismo que el 5, sin código | — |
| **7** | Descarga todos tus mapas en un zip | 10 s |

### Antes de empezar
1. Ve a **Archivo → Guardar una copia en Drive**. Trabaja siempre en esa copia.
2. Para ejecutar un bloque, pasa el mouse sobre él y presiona **▶** a la izquierda.
3. La primera vez Colab dirá *«Este notebook no fue creado por Google»*: elige **Ejecutar de todos modos**.

### Cómo leer los mensajes
✅ **Verde:** todo salió bien, sigue al próximo bloque. · ℹ️ **Azul:** información útil. · ⚠️ **Amarillo:** revisa lo que dice, corrige y vuelve a presionar ▶.

Guía con imágenes: [Guía ilustrada de Colab y Gemini](https://benjajul.github.io/clase-mapeo-censo/guia-colab.html)
"""

MD = {
    "B1": """---
## Paso 1 · Preparar Colab
**Qué hace:** instala lo necesario para hacer mapas.
**Qué debes ver:** un recuadro **verde** que dice *«Bloque 1 listo»*.
**Tiempo:** unos 30 segundos.""",
    "B2": """---
## Paso 2 · Descargar los datos del Censo 2024
**Qué hace:** trae la base del Censo 2024 por manzana desde la carpeta del docente.
**Qué debes ver:** un recuadro **verde** con el número de manzanas y comunas.
**Tiempo:** entre 1 y 3 minutos la primera vez. Si aparece un error de descarga, revisa la sección *Si la descarga falla* de la guía.""",
    "B3": """---
## Paso 3 · Preparar el diccionario y la herramienta de mapas
**Qué hace:** ordena el diccionario de variables del INE y deja lista la herramienta `hacer_mapa(...)`.
**Qué debes ver:** un recuadro **verde** que dice *«Bloque 3 listo»*.
**Tiempo:** unos segundos.""",
    "B4": """---
## Paso 4 · Arma tu mensaje para Gemini
**Qué hace:** muestra un armador donde respondes, con tus palabras, **qué** quieres mapear, **dónde**, si lo **cruzas** con otro tema, tu pregunta y tu nombre.

**Qué haces tú:**
1. Responde las preguntas (o toca una de las ideas).
2. Presiona **📋 Copiar mensaje para Gemini** (ya incluye el diccionario).
3. Abre **✦ Gemini** (arriba a la derecha de Colab), pega con **Ctrl + V** y presiona **Enter**.
4. Gemini te responderá con **una línea** que empieza con `hacer_mapa(`. Revisa la *Parte 1*: ¿entendió lo que querías?""",
    "B5": """---
## Paso 5 · Tu mapa
**Qué haces tú:** en el bloque de abajo, borra la línea de ejemplo, **pega la línea que te dio Gemini** y presiona **▶**.
*(Si Gemini te muestra un botón para ejecutar o insertar el código, también puedes usarlo.)*

**Qué debes ver:** un recuadro **verde** con el territorio elegido, luego el **mapa** y el **gráfico**. Ambos se descargan solos.
Si aparece un recuadro **amarillo**, cópialo en Gemini y pídele la línea corregida.

**¿Otro mapa?** Pega otra línea y vuelve a presionar ▶: puedes hacer todos los que quieras.""",
    "B6": """---
## Paso 6 · *(Opcional)* Formulario
Si prefieres no pegar código, completa este formulario con los valores de la línea de Gemini y presiona ▶. Hace exactamente lo mismo que el Paso 5.""",
    "B7": """---
## Paso 7 · Descargar todos tus mapas
**Qué hace:** junta en un zip todos los mapas y gráficos que hiciste y lo descarga.
**Tiempo:** unos segundos. Si el navegador pregunta, elige **Permitir**.

🎉 **¡Listo!** Si quieres, comparte tu mapa con el docente con un párrafo sobre lo que muestra y lo que no.""",
}

BLOQUES = [("B1", B1, True), ("B2", B2, True), ("B3", B3, True), ("B4", B4, True),
           ("B5", B5, False), ("B6", B6, True), ("B7", B7, True)]

# Para el notebook del docente: preparación completa sin armador
PREPARAR = (importaciones + ayudantes + descarga + catalogo + diccionario + funcion)
