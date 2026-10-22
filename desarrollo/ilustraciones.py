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

def guardar(nombre, contenido):
    (OUT / f"{nombre}.svg").write_text(contenido, encoding="utf-8")

# ---------------------------------------------------------------- 0. Recorrido
pasos = [("☁", "Habilitar Colab", "una sola vez", AZUL),
         ("▶", "Bloque 1", "carga los datos", VERDE),
         ("✦", "Gemini", "elige las variables", MORADO),
         ("☰", "Bloque 2", "llenas el formulario", VERDE),
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
c = ventana(10, 10, 740, 330, "colab.research.google.com — tarea_cartografia.ipynb")
c += t(30, 66, "tarea_cartografia.ipynb", 16, TINTA, "bold")
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
c += t(350, 274, "cambia a «Copia de tarea_cartografia».", 13, TINTA, "bold")
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

# ---------------------------------------------------------------- 6. Panel de archivos
c = ventana(10, 10, 740, 300, "Colab — panel de archivos")
c += r(10, 42, 52, 268, "#f1f3f5", "none", 0)
for i, ic in enumerate(["☰", "🔍", "{x}", "🔑", "📁"]):
    c += t(36, 74 + i * 42, ic, 17, TINTA if ic == "📁" else GRIS, "normal", "middle")
c += resalte(18, 222, 36, 32) + num(18, 220, "1")
c += r(62, 42, 290, 268, "white", LINEA, 0)
c += t(78, 70, "Archivos", 15, TINTA, "bold")
arbol = [("📁 ..", 0), ("📁 datos", 0), ("📁 resultados", 0), ("📁 sample_data", 0), ("📄 diccionario_para_IA.txt", 0)]
for i, (n, _) in enumerate(arbol):
    c += t(82, 104 + i * 30, n, 13, TINTA if "IA" in n else GRIS, "bold" if "IA" in n else "normal")
c += resalte(76, 104 + 4 * 30 - 17, 230, 24) + num(318, 104 + 4 * 30 - 5, "2")
c += r(390, 64, 340, 222, FONDO, LINEA, 8)
c += t(406, 88, "diccionario_para_IA.txt", 13, TINTA, "bold")
for i, l in enumerate(["COLUMNAS DISPONIBLES EN LA BASE…", "CUT, COMUNA, REGION, n_per, …", "",
                       "DICCIONARIO DE VARIABLES (Variable |", "Tipo | Descripción | Universo | …)",
                       "n_per|Frecuencia|Personas|…|n_per", "n_edad_60_mas|Frecuencia|…"]):
    c += t(406, 114 + i * 20, l, 11, GRIS)
c += r(406, 252, 150, 24, "#fff4e6", ACENTO, 6) + t(481, 269, "Ctrl + A  →  Ctrl + C", 12, ACENTO, "bold", "middle")
c += num(570, 264, "3")
c += flecha(310, 210, 400, 170, 30)
guardar("06_archivos", svg(760, 320, c, "Panel de archivos: abrir y copiar diccionario_para_IA.txt"))

# ---------------------------------------------------------------- 7. Gemini
c = ventana(10, 10, 740, 380, "Colab con el panel de Gemini abierto")
c += r(26, 50, 380, 320, FONDO, LINEA, 8) + t(42, 76, "Tu notebook", 13, GRIS, "bold")
for i in range(3):
    c += r(42, 92 + i * 80, 348, 62, "white", LINEA, 6)
c += r(586, 18, 80, 24, "white", "#adb5bd", 12) + t(626, 35, "✦ Gemini", 12, MORADO, "bold", "middle")
c += resalte(586, 18, 80, 24) + num(680, 30, "1")
c += r(420, 50, 316, 320, "white", MORADO, 8, 1.5)
c += t(436, 76, "✦ Gemini", 14, MORADO, "bold")
c += r(500, 90, 222, 92, "#f3f0ff", "none", 12)
for i, l in enumerate(["Actúa como asesor(a) en análisis", "territorial… MI PREGUNTA: ¿dónde", "se concentra…? ESCALA: Comunal",
                       "[+ texto del diccionario]"]):
    c += t(512, 110 + i * 19, l, 11, TINTA if i < 3 else MORADO, "normal", "start", "italic" if i == 3 else "normal")
c += num(494, 92, "2")
c += r(434, 196, 260, 120, FONDO, "none", 12)
for i, l in enumerate(["ESCALA = Comunal", "TERRITORIO = Valparaíso", "VARIABLE_1 = n_edad_60_mas",
                       "DENOMINADOR_1 = n_per", "NOMBRE_1 = Personas de 60+ …", "Justificación: …"]):
    c += t(446, 216 + i * 18, l, 11, TINTA if i < 5 else GRIS, "bold" if i < 5 else "normal")
c += num(700, 200, "3")
c += r(434, 328, 288, 30, "white", "#adb5bd", 15) + t(450, 348, "Escribe aquí y presiona Enter…", 12, GRIS)
guardar("07_gemini", svg(760, 400, c, "Panel de Gemini: pegar el prompt y recibir los valores"))

# ---------------------------------------------------------------- 8. Formulario
c = r(10, 10, 740, 330, "white", "#adb5bd", 10, 1.5)
c += t(30, 40, "▶   Bloque 2 · Formulario del mapa", 15, TINTA, "bold")
campos = [("ESCALA", "Comunal ▾"), ("TERRITORIO", "Valparaíso"), ("UNIDAD", "Automática ▾"),
          ("AREA", "Urbana y rural ▾"), ("VARIABLE_1", "n_edad_60_mas"), ("DENOMINADOR_1", "n_per"),
          ("NOMBRE_1", "Personas de 60 años y más"), ("VARIABLE_2", ""), ("AUTOR", "Tu nombre")]
for i, (k, v) in enumerate(campos):
    y = 66 + i * 29
    c += t(46, y + 15, k + ":", 13, GRIS, "normal") + r(190, y, 250, 22, "white", "#adb5bd", 4)
    c += t(198, y + 16, v, 12, TINTA if v else GRIS)
    if not v:
        c += t(198, y + 16, "(vacío = una sola variable)", 11, GRIS, "normal", "start", "italic")
c += resalte(190, 66 + 4 * 29, 250, 22 + 29)
c += r(490, 70, 240, 112, "#f3f0ff", MORADO, 10)
c += t(504, 92, "Lo que respondió Gemini", 12, MORADO, "bold")
for i, l in enumerate(["VARIABLE_1 = n_edad_60_mas", "DENOMINADOR_1 = n_per", "NOMBRE_1 = Personas de…"]):
    c += t(504, 116 + i * 20, l, 11, TINTA)
c += flecha(488, 140, 446, 190, -10)
c += t(490, 220, "Copia cada valor en su campo:", 13, TINTA, "bold")
c += t(490, 240, "sin comillas y sin el signo =.", 13, GRIS)
c += t(490, 272, "Luego presiona ▶ (arriba a la", 13, GRIS) + t(490, 290, "izquierda del bloque).", 13, GRIS)
c += num(30, 34, "▶")
guardar("08_formulario", svg(760, 350, c, "Formulario del Bloque 2 con los valores de Gemini"))

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
