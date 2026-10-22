INTRO = """# Tarea · Cartografía censal de Chile con apoyo de IA
**Magíster en Metodologías Críticas para la Investigación Social** · Docente: Benjamín Julio · Datos: INE, Censo 2024

Este notebook tiene **solo dos bloques**. No necesitas programar:

| Paso | Qué haces | Dónde |
|---|---|---|
| 1 | Ejecuta el **Bloque 1** (▶). Descarga los datos y te muestra el diccionario de variables. | Aquí |
| 2 | Copia el **prompt tipo** de la tarea y pégalo en **Gemini** junto al diccionario. Gemini te propone las variables y te devuelve los valores para el formulario. | Panel de Gemini |
| 3 | Completa el **formulario del Bloque 2** (a la derecha del bloque) con esos valores y ejecútalo (▶). | Aquí |
| 4 | Se descargan dos archivos: el **mapa en JPEG** y el **gráfico complementario**. Úsalos en tu informe. | Tu computador |

Antes de empezar: *Archivo → Guardar una copia en Drive*. Si algo falla, vuelve a ejecutar el Bloque 1 y luego el 2.
"""

TITULO_1 = "Bloque 1 · Preparar el entorno y cargar los datos (no se modifica)"
EXPL_1 = """Instala lo necesario, descarga la cartografía del Censo 2024 desde la carpeta compartida del docente y muestra:
las **regiones y provincias** disponibles, las **columnas** de la base y el **diccionario de variables**.
Además guarda `diccionario_para_IA.txt`, un resumen del diccionario listo para entregárselo a Gemini.
Tarda entre 1 y 3 minutos la primera vez."""

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

def denominador_sugerido(universo):
    u = normalizar(universo)
    return next((d for clave, d in UNIVERSOS.items() if u.startswith(clave)), "")

TEXTO_IA = Path("/content/diccionario_para_IA.txt") if Path("/content").exists() else Path("diccionario_para_IA.txt")
with open(TEXTO_IA, "w", encoding="utf-8") as f:
    f.write("COLUMNAS DISPONIBLES EN LA BASE DE MANZANAS (Censo 2024, INE):\n")
    f.write(", ".join(COLUMNAS) + "\n\n")
    if DICCIONARIO is not None:
        d = DICCIONARIO[~DICCIONARIO.get("Tipo de variable", pd.Series("", index=DICCIONARIO.index))
                        .astype(str).str.contains("Identificador")].copy()
        if "Universo" in d:
            d["Denominador sugerido"] = d["Universo"].map(denominador_sugerido)
        f.write("DICCIONARIO DE VARIABLES (Variable | Tipo | Descripción | Universo | Denominador sugerido):\n")
        f.write(d.drop(columns=["Temática"], errors="ignore").to_csv(sep="|", index=False))

# 5. Resumen en pantalla
print(f"Listo. {CATALOGO['manzanas'].sum():,} manzanas en {CATALOGO['CUT'].nunique()} comunas.\n")
print("REGIONES:", " · ".join(sorted(CATALOGO["REGION"].unique())), "\n")
print("PROVINCIAS:", " · ".join(sorted(CATALOGO["PROVINCIA"].unique())), "\n")
print(f"COLUMNAS DE LA BASE ({len(COLUMNAS)}):", ", ".join(COLUMNAS), "\n")
if DICCIONARIO is not None:
    print(f"DICCIONARIO: {archivos_dic[0].name} ({len(DICCIONARIO)} variables). Vista previa:")
    display(DICCIONARIO.drop(columns=["Temática"], errors="ignore").iloc[20:35])
else:
    print("No encontré el diccionario: descárgalo del sitio de la clase y súbelo a Gemini.")
print("\nSiguiente paso: entrega a Gemini el archivo diccionario_para_IA.txt (carpeta 📁 de la izquierda) "
      "junto con el prompt tipo.")
'''

TITULO_2 = "Bloque 2 · Tu mapa y tu gráfico (solo se completa el formulario)"
EXPL_2 = """Completa el **formulario** de la derecha con los valores que te propuso Gemini y ejecuta el bloque (▶).
El bloque hace solo todo el procesamiento:

1. **Filtra** el territorio elegido (región, provincia o comuna).
2. **Limpia**: los valores negativos (datos suprimidos por el INE) pasan a vacío y las manzanas con menos de 20
   personas se excluyen (números pequeños).
3. **Calcula** la tasa (numerador / denominador × 100) o usa el promedio tal como viene.
4. **Agrega** a la unidad de análisis: por **comuna** en escala regional; por **comuna o manzana** en escala
   provincial; por **manzana** en escala comunal.
5. **Clasifica** (quintiles para una variable; terciles 3 × 3 para dos variables) y dibuja un **mapa
   profesional**: título, subtítulo, leyenda, escala, norte, grilla, fuente y proyección.
6. Dibuja un **gráfico complementario** adecuado al caso y descarga ambos archivos en **JPEG**.

Si el territorio o una variable no existe, el bloque te sugiere los nombres más parecidos."""

CODIGO_2 = r'''#@title Bloque 2 · Formulario del mapa { display-mode: "form" }
#@markdown ### 1. Territorio
ESCALA = "Comunal" #@param ["Regional", "Provincial", "Comunal"]
TERRITORIO = "Valparaíso" #@param {type:"string"}
UNIDAD = "Automática" #@param ["Automática", "Comuna", "Manzana"]
AREA = "Urbana y rural" #@param ["Urbana y rural", "Solo urbana"]
#@markdown ### 2. Variable principal (eje X del mapa bivariado)
VARIABLE_1 = "n_edad_60_mas" #@param {type:"string"}
DENOMINADOR_1 = "n_per" #@param {type:"string"}
NOMBRE_1 = "Personas de 60 años y más" #@param {type:"string"}
#@markdown ### 3. Segunda variable (déjala vacía para un mapa de una sola variable)
VARIABLE_2 = "" #@param {type:"string"}
DENOMINADOR_2 = "" #@param {type:"string"}
NOMBRE_2 = "" #@param {type:"string"}
#@markdown ### 4. Textos del mapa
TITULO = "" #@param {type:"string"}
AUTOR = "Nombre Apellido" #@param {type:"string"}
#@markdown ---
#@markdown *No modifiques el código de este bloque: todo se controla desde el formulario.*

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

def avisar(mensaje):
    raise SystemExit("⚠️  " + mensaje)

def limpiar(texto):
    return str(texto).strip()

# ---------- 1. Territorio ----------
campo = {"Regional": "REGION", "Provincial": "PROVINCIA", "Comunal": "COMUNA"}[ESCALA]
opciones = CATALOGO[campo].unique()
claves = {normalizar(o): o for o in opciones}
buscado = normalizar(TERRITORIO)
if buscado not in claves:
    parecidas = [o for o in opciones if buscado and buscado in normalizar(o)]
    if len(parecidas) == 1:
        buscado = normalizar(parecidas[0])
    else:
        sug = parecidas or difflib.get_close_matches(buscado, list(claves), n=5, cutoff=0.5)
        avisar(f"No encontré '{TERRITORIO}' en la escala {ESCALA}. ¿Quisiste decir: "
               f"{', '.join(claves.get(s, s) for s in sug) or 'revisa la lista del Bloque 1'}?")
NOMBRE_TERRITORIO = claves[buscado]
CUTS = CATALOGO.loc[CATALOGO[campo] == NOMBRE_TERRITORIO, "CUT"].unique().tolist()
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
           "Copia el nombre exacto de la lista de columnas del Bloque 1.")

def revisar_expresion(texto, rol):
    # Permite sumas y restas de columnas: "n_ocupado+n_desocupado" o "n_per-n_edad_0_5"
    texto = limpiar(texto).replace(" ", "")
    if not texto:
        return "", []
    partes = re.findall(r"([+-]?)([^+-]+)", texto)
    return texto, [(signo or "+", revisar(col, rol)) for signo, col in partes]

V1, D1 = revisar(VARIABLE_1, "variable 1"), revisar_expresion(DENOMINADOR_1, "denominador 1")
V2, D2 = revisar(VARIABLE_2, "variable 2"), revisar_expresion(DENOMINADOR_2, "denominador 2")
ES_PROM = {v: v.lower().startswith("prom") for v in (V1, V2) if v}
if not V1:
    avisar("Falta la VARIABLE_1.")
BIVARIADO = bool(V2)
NOMBRE_1 = limpiar(NOMBRE_1) or V1
NOMBRE_2 = limpiar(NOMBRE_2) or V2
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

def bonito(nombre):
    # "VIÑA DEL MAR" → "Viña del Mar"
    menores = {"De", "Del", "La", "Las", "Los", "Y", "El"}
    palabras = str(nombre).title().split()
    return " ".join(p.lower() if i and p in menores else p for i, p in enumerate(palabras))

unidad_txt = "manzana o entidad censal" if UNIDAD_FINAL == "Manzana" else "comuna"
if ESCALA == "Regional":
    n = bonito(NOMBRE_TERRITORIO)
    lugar = ("Región " + n[0].lower() + n[1:]) if n.split()[0] in ("De", "Del") else \
            ("Región " + n if n.startswith("Metropolitana") else "Región de " + n)
else:
    lugar = {"Provincial": "Provincia de", "Comunal": "Comuna de"}[ESCALA] + " " + bonito(NOMBRE_TERRITORIO)
archivo_base = normalizar(f"{V1}{'_' + V2 if BIVARIADO else ''}_{NOMBRE_TERRITORIO}").lower().replace(" ", "_")

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
try:
    from google.colab import files
    files.download(str(RUTA_MAPA)); files.download(str(RUTA_GRAFICO))
except ImportError:
    pass
'''
