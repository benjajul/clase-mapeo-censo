INTRO = """# Desafío para seguir aprendiendo · Tu propio mapa del Censo 2024 con apoyo de IA
**Magíster en Metodologías Críticas para la Investigación Social** · Docente: Benjamín Julio · Datos: INE, Censo 2024

Este notebook tiene **solo dos bloques**. No necesitas programar:

| Paso | Qué haces | Dónde |
|---|---|---|
| 1 | Ejecuta el **Bloque 1** (▶). Carga los datos y, al final, muestra el **armador del mensaje para Gemini**. | Aquí |
| 2 | Responde las preguntas del armador con tus palabras y presiona **Copiar mensaje para Gemini**. | Aquí |
| 3 | Abre **✦ Gemini** (arriba a la derecha), pega el mensaje (Ctrl + V) y presiona Enter. Gemini te devuelve **una línea** `hacer_mapa(...)`. | Panel de Gemini |
| 4 | Ejecuta esa línea desde el chat (o cópiala en una celda nueva y presiona ▶). Se descargan el **mapa** y el **gráfico** en JPEG. | Aquí |

El **Bloque 2** es un formulario opcional que hace lo mismo, por si prefieres escribir los valores a mano.

Antes de empezar: *Archivo → Guardar una copia en Drive*. Guía paso a paso: [Guía ilustrada de Colab y Gemini](https://benjajul.github.io/clase-mapeo-censo/guia-colab.html). Si algo falla, vuelve a ejecutar el Bloque 1 y luego el 2.
"""

TITULO_1 = "Bloque 1 · Preparar el entorno y cargar los datos (no se modifica)"
EXPL_1 = """Presiona ▶ y espera el recuadro verde **Listo** (1 a 3 minutos la primera vez). No necesitas cambiar nada.
Al final del resultado aparece el **armador del mensaje para Gemini**: responde las preguntas con tus palabras,
presiona **Copiar mensaje para Gemini**, abre **✦ Gemini** (arriba a la derecha de Colab), pega y presiona Enter.
Gemini te devolverá una línea `hacer_mapa(...)` para ejecutar."""

CODIGO_1 = r'''#@title Bloque 1 · Preparar el entorno y cargar los datos { display-mode: "form" }
# Este bloque NO se modifica. Ejecútalo con ▶ y espera el mensaje "Listo".
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown", "mapclassify", "contextily", "adjustText"],
               check=False)

import json, re, unicodedata, zipfile, difflib, warnings
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd, pyarrow.parquet as pq
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

FUENTE = "docente"
CARPETA_DOCENTE = "https://drive.google.com/drive/folders/1qzYq0RzuFlMieopEV03JyfpTOxxxWjij"
CARPETA_DATOS = Path("/content/datos")
CARPETA_SALIDA = Path("/content/resultados")
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

# 1. Descargar los datos (solo la primera vez)
if FUENTE == "docente" and not any(CARPETA_DATOS.rglob("*.parquet")):
    try:
        import gdown
        gdown.download_folder(CARPETA_DOCENTE, output=str(CARPETA_DATOS), quiet=True)
    except Exception:
        print("La descarga automática falló (Google limita descargas simultáneas).\n"
              "Uso la copia de tu Drive: Mi unidad/censo2024 (ver la guía de Colab).")
        FUENTE = "drive"
if FUENTE == "drive":
    from google.colab import drive
    drive.mount("/content/drive")
    CARPETA_DATOS = Path("/content/drive/MyDrive/censo2024")
for z in CARPETA_DATOS.rglob("*.zip"):
    if not any(z.parent.rglob("*.parquet")):
        zipfile.ZipFile(z).extractall(z.parent)

parquets = sorted(CARPETA_DATOS.rglob("*.parquet"))
RUTA_MANZANAS = next(p for p in parquets if "manzana" in p.name.lower())
RUTA_COMUNAS = next((p for p in parquets if "comuna" in p.name.lower()), None)

# 2. Columnas de la base de manzanas
esquema = pq.read_schema(RUTA_MANZANAS)
COL_GEOM = json.loads(esquema.metadata[b"geo"])["primary_column"]
COLUMNAS = [c for c in esquema.names if c != COL_GEOM]

def normalizar(texto):
    # Mayúsculas, sin tildes ni signos: "Ñuñoa" → "NUNOA"
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return " ".join(re.sub(r"[^A-Z0-9 ]", " ", t).split())

from IPython.display import HTML, display

ESTILOS = {"ok": ("#e6f4ea", "#2f9e44", "✓"), "info": ("#e7f1fb", "#1c7ed6", "i"),
           "revisa": ("#fff4d6", "#e67700", "!"), "ojo": ("#fff4d6", "#e67700", "!")}

def caja(tipo, titulo, cuerpo=""):
    # Recuadro de color legible en Colab (tema claro u oscuro)
    fondo, borde, icono = ESTILOS[tipo]
    display(HTML(
        f'<div style="background:{fondo};color:#1f2329;border-left:6px solid {borde};border-radius:8px;'
        f'padding:12px 16px;margin:8px 0;font-family:system-ui,Arial,sans-serif;font-size:14px;line-height:1.5">'
        f'<b style="color:{borde}">{icono} {titulo}</b>'
        + (f'<div style="margin-top:4px">{cuerpo}</div>' if cuerpo else "") + "</div>"))

class Revisa(Exception):
    # Detiene el bloque sin mostrar el error técnico de Python
    def _render_traceback_(self):
        return []

def avisar(mensaje):
    caja("revisa", "Revisa esto y vuelve a intentarlo", mensaje)
    raise Revisa()

def limpiar(texto):
    return str(texto).strip()

def cut5(serie):
    return serie.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)

# 3. Catálogo territorial: regiones, provincias y comunas
PROVINCIAS = {
    "011": "Iquique", "014": "Tamarugal", "021": "Antofagasta", "022": "El Loa", "023": "Tocopilla",
    "031": "Copiapó", "032": "Chañaral", "033": "Huasco", "041": "Elqui", "042": "Choapa", "043": "Limarí",
    "051": "Valparaíso", "052": "Isla de Pascua", "053": "Los Andes", "054": "Petorca", "055": "Quillota",
    "056": "San Antonio", "057": "San Felipe de Aconcagua", "058": "Marga Marga",
    "061": "Cachapoal", "062": "Cardenal Caro", "063": "Colchagua",
    "071": "Talca", "072": "Cauquenes", "073": "Curicó", "074": "Linares",
    "081": "Concepción", "082": "Arauco", "083": "Biobío", "091": "Cautín", "092": "Malleco",
    "101": "Llanquihue", "102": "Chiloé", "103": "Osorno", "104": "Palena",
    "111": "Coyhaique", "112": "Aysén", "113": "Capitán Prat", "114": "General Carrera",
    "121": "Magallanes", "122": "Antártica Chilena", "123": "Tierra del Fuego", "124": "Última Esperanza",
    "131": "Santiago", "132": "Cordillera", "133": "Chacabuco", "134": "Maipo", "135": "Melipilla",
    "136": "Talagante", "141": "Valdivia", "142": "Ranco", "151": "Arica", "152": "Parinacota",
    "161": "Diguillín", "162": "Itata", "163": "Punilla"}

cols_terr = [c for c in ("CUT", "COMUNA", "REGION", "PROVINCIA") if c in COLUMNAS]
CATALOGO = pd.read_parquet(RUTA_MANZANAS, columns=cols_terr)
CATALOGO["CUT"] = cut5(CATALOGO["CUT"])
if "PROVINCIA" not in CATALOGO:
    cod = CATALOGO["CUT"].str[:3]
    CATALOGO["PROVINCIA"] = cod.map(PROVINCIAS).fillna("Provincia " + cod)
CATALOGO = (CATALOGO.groupby(["REGION", "PROVINCIA", "COMUNA", "CUT"], as_index=False)
            .agg(manzanas=("CUT", "size")).sort_values("CUT"))
CATALOGO["COD_PROV"] = CATALOGO["CUT"].str[:3]
CATALOGO["COD_REG"] = CATALOGO["CUT"].str[:2]

# Nombres que se repiten en más de un nivel (ej.: Santiago es comuna, provincia y parte del nombre de la región)
NIVELES = {"Comunal": ("COMUNA", "CUT"), "Provincial": ("PROVINCIA", "COD_PROV"), "Regional": ("REGION", "COD_REG")}
def sin_prefijo(nombre):
    n = normalizar(nombre)
    for pref in ("METROPOLITANA DE ", "DEL ", "DE "):
        n = n[len(pref):] if n.startswith(pref) else n
    return n
indice_nombres = {}
for escala_, (col, cod) in NIVELES.items():
    for nombre, codigo in CATALOGO[[col, cod]].drop_duplicates().itertuples(index=False):
        indice_nombres.setdefault(sin_prefijo(nombre), []).append((escala_, nombre, codigo))
AMBIGUOS = {k: v for k, v in indice_nombres.items() if len({e for e, _, _ in v}) > 1}

# 4. Diccionario de variables del INE (archivo con "diccionario" en el nombre)
URL_DICCIONARIO = ("https://raw.githubusercontent.com/benjajul/clase-mapeo-censo/main/datos/"
                   "diccionario_variables_glosas_censo2024.xlsx")
archivos_dic = [p for p in CARPETA_DATOS.rglob("*.xls*") if "diccionario" in p.name.lower()]
if not archivos_dic:   # respaldo: copia publicada en el repositorio de la clase
    try:
        import urllib.request
        destino = CARPETA_DATOS / "diccionario_variables_glosas_censo2024.xlsx"
        CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL_DICCIONARIO, destino)
        archivos_dic = [destino]
    except Exception:
        pass

DICCIONARIO = None
for p in archivos_dic:
    for hoja in pd.read_excel(p, sheet_name=None).values():
        hoja.columns = [str(c).strip() for c in hoja.columns]
        if "Variable" in hoja.columns:   # la hoja con la lista de variables
            DICCIONARIO = hoja.dropna(subset=["Variable"])
            break

# Denominador sugerido según el universo de cada variable
UNIVERSOS = {
    "PERSONAS CENSADAS": "n_per",
    "HOGARES CENSADOS": "n_hog",
    "VIVIENDAS PARTICULARES OCUPADAS": "n_vp_ocupada",
    "VIVIENDAS PARTICULARES": "n_vp",
    "PERSONAS DE 15 ANOS O MAS OCUPADAS QUE TRABAJAN FUERA": "+".join(
        c for c in COLUMNAS if c.startswith("n_transporte_")),
    "PERSONAS DE 15 ANOS O MAS OCUPADAS": "n_ocupado",
    "PERSONAS DE 15 ANOS O MAS": "n_ocupado+n_desocupado+n_fuera_fuerza_trabajo",
    "PERSONAS DE 18 ANOS O MAS": "n_edad_18_24+n_edad_25_44+n_edad_45_59+n_edad_60_mas",
    "PERSONAS DE 5 ANOS O MAS": "n_per-n_edad_0_5",
    "PERSONAS DE 0 A 5 ANOS": "n_edad_0_5", "PERSONAS DE 6 A 13 ANOS": "n_edad_6_13",
    "PERSONAS DE 14 A 17 ANOS": "n_edad_14_17", "PERSONAS DE 18 A 24 ANOS": "n_edad_18_24"}

CORTOS = {"PERSONAS CENSADAS": "personas", "HOGARES CENSADOS": "hogares",
          "VIVIENDAS PARTICULARES OCUPADAS": "viviendas ocupadas", "VIVIENDAS PARTICULARES": "viviendas",
          "PERSONAS DE 15 ANOS O MAS OCUPADAS QUE TRABAJAN FUERA": "ocupados que trabajan fuera de casa",
          "PERSONAS DE 15 ANOS O MAS OCUPADAS": "ocupados (15+)", "PERSONAS DE 15 ANOS O MAS": "personas de 15+",
          "PERSONAS DE 18 ANOS O MAS": "personas de 18+", "PERSONAS DE 5 ANOS O MAS": "personas de 5+"}

def universo_corto(universo):
    u = normalizar(universo)
    return next((c for k, c in CORTOS.items() if u.startswith(k)), str(universo).lower())

def denominador_sugerido(universo):
    u = normalizar(universo)
    return next((d for clave, d in UNIVERSOS.items() if u.startswith(clave)), "")

# Valores automáticos para el Bloque 2 (denominador y nombre legible de cada variable)
SUGERIDOS, DESCRIPCIONES = {}, {}
if DICCIONARIO is not None and "Universo" in DICCIONARIO:
    for _, fila in DICCIONARIO.iterrows():
        SUGERIDOS[str(fila["Variable"]).strip()] = denominador_sugerido(fila["Universo"])
        DESCRIPCIONES[str(fila["Variable"]).strip()] = str(fila.get("Descripción", "")).strip()

TEXTO_IA = Path("/content/diccionario_para_IA.txt") if Path("/content").exists() else Path("diccionario_para_IA.txt")
with open(TEXTO_IA, "w", encoding="utf-8") as f:
    f.write("CENSO 2024 (INE) · BASE POR MANZANA · DICCIONARIO PARA LA IA\n")
    en_dic = set(DICCIONARIO["Variable"].astype(str).str.strip()) if DICCIONARIO is not None else set()
    extra_cols = [c for c in COLUMNAS if c not in en_dic]
    if extra_cols:
        f.write("Otras columnas de la base (sin descripción): " + ", ".join(extra_cols) + "\n")
    if DICCIONARIO is not None:
        d = DICCIONARIO[~DICCIONARIO.get("Tipo de variable", pd.Series("", index=DICCIONARIO.index))
                        .astype(str).str.contains("Identificador")].copy()
        if "Universo" in d:
            d["Denominador sugerido"] = d["Universo"].map(denominador_sugerido)
            d["Universo"] = d["Universo"].map(universo_corto)
        tema_actual = None
        f.write("DICCIONARIO DE VARIABLES (variable | descripción | universo | denominador sugerido)\n")
        for _, fila in d.iterrows():
            if fila.get("Temática") != tema_actual:
                tema_actual = fila.get("Temática"); f.write(f"\n## {tema_actual}\n")
            f.write(f"{fila['Variable']} | {fila.get('Descripción', '')} | {fila.get('Universo', '')} | "
                    f"{fila.get('Denominador sugerido', '')}\n")
    f.write("\nTERRITORIOS DE CHILE (en el campo TERRITORIO usa el CÓDIGO del nivel elegido: "
            "5 dígitos = comuna, 3 dígitos = provincia, 2 dígitos = región)\n")
    for (cr, reg), g_reg in CATALOGO.groupby(["COD_REG", "REGION"], sort=True):
        f.write(f"\nREGIÓN {cr} {reg}\n")
        for (cp, prov), g_prov in g_reg.groupby(["COD_PROV", "PROVINCIA"], sort=True):
            f.write(f"  Provincia {cp} {prov}: " + ", ".join(f"{c} {n}" for c, n in
                    zip(g_prov["CUT"], g_prov["COMUNA"])) + "\n")
    f.write("\nNOMBRES QUE SE REPITEN EN MÁS DE UN NIVEL (confirma el nivel antes de proponer el código):\n")
    for lista in AMBIGUOS.values():
        f.write(" / ".join(f"{e}: {n} = {c}" for e, n, c in lista) + "\n")

# 5. Resumen en pantalla
caja("ok", f"Listo: datos cargados ({CATALOGO['manzanas'].sum():,} manzanas y entidades en "
     f"{CATALOGO['CUT'].nunique()} comunas).",
     "<b>Siguiente paso:</b> baja hasta el <b>armador del mensaje para Gemini</b>, responde las preguntas "
     "y presiona <b>Copiar mensaje para Gemini</b>.")
if DICCIONARIO is None:
    caja("revisa", "No encontré el diccionario del INE",
         "El archivo para Gemini solo tiene la lista de columnas. Descarga el diccionario desde el sitio de la clase.")
caja("info", "Nombres repetidos",
     f"{len(AMBIGUOS)} nombres existen como comuna y también como provincia o región (por ejemplo: "
     + ", ".join(v[0][1].title() for v in list(AMBIGUOS.values())[:5]) + "). En el formulario conviene escribir el <b>código</b> del territorio.")
print("Regiones:", " · ".join(sorted(CATALOGO["REGION"].unique())))

# 6. La función que hace el mapa y el gráfico (la usan Gemini y el formulario del Bloque 2)
PARAMETROS = {"escala": None, "territorio": None, "variable_1": None, "denominador_1": "", "nombre_1": "",
              "variable_2": "", "denominador_2": "", "nombre_2": "", "titulo": "", "autor": "",
              "unidad": "Automática", "area": "Urbana y rural", "archivo": "", "descargar": "si"}
# Gran Santiago (como en la clase): Provincia de Santiago + Puente Alto + San Bernardo
GRAN_SANTIAGO = [f"131{n:02d}" for n in range(1, 33)] + ["13201", "13401"]

def hacer_mapa(**opciones):
    """Hace el mapa (JPEG) y el gráfico complementario. Ejemplo:
    hacer_mapa(escala="Comunal", territorio="05101", variable_1="n_edad_60_mas")"""
    try:
        valores = dict(PARAMETROS)
        for clave, valor in opciones.items():
            k = clave.lower()
            if k not in PARAMETROS:
                avisar(f"No conozco la opción «{clave}». Las opciones válidas son: {', '.join(PARAMETROS)}.")
            valores[k] = "" if valor is None else str(valor)
        faltan = [k for k in ("escala", "territorio", "variable_1") if not valores[k]]
        if faltan:
            avisar("Faltan datos obligatorios: " + ", ".join(faltan) + ".")
        valores["escala"] = valores["escala"].strip().capitalize()
        if valores["escala"] not in ("Regional", "Provincial", "Comunal"):
            avisar(f"La escala «{valores['escala']}» no existe: usa Regional, Provincial o Comunal.")
        _hacer_mapa(**{k.upper(): v for k, v in valores.items()})
    finally:
        plt.close("all")

def _hacer_mapa(ESCALA, TERRITORIO, VARIABLE_1, DENOMINADOR_1, NOMBRE_1, VARIABLE_2, DENOMINADOR_2, NOMBRE_2, TITULO, AUTOR, UNIDAD, AREA, ARCHIVO, DESCARGAR):

    import mapclassify, contextily as cx
    import matplotlib.colors as mcolors
    from matplotlib.patches import Patch
    from matplotlib.transforms import blended_transform_factory
    from adjustText import adjust_text

    MIN_PERSONAS = 20
    MAPA_BASE = cx.providers.Esri.WorldGrayCanvas
    PALETA_1 = ["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"]   # ColorBrewer OrRd, 5 clases
    PALETA_BI = {"1-1": "#e8e8e8", "2-1": "#e4acac", "3-1": "#c85a5a",
                 "1-2": "#b0d5df", "2-2": "#ad9ea5", "3-2": "#985356",
                 "1-3": "#64acbe", "2-3": "#627f8c", "3-3": "#574249"}   # J. Stevens
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})

    def bonito(nombre):
        # "VIÑA DEL MAR" → "Viña del Mar"
        menores = {"De", "Del", "La", "Las", "Los", "Y", "El"}
        palabras = str(nombre).title().split()
        return " ".join(p.lower() if i and p in menores else p for i, p in enumerate(palabras))

    # ---------- 1. Territorio ----------
    ES_GS = normalizar(TERRITORIO).replace(" ", "") in ("GRANSANTIAGO", "GS")
    if ES_GS:
        sel = CATALOGO[CATALOGO["CUT"].isin(GRAN_SANTIAGO)]
        CUTS = sel["CUT"].unique().tolist()
        NOMBRE_TERRITORIO, CODIGO_TERRITORIO = "GRAN SANTIAGO", "131 + 13201 + 13401"
        caja("ok", "Territorio elegido: Gran Santiago",
             f"Provincia de Santiago + Puente Alto + San Bernardo · {len(CUTS)} comunas")
    else:
        campo, campo_cod = NIVELES[ESCALA]
        largo_cod = {"Comunal": 5, "Provincial": 3, "Regional": 2}[ESCALA]
        opciones = CATALOGO[campo].unique()
        claves = {normalizar(o): o for o in opciones}
        buscado = normalizar(TERRITORIO)
        if buscado.isdigit():   # se escribió un código: CUT (5), provincia (3) o región (2)
            codigo = buscado.zfill(largo_cod) if len(buscado) < largo_cod else buscado
            if len(codigo) != largo_cod:
                avisar(f"El código '{TERRITORIO}' no corresponde a la escala {ESCALA}: se esperan {largo_cod} dígitos "
                       f"({'CUT de la comuna' if largo_cod == 5 else 'código de provincia' if largo_cod == 3 else 'código de región'}).")
            fila = CATALOGO[CATALOGO[campo_cod] == codigo]
            if fila.empty:
                avisar(f"No existe el código {codigo} en la escala {ESCALA}. Revisa la lista de territorios.")
            buscado = normalizar(fila[campo].iloc[0])
        elif buscado not in claves:
            parecidas = [o for o in opciones if buscado and buscado in normalizar(o)]
            if len(parecidas) == 1:
                buscado = normalizar(parecidas[0])
            else:
                sug = parecidas or difflib.get_close_matches(buscado, list(claves), n=5, cutoff=0.5)
                avisar(f"No encontré '{TERRITORIO}' en la escala {ESCALA}. ¿Quisiste decir: "
                       f"{', '.join(claves.get(s, s) for s in sug) or 'revisa la lista del Bloque 1'}?")
        NOMBRE_TERRITORIO = claves[buscado]
        sel = CATALOGO[CATALOGO[campo] == NOMBRE_TERRITORIO]
        CUTS = sel["CUT"].unique().tolist()
        CODIGO_TERRITORIO = sel[campo_cod].iloc[0]

        # Confirmación explícita del territorio elegido
        if ESCALA == "Comunal":
            detalle = f"Provincia {sel['PROVINCIA'].iloc[0].title()} · Región {sel['REGION'].iloc[0].title()}"
        elif ESCALA == "Provincial":
            detalle = f"Región {sel['REGION'].iloc[0].title()} · {len(CUTS)} comunas: " + ", ".join(sel["COMUNA"].str.title())
        else:
            detalle = f"{sel['COD_PROV'].nunique()} provincias y {len(CUTS)} comunas"
        nivel = {"Comunal": "Comuna", "Provincial": "Provincia", "Regional": "Región"}[ESCALA]
        caja("ok", f"Territorio elegido: {nivel} de {NOMBRE_TERRITORIO.title()} (código {CODIGO_TERRITORIO})", detalle)
        otros = [x for x in AMBIGUOS.get(sin_prefijo(NOMBRE_TERRITORIO), []) if x[0] != ESCALA]
        if otros:
            caja("ojo", "Ojo: este nombre también existe en otro nivel",
                 " · ".join(f"{e}: {bonito(n)} (código {c})" for e, n, c in otros)
                 + "<br>Si querías otro, cambia <b>ESCALA</b> o escribe ese código en <b>TERRITORIO</b>.")
    if UNIDAD == "Automática":
        UNIDAD_FINAL = {"Regional": "Comuna", "Comunal": "Manzana"}.get(ESCALA, "Comuna" if len(CUTS) >= 6 else "Manzana")
    else:
        UNIDAD_FINAL = UNIDAD
    if ESCALA == "Comunal" and UNIDAD_FINAL == "Comuna":
        UNIDAD_FINAL = "Manzana"
        print("En escala comunal la unidad es la manzana (una sola comuna no se puede comparar consigo misma).")

    # ---------- 2. Variables ----------
    def revisar(col, rol):
        col = limpiar(col)
        if not col:
            return ""
        if col in COLUMNAS:
            return col
        exacta = {c.lower(): c for c in COLUMNAS}.get(col.lower())
        if exacta:
            return exacta
        sug = difflib.get_close_matches(col, COLUMNAS, n=5, cutoff=0.4)
        avisar(f"El campo {rol}: '{col}' no existe en la base. Parecidas: {', '.join(sug) or '—'}. "
               "Copia el nombre exacto desde el diccionario (o pídeselo a Gemini).")

    def revisar_expresion(texto, rol):
        # Permite sumas y restas de columnas: "n_ocupado+n_desocupado" o "n_per-n_edad_0_5"
        texto = limpiar(texto).replace(" ", "")
        if not texto:
            return "", []
        partes = re.findall(r"([+-]?)([^+-]+)", texto)
        return texto, [(signo or "+", revisar(col, rol)) for signo, col in partes]

    def nombre_corto(texto, largo=48):
        # Nombre legible a partir de la descripción del diccionario, cortado en una palabra completa
        texto = " ".join(str(texto).split())
        if len(texto) <= largo:
            return texto
        return texto[:largo].rsplit(" ", 1)[0].rstrip(",:;") + "…"

    V1, V2 = revisar(VARIABLE_1, "variable 1"), revisar(VARIABLE_2, "variable 2")
    if not V1:
        avisar("Falta la VARIABLE_1: escribe qué quieres mapear (por ejemplo n_edad_60_mas).")
    # Completar automáticamente lo que quedó vacío
    autos = []
    if not limpiar(DENOMINADOR_1) and SUGERIDOS.get(V1):
        DENOMINADOR_1 = SUGERIDOS[V1]; autos.append(f"DENOMINADOR_1 = {DENOMINADOR_1}")
    if V2 and not limpiar(DENOMINADOR_2) and SUGERIDOS.get(V2):
        DENOMINADOR_2 = SUGERIDOS[V2]; autos.append(f"DENOMINADOR_2 = {DENOMINADOR_2}")
    if not limpiar(NOMBRE_1):
        NOMBRE_1 = nombre_corto(DESCRIPCIONES.get(V1) or V1); autos.append(f"NOMBRE_1 = {NOMBRE_1}")
    if V2 and not limpiar(NOMBRE_2):
        NOMBRE_2 = nombre_corto(DESCRIPCIONES.get(V2) or V2); autos.append(f"NOMBRE_2 = {NOMBRE_2}")
    if autos:
        caja("info", "Completé automáticamente (según el diccionario del INE)", "<br>".join(autos))

    D1 = revisar_expresion(DENOMINADOR_1, "denominador 1")
    D2 = revisar_expresion(DENOMINADOR_2, "denominador 2")
    ES_PROM = {v: v.lower().startswith("prom") for v in (V1, V2) if v}
    BIVARIADO = bool(V2)
    NOMBRE_1, NOMBRE_2 = limpiar(NOMBRE_1), limpiar(NOMBRE_2)
    for v, d in ((V1, D1), (V2, D2)):
        if v and v.lower().startswith("n_") and not d[0]:
            print(f"Nota: '{v}' es un conteo y no tiene denominador. Los conteos dependen del tamaño de la "
                  "población; considera usar una tasa (por ejemplo, denominador n_per).")


    # ---------- 3. Lectura y limpieza ----------
    cols_den = [c for _, c in D1[1] + D2[1]]
    extra = [c for c in ("AREA_C", "CONTENEDOR_COMUNAL") if c in COLUMNAS]
    necesarias = list(dict.fromkeys(c for c in ["CUT", "COMUNA", "n_per", V1, V2, *cols_den, *extra, COL_GEOM] if c))
    datos = gpd.read_parquet(RUTA_MANZANAS, columns=necesarias)
    if datos.geometry.name != "geometry":
        datos = datos.rename_geometry("geometry")
    datos["CUT"] = cut5(datos["CUT"])
    datos = datos[datos["CUT"].isin(CUTS)].copy()
    if AREA == "Solo urbana" and "AREA_C" in datos:
        datos = datos[pd.to_numeric(datos["AREA_C"], errors="coerce") == 1]
    numericas = [c for c in dict.fromkeys(["n_per", V1, V2, *cols_den]) if c]
    for c in numericas:
        datos[c] = pd.to_numeric(datos[c], errors="coerce")
        datos.loc[datos[c] < 0, c] = np.nan          # valores suprimidos por el INE
    # Denominadores compuestos (sumas o restas de columnas)
    for i, (texto, partes) in enumerate((D1, D2), start=1):
        if texto:
            datos[f"den_{i}"] = sum((1 if s == "+" else -1) * datos[c] for s, c in partes)
    D1, D2 = ("den_1" if D1[0] else ""), ("den_2" if D2[0] else "")
    D1_TXT, D2_TXT = DENOMINADOR_1.strip(), DENOMINADOR_2.strip()
    CRS_METROS = datos.estimate_utm_crs()
    datos = datos.to_crs(CRS_METROS)
    datos["geometry"] = datos.buffer(0)
    if "CONTENEDOR_COMUNAL" in datos:   # registros comunales sin geometría de manzana
        datos["contenedor"] = pd.to_numeric(datos["CONTENEDOR_COMUNAL"], errors="coerce").fillna(0) == 1
    else:
        datos["contenedor"] = False
    print(f"{NOMBRE_TERRITORIO}: {len(datos):,} manzanas en {datos['CUT'].nunique()} comuna(s). "
          f"Unidad de análisis: {UNIDAD_FINAL}.")

    def calcular(tabla, v, d):
        # Tasa: numerador / denominador × 100. Los promedios se usan tal como vienen.
        if d and not ES_PROM[v]:
            return tabla[v] / tabla[d].where(tabla[d] > 0) * 100
        return tabla[v]

    if UNIDAD_FINAL == "Manzana":
        unidades = datos[datos["n_per"] >= MIN_PERSONAS].copy()
        if "CONTENEDOR_COMUNAL" in unidades:   # registros comunales sin manzana: no se dibujan
            unidades = unidades[pd.to_numeric(unidades["CONTENEDOR_COMUNAL"], errors="coerce").fillna(0) != 1]
        unidades["valor_1"] = calcular(unidades, V1, D1)
        if BIVARIADO:
            unidades["valor_2"] = calcular(unidades, V2, D2)
        unidades["etiqueta"] = unidades["COMUNA"]
    else:
        agr = {}
        for v, d in ((V1, D1), (V2, D2)):
            if not v:
                continue
            if not ES_PROM[v]:
                agr[v] = (v, "sum")
                if d:
                    agr[d] = (d, "sum")
            else:   # promedio ponderado por su universo (denominador) o, si no hay, por población
                peso = datos[d] if d else datos["n_per"]
                datos[f"{v}_x_pob"] = datos[v] * peso
                datos[f"{v}_pob"] = peso.where(datos[v].notna())
                agr[f"{v}_x_pob"] = (f"{v}_x_pob", "sum"); agr[f"{v}_pob"] = (f"{v}_pob", "sum")
        agr["n_per"] = ("n_per", "sum")
        tabla = datos.groupby(["CUT", "COMUNA"], as_index=False).agg(**agr)
        for i, (v, d) in enumerate(((V1, D1), (V2, D2)), start=1):
            if v:
                tabla[f"valor_{i}"] = (tabla[f"{v}_x_pob"] / tabla[f"{v}_pob"]) if ES_PROM[v] else calcular(tabla, v, d)
        if RUTA_COMUNAS is not None:
            geo_c = gpd.read_parquet(RUTA_COMUNAS)
            if geo_c.geometry.name != "geometry":
                geo_c = geo_c.rename_geometry("geometry")
            geo_c["CUT"] = cut5(geo_c["CUT"])
            geo_c = geo_c[geo_c["CUT"].isin(CUTS)][["CUT", "geometry"]].to_crs(CRS_METROS)
        else:
            geo_c = datos.loc[~datos["contenedor"], ["CUT", "geometry"]].dissolve("CUT").reset_index()
        unidades = geo_c.merge(tabla, on="CUT")
        unidades["etiqueta"] = unidades["COMUNA"].map(lambda c: " ".join(
            p.lower() if i and p in ("De", "Del", "La", "Las", "Los", "El") else p
            for i, p in enumerate(str(c).title().split())))

    cols_valor = ["valor_1", "valor_2"] if BIVARIADO else ["valor_1"]
    unidades = unidades.replace([np.inf, -np.inf], np.nan)
    validas = unidades.dropna(subset=cols_valor).copy()
    if len(validas) < (9 if BIVARIADO else 5):
        avisar(f"Solo hay {len(validas)} unidades con datos: muy pocas para clasificar. "
               "Prueba la unidad 'Manzana' o una escala mayor.")
    print(f"Unidades con datos: {len(validas):,} de {len(unidades):,}.")

    # ---------- 4. Diseño cartográfico ----------
    comunas_borde = (gpd.read_parquet(RUTA_COMUNAS).pipe(lambda g: g.rename_geometry("geometry")
                     if g.geometry.name != "geometry" else g) if RUTA_COMUNAS is not None else None)
    if comunas_borde is not None:
        comunas_borde["CUT"] = cut5(comunas_borde["CUT"])
        comunas_borde = comunas_borde[comunas_borde["CUT"].isin(CUTS)].to_crs(CRS_METROS)
    else:
        comunas_borde = datos.loc[~datos["contenedor"], ["CUT", "geometry"]].dissolve("CUT").reset_index()

    xmin, ymin, xmax, ymax = validas.total_bounds
    mx, my = (xmax - xmin) * 0.04, (ymax - ymin) * 0.04
    xmin, xmax, ymin, ymax = xmin - mx, xmax + mx, ymin - my, ymax + my
    # Encuadre con proporción razonable (evita mapas demasiado altos o anchos)
    ancho, alto = xmax - xmin, ymax - ymin
    if alto / ancho > 1.6:
        extra = (alto / 1.6 - ancho) / 2; xmin, xmax = xmin - extra, xmax + extra
    elif alto / ancho < 0.55:
        extra = (ancho * 0.55 - alto) / 2; ymin, ymax = ymin - extra, ymax + extra

    ANCHO_MAPA, MARGEN_SUP, MARGEN_INF = 8.6, 0.9, 2.5

    def figura_mapa():
        alto_mapa = ANCHO_MAPA * (ymax - ymin) / (xmax - xmin)
        alto_fig = alto_mapa + MARGEN_SUP + MARGEN_INF
        fig = plt.figure(figsize=(10, alto_fig))
        ax = fig.add_axes([0.9 / 10, MARGEN_INF / alto_fig, ANCHO_MAPA / 10, alto_mapa / alto_fig])
        return fig, ax

    def bajo_el_mapa(ax, pulgadas):
        return -pulgadas / (ax.get_position().height * ax.figure.get_figheight())

    def largo_escala(ancho_m):
        # Largo "redondo" cercano a 1/5 del ancho del mapa
        objetivo = ancho_m / 5
        base = 10 ** np.floor(np.log10(objetivo))
        return max(m * base for m in (1, 2, 5) if m * base <= objetivo)

    zona = CRS_METROS.name.split("zone ")[-1] if "zone" in CRS_METROS.name else CRS_METROS.name

    def elementos_cartograficos(fig, ax, titulo, subtitulo):
        ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax); ax.set_aspect("equal")
        comunas_borde.boundary.plot(ax=ax, color="#444444", linewidth=0.5)
        try:
            cx.add_basemap(ax, crs=CRS_METROS, source=MAPA_BASE, attribution=False, zorder=0)
        except Exception as e:
            print("Sin mapa base (no afecta el resultado):", str(e)[:80])
        ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold", pad=22)
        ax.text(0, 1.01, subtitulo, transform=ax.transAxes, fontsize=9, color="dimgrey", va="bottom")
        ax.grid(True, linestyle=":", linewidth=0.5, color="grey")
        dec_km = 0 if (xmax - xmin) > 20_000 else 1
        ax.xaxis.set_major_formatter(lambda v, _: f"{v/1000:.{dec_km}f}")
        ax.yaxis.set_major_formatter(lambda v, _: f"{v/1000:.{dec_km}f}")
        ax.set_xlabel(f"Este (km, UTM {zona})", fontsize=8); ax.set_ylabel(f"Norte (km, UTM {zona})", fontsize=8)
        ax.tick_params(labelsize=7)
        for s in ax.spines.values():
            s.set_visible(True)
        # Escala gráfica bajo el mapa
        largo = largo_escala(xmax - xmin)
        t = blended_transform_factory(ax.transData, ax.transAxes)
        x0, y0 = xmin + 0.86 * (xmax - xmin) - largo, bajo_el_mapa(ax, 1.25)
        for i, color in enumerate(["black", "white", "black", "white"]):
            ax.add_patch(plt.Rectangle((x0 + i * largo / 4, y0), largo / 4, 0.012, transform=t, clip_on=False,
                                       facecolor=color, edgecolor="black", linewidth=0.8))
        fmt = (lambda m: f"{m/1000:g}") if largo >= 1000 else (lambda m: f"{m:g}")
        unidad_esc = "km" if largo >= 1000 else "m"
        for m in (0, largo / 2, largo):
            ax.text(x0 + m, y0 - 0.008, fmt(m) + (f" {unidad_esc}" if m == largo else ""), transform=t,
                    ha="center", va="top", fontsize=8)
        ax.annotate("N", xy=(0.95, bajo_el_mapa(ax, 0.8)), xytext=(0.95, bajo_el_mapa(ax, 1.6)),
                    xycoords="axes fraction", ha="center", va="center", fontsize=12, fontweight="bold",
                    arrowprops=dict(facecolor="black", width=4, headwidth=12), annotation_clip=False)
        nota = f" Manzanas con menos de {MIN_PERSONAS} personas excluidas." if UNIDAD_FINAL == "Manzana" else ""
        fig.text(0.09, 0.012,
                 f"Fuente: INE, Censo de Población y Vivienda 2024.{nota} Elaboración: {AUTOR}.\n"
                 f"Mapa base: {MAPA_BASE.attribution}. Proyección: WGS 84 / UTM {zona} (EPSG:{CRS_METROS.to_epsg()}).",
                 fontsize=7, color="dimgrey", va="bottom")

    ETQ_1 = f"{NOMBRE_1} (%)" if D1 and not ES_PROM[V1] else NOMBRE_1
    ETQ_2 = (f"{NOMBRE_2} (%)" if D2 and not ES_PROM[V2] else NOMBRE_2) if BIVARIADO else ""


    unidad_txt = "manzana o entidad censal" if UNIDAD_FINAL == "Manzana" else "comuna"
    if ES_GS:
        lugar = "Gran Santiago"
    elif ESCALA == "Regional":
        n = bonito(NOMBRE_TERRITORIO)
        lugar = ("Región " + n[0].lower() + n[1:]) if n.split()[0] in ("De", "Del") else \
                ("Región " + n if n.startswith("Metropolitana") else "Región de " + n)
    else:
        lugar = {"Provincial": "Provincia de", "Comunal": "Comuna de"}[ESCALA] + " " + bonito(NOMBRE_TERRITORIO)
    archivo_base = normalizar(ARCHIVO or f"{V1}{'_' + V2 if BIVARIADO else ''}_{NOMBRE_TERRITORIO}").lower().replace(" ", "_")

    fig, ax = figura_mapa()
    if not BIVARIADO:
        k = min(5, validas["valor_1"].nunique())
        clases = mapclassify.Quantiles(validas["valor_1"], k=k)
        colores = PALETA_1 if k == 5 else [mcolors.to_hex(c) for c in plt.get_cmap("OrRd", k + 1)(range(1, k + 1))]
        validas["color"] = [colores[c] for c in clases.yb]
        limites = [validas["valor_1"].min(), *clases.bins]
        validas.plot(color=validas["color"].tolist(), linewidth=0.15 if UNIDAD_FINAL == "Comuna" else 0,
                     edgecolor="white", alpha=0.9, ax=ax)
        sin_dato = unidades[unidades["valor_1"].isna()]
        if UNIDAD_FINAL == "Comuna" and len(sin_dato):
            sin_dato.plot(ax=ax, facecolor="none", edgecolor="grey", hatch="///", linewidth=0.3)
        titulo = limpiar(TITULO) or f"{NOMBRE_1}: {lugar}"
        elementos_cartograficos(fig, ax, titulo, f"{ETQ_1} por {unidad_txt}, {lugar}")
        dec = 1 if (validas["valor_1"].max() - validas["valor_1"].min()) < 1000 else 0
        cuadros = [Patch(facecolor=c, edgecolor="none", label=f"{limites[i]:,.{dec}f} – {limites[i + 1]:,.{dec}f}")
                   for i, c in enumerate(colores)]
        ax.legend(handles=cuadros, title=f"{ETQ_1}\nquintiles por {unidad_txt}",
                  loc="upper left", bbox_to_anchor=(0, bajo_el_mapa(ax, 0.6)), frameon=False, fontsize=8.5,
                  title_fontsize=9, alignment="left")
    else:
        tx = pd.qcut(validas["valor_1"].rank(method="first"), 3, labels=False) + 1
        ty = pd.qcut(validas["valor_2"].rank(method="first"), 3, labels=False) + 1
        validas["clase"] = tx.astype(int).astype(str) + "-" + ty.astype(int).astype(str)
        validas["color"] = validas["clase"].map(PALETA_BI)
        validas.plot(color=validas["color"].tolist(), linewidth=0.15 if UNIDAD_FINAL == "Comuna" else 0,
                     edgecolor="white", alpha=0.9, ax=ax)
        titulo = limpiar(TITULO) or f"{NOMBRE_1} y {NOMBRE_2.lower()}: {lugar}"
        elementos_cartograficos(fig, ax, titulo,
                                f"Terciles de {ETQ_1.lower()} y de "
                                f"{ETQ_2.lower()} por {unidad_txt}")
        lado = 1.1
        alto_mapa = ax.get_position().height * fig.get_figheight()
        ax_ley = ax.inset_axes([0.45 / ANCHO_MAPA, bajo_el_mapa(ax, 0.75 + lado), lado / ANCHO_MAPA, lado / alto_mapa])
        for clave, color in PALETA_BI.items():
            x, y = (int(v) for v in clave.split("-"))
            ax_ley.add_patch(plt.Rectangle((x - 1, y - 1), 1, 1, facecolor=color, edgecolor="white", linewidth=1))
        ax_ley.set_xlim(0, 3); ax_ley.set_ylim(0, 3); ax_ley.set_aspect("equal")
        ax_ley.set_xticks([]); ax_ley.set_yticks([])
        for s in ax_ley.spines.values():
            s.set_visible(False)
        corto = lambda s: s if len(s) <= 17 else s[:16] + "…"
        ax_ley.set_xlabel(f"{corto(NOMBRE_1)} →", fontsize=7, labelpad=2)
        ax_ley.set_ylabel(f"{corto(NOMBRE_2)} →", fontsize=7, labelpad=2)
        ax.text(0.45 / ANCHO_MAPA + lado / ANCHO_MAPA + 0.05, bajo_el_mapa(ax, 0.95),
                f"Oscuro: alto en ambas\nRojo: más {corto(NOMBRE_1).lower()}\n"
                f"Azul: más {corto(NOMBRE_2).lower()}\nGris claro: bajo en ambas",
                transform=ax.transAxes, fontsize=7.5, va="top", color="dimgrey", linespacing=1.6)

    RUTA_MAPA = CARPETA_SALIDA / f"mapa_{archivo_base}.jpg"
    fig.savefig(RUTA_MAPA, dpi=300, pil_kwargs={"quality": 92})
    plt.show()

    # ---------- 5. Gráfico complementario ----------
    GRIS, ACENTO = "#555555", "#b30000"
    fig2, ax2 = plt.subplots(figsize=(9, 6))
    fuente_g = f"Fuente: INE, Censo 2024. Elaboración: {AUTOR}."
    if not BIVARIADO and UNIDAD_FINAL == "Comuna":
        # Ranking: barras horizontales ordenadas, con el valor del territorio como referencia
        orden = validas.sort_values("valor_1")
        if len(orden) > 30:
            orden = pd.concat([orden.head(15), orden.tail(15)])
        barras = ax2.barh(orden["etiqueta"], orden["valor_1"], color=orden["color"], edgecolor="#999999", linewidth=0.4)
        ax2.bar_label(barras, labels=[f"{v:,.1f}" for v in orden["valor_1"]], padding=3, fontsize=7.5, color=GRIS)
        if D1 and not ES_PROM[V1]:
            ref = unidades[V1].sum() / unidades[D1].sum() * 100
        else:
            ref = np.average(validas["valor_1"], weights=validas["n_per"].clip(lower=1))
        ax2.axvline(ref, color=GRIS, linestyle="--", linewidth=1)
        ax2.text(ref, 1.0, f"{lugar}: {ref:,.1f}", color=GRIS, fontsize=8, va="bottom", ha="center",
                 transform=blended_transform_factory(ax2.transData, ax2.transAxes))
        ax2.set_xlabel(ETQ_1); ax2.tick_params(axis="y", labelsize=8)
        ax2.set_title(f"{NOMBRE_1} por comuna", loc="left", fontweight="bold")
        tipo_grafico = "ranking"
    elif not BIVARIADO:
        # Distribución: histograma coloreado con las mismas clases del mapa
        n_bins = 40
        cuentas, bordes, barras = ax2.hist(validas["valor_1"], bins=n_bins, edgecolor="white", linewidth=0.4)
        for b, izq, der in zip(barras, bordes[:-1], bordes[1:]):
            b.set_facecolor(colores[min(np.searchsorted(clases.bins, (izq + der) / 2), len(colores) - 1)])
        med = validas["valor_1"].median()
        ax2.axvline(med, color=GRIS, linestyle="--", linewidth=1)
        ax2.text(med, 0.98, f" mediana: {med:,.1f}", color=GRIS, fontsize=8, va="top",
                 transform=blended_transform_factory(ax2.transData, ax2.transAxes))
        ax2.set_xlabel(ETQ_1); ax2.set_ylabel("Número de manzanas o entidades")
        ax2.set_title(f"Distribución de {NOMBRE_1.lower()} por manzana", loc="left", fontweight="bold")
        tipo_grafico = "distribucion"
    else:
        # Dispersión: cada unidad con el color de su clase bivariada y líneas de terciles
        tam = (validas["n_per"] / validas["n_per"].max() * 600 + 15) if UNIDAD_FINAL == "Comuna" else 8
        ax2.scatter(validas["valor_1"], validas["valor_2"], s=tam, c=validas["color"],
                    edgecolor="white" if UNIDAD_FINAL == "Comuna" else "none", linewidth=0.6,
                    alpha=0.95 if UNIDAD_FINAL == "Comuna" else 0.7)
        for q in validas["valor_1"].quantile([1/3, 2/3]):
            ax2.axvline(q, color="#bbbbbb", linestyle=":", linewidth=1)
        for q in validas["valor_2"].quantile([1/3, 2/3]):
            ax2.axhline(q, color="#bbbbbb", linestyle=":", linewidth=1)
        r = validas[["valor_1", "valor_2"]].corr().iloc[0, 1]
        if UNIDAD_FINAL == "Comuna" and len(validas) <= 60:
            textos = [ax2.text(x, y, e, fontsize=7.5, color="#333333")
                      for x, y, e in zip(validas["valor_1"], validas["valor_2"], validas["etiqueta"])]
            adjust_text(textos, ax=ax2, arrowprops=dict(arrowstyle="-", color="grey", lw=0.5))
        ax2.set_xlabel(ETQ_1); ax2.set_ylabel(ETQ_2)
        ax2.set_title(f"{NOMBRE_1} y {NOMBRE_2.lower()} por {unidad_txt}", loc="left", fontweight="bold")
        fuente_g = (f"Correlación de Pearson r = {r:.2f}. Líneas punteadas: terciles"
                    + (" · tamaño del círculo: población. " if UNIDAD_FINAL == "Comuna" else ". ") + fuente_g)
        tipo_grafico = "dispersion"
    ax2.grid(axis="x" if tipo_grafico == "ranking" else "both", color="#e5e5e5", linewidth=0.6)
    ax2.set_axisbelow(True)
    fig2.text(0.01, 0.005, f"{lugar}. {fuente_g}", fontsize=7, color="dimgrey")
    fig2.tight_layout(rect=(0, 0.03, 1, 1))
    RUTA_GRAFICO = CARPETA_SALIDA / f"grafico_{archivo_base}.jpg"
    fig2.savefig(RUTA_GRAFICO, dpi=300, pil_kwargs={"quality": 92})
    plt.show()

    # ---------- 6. Resumen y descarga ----------
    resumen = validas[["etiqueta"] + cols_valor].describe().round(2)
    print("Resumen de los valores mapeados:"); display(resumen)
    print(f"Archivos: {RUTA_MAPA.name} · {RUTA_GRAFICO.name}")
    if normalizar(DESCARGAR) not in ("NO", "FALSE", "0"):
        try:
            from google.colab import files
            files.download(str(RUTA_MAPA)); files.download(str(RUTA_GRAFICO))
        except ImportError:
            pass

# 7. Armador del mensaje para Gemini (con el diccionario incluido)
ARMADOR = r"""__ARMADOR_HTML__"""
display(HTML(ARMADOR.replace('"__DICCIONARIO_JSON__"',
                             json.dumps(TEXTO_IA.read_text(encoding="utf-8"), ensure_ascii=False))))

'''

TITULO_2 = "Bloque 2 · (Opcional) Formulario manual"
EXPL_2 = """**Solo si no usaste la línea de Gemini.** Este formulario hace exactamente lo mismo que `hacer_mapa(...)`:
copia en cada campo los valores de la línea que te dio Gemini (sin comillas) y presiona ▶.
Solo son obligatorios los campos marcados con ★; lo que dejes vacío lo completa el código con el diccionario del INE."""

CODIGO_2 = r'''#@title Bloque 2 · Formulario del mapa (si no usas la línea de Gemini) { display-mode: "form" }
#@markdown Copia aquí la tabla que te entregó Gemini. **Solo son obligatorios los campos marcados con ★**; lo que dejes vacío lo completa el código.

#@markdown ### ★ ¿Dónde? · Nivel y territorio
#@markdown Nivel: Regional, Provincial o Comunal. Territorio: el código (13101 = comuna de Santiago · 131 = provincia · 13 = región) o el nombre.
ESCALA = "Comunal" #@param ["Regional", "Provincial", "Comunal"]
TERRITORIO = "05101" #@param {type:"string"}

#@markdown ### ★ ¿Qué quieres mapear?
#@markdown Nombre de la variable del Censo (empieza con n_ o prom_). Si dejas vacío el denominador, se usa el sugerido por el diccionario.
VARIABLE_1 = "n_edad_60_mas" #@param {type:"string"}
DENOMINADOR_1 = "" #@param {type:"string"}
NOMBRE_1 = "" #@param {type:"string"}

#@markdown ### ¿Lo cruzas con otro tema? (opcional)
#@markdown Déjalo vacío para un mapa de un solo tema. Si lo completas, se hace un mapa bivariado.
VARIABLE_2 = "" #@param {type:"string"}
DENOMINADOR_2 = "" #@param {type:"string"}
NOMBRE_2 = "" #@param {type:"string"}

#@markdown ### Textos del mapa (opcional)
TITULO = "" #@param {type:"string"}
AUTOR = "Nombre Apellido" #@param {type:"string"}

#@markdown ### Opciones avanzadas (puedes no tocarlas)
UNIDAD = "Automática" #@param ["Automática", "Comuna", "Manzana"]
AREA = "Urbana y rural" #@param ["Urbana y rural", "Solo urbana"]
#@markdown ---
#@markdown *No modifiques el código de este bloque: todo se controla desde el formulario.*

hacer_mapa(escala=ESCALA, territorio=TERRITORIO, variable_1=VARIABLE_1, denominador_1=DENOMINADOR_1, nombre_1=NOMBRE_1, variable_2=VARIABLE_2, denominador_2=DENOMINADOR_2, nombre_2=NOMBRE_2, titulo=TITULO, autor=AUTOR, unidad=UNIDAD, area=AREA)

'''
