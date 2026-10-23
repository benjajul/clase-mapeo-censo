"""Ilustraciones esquemáticas (SVG) para la guía de Colab y Gemini."""
from pathlib import Path
OUT = Path("/home/claude/clase-mapeo-censo/img/guia")
OUT.mkdir(parents=True, exist_ok=True)

ACENTO = "#e8590c"; TINTA = "#212529"; GRIS = "#6c757d"; LINEA = "#ced4da"; FONDO = "#f8f9fa"; AZUL = "#1c7ed6"
VERDE = "#2f9e44"; MORADO = "#7048e8"
FUENTE = "font-family:system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif"

def svg(w, h, cuerpo, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{titulo}" '
            f'style="{FUENTE}"><title>{titulo}</title>'
            f'<defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACENTO}"/></marker></defs>'
            f'<rect width="{w}" height="{h}" fill="white"/>{cuerpo}</svg>')

def t(x, y, s, size=13, color=TINTA, peso="normal", ancla="start", estilo="normal"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{peso}" '
            f'text-anchor="{ancla}" font-style="{estilo}">{s}</text>')

def r(x, y, w, h, fill="white", stroke=LINEA, rx=6, sw=1.2, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def ventana(x, y, w, h, titulo):
    return (r(x, y, w, h, "white", "#adb5bd", 10, 1.5) +
            f'<path d="M{x} {y+10} a10 10 0 0 1 10 -10 h{w-20} a10 10 0 0 1 10 10 v22 h-{w} z" fill="#e9ecef"/>' +
            "".join(f'<circle cx="{x+16+i*16}" cy="{y+16}" r="5" fill="{c}"/>' for i, c in
                    enumerate(["#fa5252", "#fab005", "#40c057"])) +
            t(x + 70, y + 21, titulo, 12, GRIS))

def num(x, y, n):
    return (f'<circle cx="{x}" cy="{y}" r="13" fill="{ACENTO}"/>' + t(x, y + 5, n, 14, "white", "bold", "middle"))

def flecha(x1, y1, x2, y2, curva=0):
    if curva:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - curva
        d = f"M{x1},{y1} Q{mx},{my} {x2},{y2}"
    else:
        d = f"M{x1},{y1} L{x2},{y2}"
    return f'<path d="{d}" fill="none" stroke="{ACENTO}" stroke-width="2.5" marker-end="url(#fl)"/>'

def resalte(x, y, w, h):
    return r(x - 3, y - 3, w + 6, h + 6, "none", ACENTO, 7, 3)

OUT_OSCURO = OUT.parent / "guia_oscuro"
OUT_OSCURO.mkdir(parents=True, exist_ok=True)
OSCURO = {"#212529": "#e6e8eb", "#6c757d": "#9aa4b2", "#ced4da": "#3a414b", "#f8f9fa": "#232830",
          "#adb5bd": "#4a525e", "#e9ecef": "#2a3038", "#f1f3f5": "#1f242b", "#fff4e6": "#3b2616",
          "#f3f0ff": "#2a2440", "#495057": "#000000", "#1c7ed6": "#339af0", "#7048e8": "#9775fa",
          "#2f9e44": "#51cf66", "#e6f4ea": "#173a24", "#e7f1fb": "#16304a", "#fff4d6": "#3d3012"}

def a_oscuro(contenido):
    import re
    # Fondos blancos de rectángulos y círculos → superficie oscura (el texto blanco se mantiene)
    contenido = re.sub(r'(<(?:rect|circle)[^>]*?)fill="white"', r'\1fill="#1b1f26"', contenido)
    contenido = re.sub(r'<rect width="(\d+)" height="(\d+)" fill="#1b1f26"/>',
                       r'<rect width="\1" height="\2" fill="#14181e"/>', contenido, count=1)
    for claro, oscuro in OSCURO.items():
        contenido = contenido.replace(claro, oscuro)
    return contenido.replace('rgba(0,0,0,.15)', 'rgba(0,0,0,.5)').replace('rgba(0,0,0,.2)', 'rgba(0,0,0,.6)')

def guardar(nombre, contenido):
    (OUT / f"{nombre}.svg").write_text(contenido, encoding="utf-8")
    (OUT_OSCURO / f"{nombre}.svg").write_text(a_oscuro(contenido), encoding="utf-8")

# ---------------------------------------------------------------- 0. Recorrido
pasos = [("☁", "Abrir Colab", "desde el enlace", AZUL),
         ("▶", "Bloques 1–3", "preparar los datos", VERDE),
         ("✦", "Bloque 4", "mensaje + Gemini", MORADO),
         ("☰", "Bloque 5", "pegar la línea", VERDE),
         ("🗺", "Mapa y gráfico", "en JPEG", ACENTO)]
c = ""
for i, (ic, a, b, col) in enumerate(pasos):
    x = 20 + i * 150
    c += r(x, 40, 126, 130, FONDO, col, 14, 2)
    c += f'<circle cx="{x+63}" cy="82" r="26" fill="{col}"/>' + t(x + 63, 92, ic, 24, "white", "bold", "middle")
    c += t(x + 63, 133, a, 14, TINTA, "bold", "middle") + t(x + 63, 153, b, 12, GRIS, "normal", "middle")
    c += t(x + 63, 26, f"Paso {i+1}", 12, col, "bold", "middle")
    if i < 4:
        c += flecha(x + 128, 105, x + 148, 105)
c += t(380, 205, "Tiempo total aproximado: 20 a 30 minutos la primera vez", 13, GRIS, "normal", "middle", "italic")
guardar("00_recorrido", svg(760, 220, c, "Recorrido completo en cinco pasos"))

# ---------------------------------------------------------------- 1. Drive: + Nuevo → Más → Conectar
c = ventana(10, 10, 740, 330, "drive.google.com — Mi unidad")
c += r(30, 60, 92, 40, "white", "#adb5bd", 14) + t(76, 86, "+ Nuevo", 15, TINTA, "bold", "middle")
c += resalte(30, 60, 92, 40) + num(30, 58, "1")
menu = ["Carpeta nueva", "Subir archivo", "Subir carpeta", "Documentos", "Hojas de cálculo", "Más  ›"]
c += r(40, 110, 200, 30 * len(menu) + 10, "white", LINEA, 8, 1, 'filter="drop-shadow(0 2px 4px rgba(0,0,0,.15))"')
for i, m in enumerate(menu):
    c += t(58, 135 + i * 30, m, 13, TINTA if i == len(menu) - 1 else GRIS, "bold" if i == len(menu) - 1 else "normal")
c += resalte(46, 117 + 5 * 30, 188, 26) + num(238, 130 + 5 * 30, "2")
sub = ["Formularios", "Dibujos", "Mis mapas", "Conectar más aplicaciones"]
c += r(262, 220, 250, 30 * len(sub) + 10, "white", LINEA, 8, 1, 'filter="drop-shadow(0 2px 4px rgba(0,0,0,.15))"')
for i, m in enumerate(sub):
    c += t(280, 245 + i * 30, m, 13, TINTA if i == 3 else GRIS, "bold" if i == 3 else "normal")
c += resalte(268, 227 + 3 * 30, 238, 26) + num(516, 240 + 3 * 30, "3")
c += t(560, 120, "Haz clic en", 13, GRIS) + t(560, 140, "+ Nuevo → Más →", 13, TINTA, "bold")
c += t(560, 160, "Conectar más aplicaciones", 13, TINTA, "bold")
c += t(560, 190, "Se abre una tienda", 13, GRIS) + t(560, 208, "de aplicaciones.", 13, GRIS)
guardar("01_drive_conectar", svg(760, 350, c, "Google Drive: Nuevo, Más, Conectar más aplicaciones"))

# ---------------------------------------------------------------- 2. Tienda: buscar Colaboratory → Instalar
c = ventana(10, 10, 740, 300, "Conectar más aplicaciones")
c += r(40, 58, 420, 38, FONDO, "#adb5bd", 19) + t(62, 82, "🔍  Colaboratory", 15, TINTA)
c += resalte(40, 58, 420, 38) + num(40, 56, "1")
c += r(40, 120, 300, 160, "white", LINEA, 12)
c += r(60, 140, 54, 54, "#fff4e6", ACENTO, 12) + t(87, 175, "CO", 18, ACENTO, "bold", "middle")
c += t(128, 160, "Colaboratory", 16, TINTA, "bold") + t(128, 180, "Google", 12, GRIS)
c += t(60, 220, "Notebooks de Python en la nube", 12, GRIS)
c += r(60, 236, 110, 32, AZUL, AZUL, 16) + t(115, 257, "Instalar", 14, "white", "bold", "middle")
c += resalte(60, 236, 110, 32) + num(178, 252, "2")
c += t(380, 150, "Escribe Colaboratory en el buscador", 13, TINTA)
c += t(380, 172, "y elige la tarjeta de la aplicación.", 13, GRIS)
c += t(380, 214, "Presiona Instalar y luego Continuar /", 13, TINTA)
c += t(380, 236, "Permitir con tu cuenta de Google.", 13, GRIS)
c += t(380, 270, "✓ Listo: esto se hace una sola vez.", 13, VERDE, "bold")
guardar("02_instalar_colab", svg(760, 320, c, "Buscar Colaboratory e instalar"))

# ---------------------------------------------------------------- 3. Colab: Archivo → Guardar una copia en Drive
c = ventana(10, 10, 740, 330, "colab.research.google.com — desafio_cartografia.ipynb")
c += t(30, 66, "desafio_cartografia.ipynb", 16, TINTA, "bold")
menus = ["Archivo", "Editar", "Ver", "Insertar", "Entorno de ejecución", "Herramientas", "Ayuda"]
x = 30
for i, m in enumerate(menus):
    c += t(x, 90, m, 13, TINTA if i == 0 else GRIS, "bold" if i == 0 else "normal")
    if i == 0:
        c += resalte(x - 4, 76, 60, 20) + num(x - 6, 74, "1")
    x += len(m) * 7.4 + 18
items = ["Abrir cuaderno", "Subir cuaderno", "Cambiar nombre", "Guardar una copia en Drive",
         "Guardar una copia en GitHub", "Descargar"]
c += r(30, 104, 270, 28 * len(items) + 12, "white", LINEA, 8, 1, 'filter="drop-shadow(0 2px 4px rgba(0,0,0,.15))"')
for i, m in enumerate(items):
    c += t(48, 128 + i * 28, m, 13, TINTA if i == 3 else GRIS, "bold" if i == 3 else "normal")
c += resalte(36, 112 + 3 * 28, 258, 24) + num(306, 124 + 3 * 28, "2")
c += t(350, 150, "¿Por qué una copia?", 14, TINTA, "bold")
c += t(350, 174, "El notebook original es del docente y es de", 13, GRIS)
c += t(350, 194, "solo lectura. Tu copia queda en tu Drive", 13, GRIS)
c += t(350, 214, "(carpeta Colab Notebooks) y guarda tus cambios.", 13, GRIS)
c += t(350, 254, "Sabrás que funcionó porque el título", 13, TINTA)
c += t(350, 274, "cambia a «Copia de desafio_cartografia».", 13, TINTA, "bold")
guardar("03_guardar_copia", svg(760, 350, c, "Colab: Archivo, Guardar una copia en Drive"))

# ---------------------------------------------------------------- 4. Ejecutar un bloque: tres estados
def celda(x, y, estado):
    s = r(x, y, 210, 70, FONDO, LINEA, 8)
    if estado == "antes":
        s += f'<circle cx="{x+28}" cy="{y+35}" r="16" fill="white" stroke="{TINTA}" stroke-width="1.5"/>'
        s += f'<path d="M{x+23},{y+26} L{x+36},{y+35} L{x+23},{y+44} z" fill="{TINTA}"/>'
    elif estado == "corriendo":
        s += f'<circle cx="{x+28}" cy="{y+35}" r="16" fill="none" stroke="{LINEA}" stroke-width="3"/>'
        s += f'<path d="M{x+28},{y+19} a16,16 0 0 1 16,16" fill="none" stroke="{AZUL}" stroke-width="3"/>'
        s += f'<rect x="{x+23}" y="{y+30}" width="10" height="10" fill="{TINTA}"/>'
    else:
        s += t(x + 28, y + 42, "✓", 22, VERDE, "bold", "middle")
    s += t(x + 56, y + 31, "Bloque 1 · Preparar…", 12, TINTA, "bold") + t(x + 56, y + 50, "{ formulario }", 11, GRIS)
    return s
c = ""
estados = [("antes", "1 · Antes", "Pasa el mouse: aparece ▶. Haz clic", "(o Ctrl + Enter)."),
           ("corriendo", "2 · Ejecutándose", "El botón gira. Espera; no hagas", "clic otra vez."),
           ("listo", "3 · Terminado", "Aparece ✓ verde y el resultado", "debajo del bloque.")]
for i, (e, a, b1, b2) in enumerate(estados):
    x = 20 + i * 250
    c += t(x, 30, a, 14, [TINTA, AZUL, VERDE][i], "bold") + celda(x, 44, e)
    c += t(x, 140, b1, 12, GRIS) + t(x, 158, b2, 12, GRIS)
    if i < 2:
        c += flecha(x + 214, 79, x + 246, 79)
c += resalte(25, 56, 46, 46)
guardar("04_ejecutar", svg(780, 175, c, "Los tres estados de un bloque al ejecutarlo"))

# ---------------------------------------------------------------- 5. Advertencia
c = f'<rect width="760" height="250" fill="#495057" opacity=".18"/>'
c += r(120, 20, 520, 210, "white", "#adb5bd", 12, 1.5, 'filter="drop-shadow(0 4px 10px rgba(0,0,0,.2))"')
c += t(146, 60, "Advertencia: Este notebook no fue creado por Google.", 16, TINTA, "bold")
c += t(146, 92, "Este notebook se cargó desde GitHub. Puede solicitar acceso", 13, GRIS)
c += t(146, 112, "a tus datos almacenados en Google o leer datos y credenciales", 13, GRIS)
c += t(146, 132, "de otras sesiones. Revisa el código fuente antes de ejecutarlo.", 13, GRIS)
c += t(146, 196, "Cancelar", 14, AZUL, "bold")
c += r(430, 174, 186, 36, "white", "#adb5bd", 18) + t(523, 197, "Ejecutar de todos modos", 13, AZUL, "bold", "middle")
c += resalte(430, 174, 186, 36) + num(626, 176, "✓")
guardar("05_advertencia", svg(760, 250, c, "Advertencia de Colab: Ejecutar de todos modos"))

# ---------------------------------------------------------------- 6. Armador en Colab
c = ventana(10, 10, 740, 330, "Colab — Bloque 4 · Arma tu mensaje para Gemini")
c += t(34, 62, "✓", 18, VERDE, "bold") + t(56, 60, "▶ Bloque 4 · Arma tu mensaje para Gemini", 12, TINTA, "bold")
c += r(30, 72, 700, 30, "#e6f4ea", VERDE, 6, 1.2) + t(42, 92, "✓ Bloques 1, 2 y 3 listos. Responde las preguntas y copia el mensaje ↓", 12, VERDE, "bold")
c += r(30, 112, 700, 214, "white", "#adb5bd", 10)
c += t(44, 134, "✦ Arma tu mensaje para Gemini", 13, TINTA, "bold")
c += r(44, 144, 300, 34, FONDO, LINEA, 8)
for i, ch in enumerate(["Personas mayores", "Hacinamiento", "Leña"]):
    c += r(52 + i * 96, 151, 90, 20, "white" if i != 1 else "#fff4e6", ACENTO if i == 1 else LINEA, 10) + t(97 + i * 96, 165, ch, 10, ACENTO if i == 1 else GRIS, "normal", "middle")
campos = [("1 ¿Qué quieres mapear?", "dónde hay más viviendas hacinadas"), ("2 ¿Dónde?", "Una comuna ▾   Santiago"),
          ("3 ¿Cruzar con otro tema?", "No, un solo tema"), ("5 Tu nombre", "Camila Rojas")]
for i, (k, v) in enumerate(campos):
    y = 188 + i * 33
    c += t(44, y + 8, k, 10.5, TINTA, "bold") + r(180, y - 6, 164, 22, FONDO, LINEA, 5) + t(186, y + 9, v, 10, TINTA)
c += r(360, 144, 356, 130, FONDO, LINEA, 8)
for i, l in enumerate(["Hola Gemini. Estoy en Google Colab…", "- ¿Qué quiero mapear?: dónde hay más viviendas…",
                       "- ¿Dónde?: la comuna de Santiago", "…", "[+ diccionario y territorios: se agregan al copiar]"]):
    c += t(372, 164 + i * 20, l, 10.5, GRIS if i == 4 else TINTA, "normal", "start", "italic" if i == 4 else "normal")
c += r(360, 284, 230, 32, ACENTO, ACENTO, 9) + t(475, 305, "📋 Copiar mensaje para Gemini", 12, "white", "bold", "middle")
c += resalte(360, 284, 230, 32) + num(604, 300, "2") + num(352, 148, "1")
guardar("06_armador", svg(760, 350, c, "El armador del mensaje para Gemini al final del Bloque 1"))

# ---------------------------------------------------------------- 7. Gemini en Colab
c = ventana(10, 10, 740, 400, "Colab con el panel de Gemini abierto")
c += r(586, 18, 80, 24, "white", "#adb5bd", 12) + t(626, 35, "✦ Gemini", 12, MORADO, "bold", "middle")
c += resalte(586, 18, 80, 24) + num(680, 30, "1")
c += r(26, 50, 300, 350, FONDO, LINEA, 8) + t(42, 76, "Tu notebook", 13, GRIS, "bold")
for i in range(3):
    c += r(42, 92 + i * 96, 268, 76, "white", LINEA, 6)
c += r(340, 50, 396, 350, "white", MORADO, 8, 1.5)
c += t(356, 74, "✦ Gemini", 14, MORADO, "bold")
c += r(470, 84, 252, 50, "#f3f0ff", "none", 12)
c += t(482, 104, "Hola Gemini. Estoy en Google Colab…", 11, TINTA) + t(482, 122, "[+ diccionario pegado]", 11, MORADO, "normal", "start", "italic")
c += num(464, 86, "2")
c += r(354, 144, 368, 210, FONDO, "none", 12)
c += t(366, 164, "PARTE 1 · Lo que entendí", 11, MORADO, "bold")
c += t(366, 180, "% de viviendas hacinadas, comuna de Santiago (13101)", 10.5, TINTA)
c += t(366, 202, "PARTE 2 · La línea para ejecutar", 11, MORADO, "bold")
c += r(366, 210, 344, 66, "#212529" if True else "", "none", 8)
for i, l in enumerate(['hacer_mapa(escala="Comunal",', '  territorio="13101", variable_1="n_viv_hacinadas",', '  nombre_1="Viviendas hacinadas", autor="Camila Rojas")']):
    c += t(376, 228 + i * 16, l, 10, "#e9ecef", "normal")
c += r(612, 280, 98, 22, "white", "#adb5bd", 11) + t(661, 295, "▶ Ejecutar", 11, AZUL, "bold", "middle")
c += r(520, 280, 86, 22, "white", "#adb5bd", 11) + t(563, 295, "+ Insertar", 11, AZUL, "bold", "middle")
c += resalte(520, 280, 190, 22) + num(724, 291, "3")
c += t(366, 324, "PARTE 3 · Explicación simple", 11, MORADO, "bold")
c += t(366, 340, "Una vivienda está hacinada cuando…", 10.5, GRIS)
c += r(354, 362, 368, 28, "white", "#adb5bd", 14) + t(368, 381, "Escribe aquí y presiona Enter…", 11, GRIS)
guardar("07_gemini", svg(760, 420, c, "Gemini dentro de Colab: el mensaje pegado y la línea hacer_mapa lista para ejecutar"))

# ---------------------------------------------------------------- 8. Ejecutar la línea
c = r(10, 10, 740, 300, "white", "#adb5bd", 10, 1.5)
c += t(30, 40, "▶ Bloque 5 · Tu mapa: borra el ejemplo y pega la línea de Gemini", 13, GRIS, "bold")
c += r(30, 52, 700, 66, FONDO, LINEA, 8)
c += f'<circle cx="58" cy="85" r="15" fill="white" stroke="{TINTA}" stroke-width="1.5"/>' + f'<path d="M53,76 L66,85 L53,94 z" fill="{TINTA}"/>'
c += resalte(39, 66, 38, 38) + num(36, 62, "▶")
for i, l in enumerate(['hacer_mapa(escala="Comunal", territorio="13101", variable_1="n_viv_hacinadas",',
                       '           nombre_1="Viviendas hacinadas", autor="Camila Rojas")']):
    c += t(88, 80 + i * 20, l, 12, TINTA)
c += r(30, 132, 700, 30, "#e6f4ea", VERDE, 6, 1.2) + t(42, 152, "✓ Territorio elegido: Comuna de Santiago (código 13101) · Provincia Santiago · Región Metropolitana", 11.5, VERDE, "bold")
c += r(30, 170, 700, 30, "#e7f1fb", AZUL, 6, 1.2) + t(42, 190, "i Completé automáticamente (según el diccionario del INE): DENOMINADOR_1 = n_vp_ocupada", 11.5, AZUL, "bold")
c += r(30, 208, 700, 30, "#fff4d6", "#e67700", 6, 1.2) + t(42, 228, "! Si algo está mal, aparece un recuadro amarillo que te dice qué revisar.", 11.5, "#e67700", "bold")
c += t(30, 266, "Luego aparecen el mapa y el gráfico, y se descargan solos.", 13, TINTA, "bold")
c += t(30, 288, "¿Prefieres no pegar código? El Bloque 6 es un formulario que hace lo mismo.", 12, GRIS)
guardar("08_ejecutar", svg(760, 320, c, "Ejecutar la línea de Gemini y leer los recuadros de colores"))

# ---------------------------------------------------------------- 9. Resultado
c = ""
for i, (n, col) in enumerate([("mapa_….jpg", "#fc8d59"), ("grafico_….jpg", "#64acbe")]):
    x = 40 + i * 230
    c += r(x, 20, 190, 150, FONDO, LINEA, 10)
    if i == 0:
        for a in range(5):
            for b in range(4):
                c += f'<rect x="{x+30+a*26}" y="{40+b*22}" width="22" height="18" fill="{["#fef0d9","#fdcc8a","#fc8d59","#e34a33","#b30000"][(a*3+b)%5]}"/>'
    else:
        for a, h in enumerate([40, 70, 55, 90, 30, 60]):
            c += f'<rect x="{x+30+a*22}" y="{130-h}" width="16" height="{h}" fill="{col}"/>'
    c += t(x + 95, 158, n, 12, TINTA, "bold", "middle")
c += t(520, 50, "Se descargan solos a tu", 13, TINTA) + t(520, 70, "carpeta de Descargas.", 13, TINTA, "bold")
c += t(520, 104, "Si el navegador pregunta por", 13, GRIS) + t(520, 122, "«varias descargas», elige Permitir.", 13, GRIS)
c += t(520, 156, "¿Otro mapa? Cambia el formulario", 13, GRIS) + t(520, 174, "y ejecuta solo el Bloque 2.", 13, GRIS)
guardar("09_resultado", svg(760, 190, c, "Resultado: mapa y gráfico en JPEG"))
print("ok", len(list(OUT.glob("*.svg"))))
