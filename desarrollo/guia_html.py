"""Genera la guía ilustrada de Colab y Gemini como un único HTML autónomo (tema oscuro por defecto)."""
import base64, re
from armador import widget
from catalogo_variables import html_ideas, CSS as CSS_IDEAS, JS as JS_IDEAS
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SALIDA = Path("/mnt/user-data/outputs/Guia_Colab_y_Gemini.html")
NOTEBOOK = "https://colab.research.google.com/github/benjajul/clase-mapeo-censo/blob/main/codigo/desafio_cartografia.ipynb"
TAREA = "https://benjajul.github.io/clase-mapeo-censo/desafio-colab.html"
DRIVE_DOCENTE = "https://drive.google.com/drive/folders/1qzYq0RzuFlMieopEV03JyfpTOxxxWjij"


def uri(carpeta, nombre):
    datos = (REPO / "img" / carpeta / f"{nombre}.svg").read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(datos).decode()


def figura(nombre, pie, alt):
    return (f'<figure class="ilus"><img class="solo-oscuro" src="{uri("guia_oscuro", nombre)}" alt="{alt}">'
            f'<img class="solo-claro" src="{uri("guia", nombre)}" alt="{alt}">'
            f'<figcaption>{pie}</figcaption></figure>')


def paso(n, id_, titulo, tiempo, cuerpo, nota=""):
    return f'''
<section class="paso" id="{id_}" data-paso="{n}">
  <header class="paso-cab">
    <span class="paso-num">{n}</span>
    <div><p class="paso-eti">Paso {n} · <span>{tiempo}</span></p><h2>{titulo}</h2></div>
    <label class="hecho"><input type="checkbox" data-check="{id_}"> Hecho</label>
  </header>
  {nota}
  {cuerpo}
</section>'''


def caja(tipo, titulo, texto):
    icono = {"ok": "✓", "info": "i", "alerta": "!", "tip": "★"}[tipo]
    return f'<aside class="caja {tipo}"><span class="caja-ic">{icono}</span><div><strong>{titulo}</strong><p>{texto}</p></div></aside>'


habilitar = f"""
<details class="plegable"><summary>¿El enlace no abre el notebook? Habilita Colab en tu Drive (solo si hace falta)</summary>
<p>Algunas cuentas necesitan activar Colab una vez, como una "aplicación" de Google Drive:</p>
<ol class="pasitos">
  <li>Entra a <a href="https://drive.google.com/" target="_blank" rel="noopener">Google Drive</a> con tu cuenta.</li>
  <li>Haz clic en <kbd>+ Nuevo</kbd>, luego en <b>Más</b> y luego en <b>Conectar más aplicaciones</b>.</li>
</ol>
{figura("01_drive_conectar", "Los tres clics en Google Drive.", "Menú de Google Drive: Nuevo, Más, Conectar más aplicaciones")}
<ol class="pasitos" start="3">
  <li>Busca <b>Colaboratory</b>, haz clic en su tarjeta y luego en <kbd>Instalar</kbd>. Acepta los permisos.</li>
  <li>Vuelve a hacer clic en <b>Abrir en Colab</b>.</li>
</ol>
{figura("02_instalar_colab", "Buscar e instalar Colaboratory.", "Tienda de aplicaciones: buscar Colaboratory e instalar")}
</details>"""

cuerpo_1 = f'''
<ol class="pasitos">
  <li>Abre el notebook del desafío: <a class="boton" href="{NOTEBOOK}" target="_blank" rel="noopener">Abrir en Colab ↗</a> Si te lo pide, inicia sesión con tu cuenta de Gmail.</li>
  <li>Ve al menú <b>Archivo → Guardar una copia en Drive</b>.</li>
</ol>
{figura("03_guardar_copia", "Guardar una copia propia del notebook.", "Menú Archivo de Colab con Guardar una copia en Drive")}
{caja("ok", "¿Cómo sé que funcionó?", "Se abre una pestaña nueva y el título dice <b>«Copia de desafio_cartografia.ipynb»</b>. Trabaja siempre en esa pestaña: la otra puedes cerrarla.")}
{habilitar}
'''

cuerpo_2 = f'''
<p>El Bloque 1 descarga los datos del Censo y prepara todo. <b>No tienes que cambiar nada</b>: solo ejecutarlo.</p>
<ol class="pasitos">
  <li>Pasa el mouse sobre el bloque: a la izquierda aparece el botón <kbd>▶</kbd>. Haz clic.</li>
  <li>Espera. Mientras trabaja, el botón gira. La primera vez tarda <b>1 a 3 minutos</b>.</li>
  <li>Al terminar aparece un <b>✓ verde</b> y un recuadro verde que dice <b>«Listo»</b>. Debajo aparece el <b>armador del mensaje para Gemini</b> (paso 3).</li>
</ol>
{figura("04_ejecutar", "Los tres estados de un bloque.", "Un bloque antes, durante y después de ejecutarse")}
<p>La primera vez, Colab muestra esta advertencia. Es normal: aparece con cualquier notebook que no fue creado por Google. Presiona <kbd>Ejecutar de todos modos</kbd>.</p>
{figura("05_advertencia", "La advertencia de seguridad de Colab.", "Advertencia: Este notebook no fue creado por Google")}
{caja("alerta", "Si el bloque muestra un error al descargar los datos", 'Google limita las descargas cuando muchas personas bajan los datos al mismo tiempo. Mira <a href="#descarga">Si la descarga falla</a>, al final de esta guía.')}
'''

cuerpo_3 = f'''
<p>Todo ocurre <b>dentro de Colab</b>: no necesitas otra pestaña ni adjuntar archivos.</p>
<ol class="pasitos">
  <li>Baja hasta el <b>armador del mensaje para Gemini</b>, al final del resultado del Bloque 1. Responde con tus palabras: <b>qué quieres mapear</b> (o toca una de las ideas), <b>dónde</b>, si lo quieres <b>cruzar con otro tema</b>, tu pregunta (opcional) y <b>tu nombre</b>.</li>
  <li>Presiona <kbd>📋 Copiar mensaje para Gemini</kbd>. El mensaje ya incluye el diccionario de variables y los códigos de los territorios.</li>
</ol>
{figura("06_armador", "El armador aparece al final del Bloque 1.", "Armador del mensaje para Gemini con ideas, preguntas y botón Copiar")}
<ol class="pasitos" start="3">
  <li>Haz clic en <kbd>✦ Gemini</kbd>, arriba a la derecha de Colab: se abre un chat al costado. Pega el mensaje (<kbd>Ctrl</kbd> + <kbd>V</kbd>) y presiona <kbd>Enter</kbd>.</li>
  <li>Gemini responde en tres partes: <b>lo que entendió</b> (confirma que es lo que querías), <b>una línea</b> <code>hacer_mapa(...)</code> lista para ejecutar y una <b>explicación simple</b>. Si no entendió bien, díselo con tus palabras y pídele que corrija la línea.</li>
</ol>
{figura("07_gemini", "Gemini dentro de Colab, con la línea lista para ejecutar.", "Panel de Gemini en Colab con la respuesta en tres partes")}
{caja("tip", "Si no ves el botón Gemini en Colab", 'Abre <a href="https://gemini.google.com/" target="_blank" rel="noopener">gemini.google.com</a> en otra pestaña y pega el mismo mensaje: también funciona. Luego copia la línea <code>hacer_mapa(...)</code> de vuelta en Colab (paso 4).')}
{caja("info", "¿No sabes qué mapear?", 'El armador trae 23 ideas listas para tocar. Hay 189 variables en total: pregúntale a Gemini <i>«Con este diccionario, muéstrame todas las variables sobre [tema] y explícamelas en simple»</i>.')}
<h3>Cómo conversar bien con Gemini</h3>
<p>Gemini no es un buscador: es una <b>conversación</b>. Su primera respuesta es un punto de partida. Algunas preguntas útiles para continuar:</p>
<div class="dialogos">
  <div><span>Para entender la propuesta</span><q>¿Por qué elegiste ese denominador y no otro?</q></div>
  <div><span>Para explorar alternativas</span><q>Dame dos variables alternativas para mi pregunta y explica qué mide cada una.</q></div>
  <div><span>Para revisar un posible error</span><q>¿El numerador y el denominador tienen el mismo universo?</q></div>
  <div><span>Para simplificar</span><q>Explícame esta variable como se la explicarías a alguien sin formación técnica.</q></div>
</div>
<aside class="caja alerta"><span class="caja-ic">!</span><div><strong>Cuatro cuidados con la IA</strong>
<ol>
  <li><b>Verifica</b> en la Parte 1 que entendió bien el tema y el territorio. Gemini puede equivocarse o inventar nombres.</li>
  <li>Si Gemini propone escribir <b>otro código</b> (instalar cosas, cargar datos, hacer su propio mapa), no lo ejecutes: pídele solo la línea <code>hacer_mapa(...)</code>.</li>
  <li><b>No compartas datos personales</b> (tuyos ni de terceros) en el chat.</li>
  <li><b>Guarda la conversación</b> (copia el texto en un documento): la necesitas para el anexo de uso de IA del informe.</li>
</ol></div></aside>
'''

cuerpo_4 = f'''
<ol class="pasitos">
  <li>Junto a la línea <code>hacer_mapa(...)</code>, Gemini muestra botones para usar el código: <b>▶ Ejecutar</b> o <b>+ Insertar</b> (agrega la línea como una celda nueva). Los nombres pueden variar un poco.</li>
  <li>Si la insertaste, presiona <kbd>▶</kbd> en esa celda nueva. Si no ves botones, copia la línea, crea una celda con <kbd>+ Código</kbd> (arriba a la izquierda), pégala y presiona <kbd>▶</kbd>.</li>
  <li>Lee los recuadros de colores que aparecen: <b>verde</b> confirma el territorio, <b>azul</b> te dice qué se completó solo y <b>amarillo</b> te dice qué revisar.</li>
</ol>
{figura("08_ejecutar", "La línea de Gemini en una celda, y los recuadros de colores.", "Celda con hacer_mapa y recuadros verde, azul y amarillo")}
{caja("info", "¿Prefieres no ejecutar código del chat?", "El <b>Bloque 2</b> es un formulario que hace exactamente lo mismo: copia en cada campo los valores de la línea de Gemini (sin comillas) y presiona ▶. Solo son obligatorios los campos marcados con ★.")}
{caja("ok", "Si un recuadro amarillo te pide corregir algo", "Cópiale el mensaje a Gemini y pídele la línea corregida, o corrige tú el valor en la línea y vuelve a presionar ▶.")}
'''

cuerpo_5 = f'''
<p>En 1 o 2 minutos aparecen, debajo del bloque, el <b>mapa</b> y el <b>gráfico</b>, y se descargan solos a tu computador.</p>
{figura("09_resultado", "Los dos archivos del desafío.", "Dos archivos descargados: mapa y gráfico en JPEG")}
{caja("tip", "¿Otro mapa?", "Cambia el formulario y ejecuta <b>solo el Bloque 2</b> las veces que quieras. El Bloque 1 se vuelve a ejecutar únicamente si Colab se desconectó.")}
'''

PASOS = [
    paso(1, "abrir", "Abrir el notebook y guardar tu copia", "2 min", cuerpo_1),
    paso(2, "bloque1", "Ejecutar el Bloque 1", "3 min", cuerpo_2),
    paso(3, "gemini", "Armar el mensaje y conversar con Gemini", "10 min", cuerpo_3),
    paso(4, "ejecutar", "Ejecutar la línea de Gemini", "3 min", cuerpo_4),
    paso(5, "resultados", "Tus resultados", "2 min", cuerpo_5),
]

TITULOS_NAV = [("abrir", "Abrir Colab"), ("bloque1", "Bloque 1"), ("gemini", "Gemini"),
               ("ejecutar", "Ejecutar"), ("resultados", "Resultados")]

NAV = "".join(f'<li><a href="#{i}"><span class="nav-n">{n}</span>{t}<span class="nav-ok">✓</span></a></li>'
              for n, (i, t) in enumerate(TITULOS_NAV, start=1))

PROBLEMAS = [
    ("«Sesión desconectada» o «Volver a conectar»", "Colab apaga la “cocina” tras un rato sin uso", "Ejecuta de nuevo el Bloque 1 y luego el Bloque 2"),
    ("<code>NameError: name 'hacer_mapa' is not defined</code>", "Colab se reinició o no ejecutaste el Bloque 1", "Ejecuta primero el Bloque 1 y luego la línea"),
    ("Recuadro amarillo «No encontré '…' en la escala …»", "El territorio está mal escrito o no corresponde a esa escala", "Usa una de las sugerencias del aviso"),
    ("Recuadro amarillo «El campo variable 1: '…' no existe»", "Gemini escribió un nombre que no está en la base", "Cópiale el recuadro a Gemini y pídele la línea corregida"),
    ("Gemini escribe mucho código o instala paquetes", "Se salió de la instrucción", "No lo ejecutes. Escríbele: «Solo dame la línea hacer_mapa(...)»"),
    ("Recuadro amarillo «Ojo: este nombre también existe en otro nivel»", "Hay una comuna, provincia o región con el mismo nombre (no es un error)", "Revisa el recuadro verde del territorio elegido; si no es el nivel que querías, cambia <code>ESCALA</code> o escribe el código"),
    ("«El código '…' no corresponde a la escala …»", "El código no tiene los dígitos de esa escala", "5 dígitos para comuna, 3 para provincia, 2 para región"),
    ("«Solo hay N unidades con datos»", "Muy pocas comunas para clasificar", "Cambia <code>UNIDAD</code> a <i>Manzana</i> o elige una escala mayor"),
    ("No se descargan los archivos", "El navegador bloqueó las descargas", "Acepta «Permitir varias descargas» o búscalos en 📁 → <code>resultados</code> (clic derecho → Descargar)"),
]
FILAS = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in PROBLEMAS)

CSS = r"""
:root{
  --bg:#0e1116; --sup:#151a21; --sup2:#1b2129; --borde:#28303a; --texto:#e6e8eb; --suave:#9aa4b2;
  --acento:#ff7a2f; --acento-bg:rgba(255,122,47,.12); --verde:#51cf66; --azul:#4dabf7; --morado:#9775fa; --ambar:#fcc419;
  --sombra:0 10px 30px rgba(0,0,0,.35); --radio:16px;
}
:root[data-theme="claro"]{
  --bg:#f6f7f9; --sup:#ffffff; --sup2:#f1f3f5; --borde:#dee2e6; --texto:#1f2329; --suave:#5c6670;
  --acento:#e8590c; --acento-bg:rgba(232,89,12,.08); --verde:#2f9e44; --azul:#1c7ed6; --morado:#7048e8; --ambar:#e67700;
  --sombra:0 6px 20px rgba(0,0,0,.08);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:80px}
body{margin:0;background:var(--bg);color:var(--texto);font:16px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--acento)} a:hover{text-decoration-thickness:2px}
code{font:0.88em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--sup2);border:1px solid var(--borde);padding:.08em .4em;border-radius:6px}
kbd{font:600 .82em ui-monospace,Menlo,Consolas,monospace;background:var(--sup2);border:1px solid var(--borde);border-bottom-width:3px;border-radius:6px;padding:.05em .45em;white-space:nowrap}
.barra{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:16px;padding:12px max(16px,calc((100vw - 1180px)/2));background:color-mix(in srgb,var(--bg) 85%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--borde)}
.barra .marca{font-weight:700;letter-spacing:.2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.barra .marca span{color:var(--acento)}
.progreso{flex:1;height:6px;background:var(--sup2);border-radius:99px;overflow:hidden;min-width:60px}
.progreso i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--acento),#ffb26b);transition:width .4s}
.barra .cuenta{color:var(--suave);font-size:.85rem;white-space:nowrap}
.tema{white-space:nowrap;background:var(--sup);color:var(--texto);border:1px solid var(--borde);border-radius:99px;padding:6px 12px;cursor:pointer;font:inherit;font-size:.85rem}
.hero{max-width:1180px;margin:0 auto;padding:56px 16px 24px}
.eyebrow{display:inline-block;color:var(--acento);background:var(--acento-bg);border:1px solid color-mix(in srgb,var(--acento) 40%,transparent);padding:4px 12px;border-radius:99px;font-size:.8rem;font-weight:600;letter-spacing:.3px}
.hero h1{font-size:clamp(2rem,4.5vw,3.2rem);line-height:1.1;margin:.5em 0 .3em;letter-spacing:-.02em}
.hero h1 em{font-style:normal;background:linear-gradient(90deg,var(--acento),#ffb26b);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero .bajada{font-size:1.15rem;color:var(--suave);max-width:680px;margin:0}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0 8px}
.chips span{background:var(--sup);border:1px solid var(--borde);padding:8px 14px;border-radius:12px;font-size:.92rem}
.recorrido{margin:28px 0 0;padding:16px;background:var(--sup);border:1px solid var(--borde);border-radius:var(--radio);box-shadow:var(--sombra)}
.recorrido img{width:100%;display:block}
.layout{max-width:1180px;margin:0 auto;padding:16px 16px 64px;display:grid;grid-template-columns:230px 1fr;gap:40px}
nav.indice{position:sticky;top:84px;align-self:start}
nav.indice p{font-size:.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--suave);margin:0 0 8px 12px}
nav.indice ol{list-style:none;margin:0;padding:0}
nav.indice a{display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:10px;color:var(--suave);text-decoration:none;font-size:.95rem}
nav.indice a:hover{background:var(--sup);color:var(--texto)}
nav.indice a.activo{background:var(--acento-bg);color:var(--texto)}
.nav-n{width:24px;height:24px;flex:none;border-radius:50%;display:grid;place-items:center;font-size:.78rem;font-weight:700;border:1.5px solid var(--borde)}
a.activo .nav-n{border-color:var(--acento);color:var(--acento)}
.nav-ok{margin-left:auto;color:var(--verde);opacity:0;font-weight:700}
a.listo .nav-ok{opacity:1} a.listo .nav-n{background:var(--verde);border-color:var(--verde);color:#0e1116}
nav.indice .extra{margin-top:10px;padding-top:10px;border-top:1px solid var(--borde)}
main{min-width:0}
h2{font-size:1.55rem;line-height:1.25;margin:0;letter-spacing:-.01em}
h3{font-size:1.15rem;margin:1.8em 0 .6em}
.ideas{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:0 0 20px}
.idea{background:var(--sup);border:1px solid var(--borde);border-radius:var(--radio);padding:20px;position:relative;overflow:hidden}
.idea::before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:var(--c)}
.idea .ico{font-size:1.8rem;line-height:1}
.idea h4{margin:.5em 0 .3em;font-size:1.05rem}
.idea p{margin:0;color:var(--suave);font-size:.95rem}
.paso{background:var(--sup);border:1px solid var(--borde);border-radius:20px;padding:28px 32px;margin:0 0 28px;box-shadow:var(--sombra)}
.paso-cab{display:flex;align-items:center;gap:16px;margin-bottom:12px}
.paso-num{width:52px;height:52px;flex:none;border-radius:14px;display:grid;place-items:center;font-size:1.5rem;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--acento),#ff9d5c);box-shadow:0 6px 16px rgba(255,122,47,.35)}
.paso-eti{margin:0;font-size:.78rem;text-transform:uppercase;letter-spacing:1px;color:var(--acento);font-weight:700}
.paso-eti span{color:var(--suave);font-weight:500;text-transform:none;letter-spacing:0}
.hecho{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:.88rem;color:var(--suave);cursor:pointer;background:var(--sup2);border:1px solid var(--borde);padding:6px 12px;border-radius:99px;user-select:none;white-space:nowrap}
.hecho input{accent-color:var(--verde);width:16px;height:16px;margin:0}
.paso.completo{border-color:color-mix(in srgb,var(--verde) 55%,var(--borde))}
.paso.completo .paso-num{background:linear-gradient(135deg,#2f9e44,var(--verde));box-shadow:none}
.plegable{margin:18px 0;border:1px solid var(--borde);border-radius:12px;padding:10px 16px;background:var(--sup2)}
.plegable summary{cursor:pointer;font-weight:600;color:var(--suave)}
.plegable[open] summary{margin-bottom:8px}
.nota-paso{margin:-4px 0 10px 68px;color:var(--suave);font-style:italic}
ol.pasitos{counter-reset:p;list-style:none;padding:0;margin:14px 0}
ol.pasitos[start="3"]{counter-reset:p 2}
ol.pasitos li{counter-increment:p;position:relative;padding:4px 0 10px 44px}
ol.pasitos li::before{content:counter(p);position:absolute;left:0;top:3px;width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:.9rem;color:var(--acento);background:var(--acento-bg);border:1px solid color-mix(in srgb,var(--acento) 45%,transparent)}
figure.ilus{margin:18px 0 22px}
figure.ilus img{width:100%;display:block;border-radius:12px;border:1px solid var(--borde)}
figure.ilus figcaption{font-size:.85rem;color:var(--suave);margin-top:8px;text-align:center}
.solo-claro{display:none!important}
:root[data-theme="claro"] .solo-claro{display:block!important}
:root[data-theme="claro"] .solo-oscuro{display:none!important}
.caja{display:flex;gap:14px;align-items:flex-start;border-radius:14px;padding:14px 18px;margin:18px 0;background:color-mix(in srgb,var(--c) 10%,transparent);border:1px solid color-mix(in srgb,var(--c) 40%,transparent)}
.caja.ok{--c:var(--verde)} .caja.info{--c:var(--azul)} .caja.alerta{--c:var(--ambar)} .caja.tip{--c:var(--morado)}
.caja-ic{width:26px;height:26px;flex:none;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:.85rem;background:var(--c);color:#0e1116;margin-top:2px}
.caja p,.caja ol{margin:.2em 0 0} .caja ol{padding-left:1.2em} .caja strong{color:var(--c)}
.dialogos{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:12px 0}
.dialogos div{background:var(--sup2);border:1px solid var(--borde);border-radius:14px 14px 14px 4px;padding:14px 16px}
.dialogos span{display:block;font-size:.75rem;text-transform:uppercase;letter-spacing:.8px;color:var(--morado);font-weight:700;margin-bottom:4px}
.dialogos q{font-style:italic} .dialogos q::before{content:"«"} .dialogos q::after{content:"»"}
.boton{display:inline-block;background:var(--acento);color:#fff!important;text-decoration:none;font-weight:700;padding:6px 14px;border-radius:10px;margin-left:4px}
.boton:hover{filter:brightness(1.1)}
.tarjeta-sec{background:var(--sup);border:1px solid var(--borde);border-radius:20px;padding:28px 32px;margin:0 0 28px}
.tabla{overflow-x:auto;border:1px solid var(--borde);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:.93rem;min-width:620px}
th{text-align:left;background:var(--sup2);color:var(--suave);font-size:.78rem;text-transform:uppercase;letter-spacing:.8px}
th,td{padding:12px 14px;border-bottom:1px solid var(--borde);vertical-align:top}
tr:last-child td{border-bottom:0}
td:first-child{font-weight:600}
.glosario{display:grid;grid-template-columns:repeat(2,1fr);gap:10px 24px;margin:0;padding:0}
.glosario div{padding:10px 0;border-bottom:1px dashed var(--borde)}
.glosario dt{font-weight:700;color:var(--acento)} .glosario dd{margin:2px 0 0;color:var(--suave)}
footer{max-width:1180px;margin:0 auto;padding:24px 16px 48px;color:var(--suave);font-size:.88rem;border-top:1px solid var(--borde)}
@media (max-width:900px){
  .layout{grid-template-columns:1fr;gap:0} nav.indice{display:none}
  .ideas{grid-template-columns:1fr} .dialogos,.glosario{grid-template-columns:1fr}
  .paso,.tarjeta-sec{padding:20px 18px} .plegable{margin:18px 0;border:1px solid var(--borde);border-radius:12px;padding:10px 16px;background:var(--sup2)}
.plegable summary{cursor:pointer;font-weight:600;color:var(--suave)}
.plegable[open] summary{margin-bottom:8px}
.nota-paso{margin-left:0}
  .paso-cab{flex-wrap:wrap} .hecho{margin-left:68px} .barra .marca{font-size:.9rem}
  .tema .lbl{display:none} .recorrido{overflow-x:auto} .recorrido img{min-width:640px}
}
@media print{
  :root{--bg:#fff;--sup:#fff;--sup2:#f4f4f4;--borde:#ccc;--texto:#111;--suave:#444;--sombra:none}
  .barra,nav.indice,.hecho{display:none} .layout{display:block}
  .solo-oscuro{display:none!important} .solo-claro{display:block!important}
  .paso{break-inside:avoid-page}
}
"""

JS = r"""
(function(){
  const raiz=document.documentElement, clave='guia-colab-v1';
  let estado={};
  try{estado=JSON.parse(localStorage.getItem(clave)||'{}')}catch(e){}
  const guardar=()=>{try{localStorage.setItem(clave,JSON.stringify(estado))}catch(e){}};
  const aplicarTema=t=>{raiz.dataset.theme=t;document.getElementById('tema').innerHTML=t==='claro'?'☾ <span class="lbl">Tema oscuro</span>':'☀ <span class="lbl">Tema claro</span>'};
  aplicarTema(estado.tema||'oscuro');
  document.getElementById('tema').addEventListener('click',()=>{estado.tema=raiz.dataset.theme==='claro'?'oscuro':'claro';aplicarTema(estado.tema);guardar()});
  const checks=[...document.querySelectorAll('[data-check]')], total=checks.length;
  const actualizar=()=>{
    let n=0;
    checks.forEach(c=>{const id=c.dataset.check,ok=!!estado[id];c.checked=ok;n+=ok;
      document.getElementById(id).classList.toggle('completo',ok);
      const a=document.querySelector('nav.indice a[href="#'+id+'"]'); if(a)a.classList.toggle('listo',ok);});
    document.querySelector('.progreso i').style.width=(100*n/total)+'%';
    document.querySelector('.cuenta').textContent=n+' de '+total+' pasos';
  };
  checks.forEach(c=>c.addEventListener('change',()=>{estado[c.dataset.check]=c.checked;guardar();actualizar()}));
  actualizar();
  const enlaces=[...document.querySelectorAll('nav.indice a[href^="#"]')];
  const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){enlaces.forEach(a=>a.classList.toggle('activo',a.getAttribute('href')==='#'+e.target.id))}}),{rootMargin:'-30% 0px -60% 0px'});
  document.querySelectorAll('section[id]').forEach(s=>obs.observe(s));
})();
"""

HTML = f"""<!doctype html>
<html lang="es" data-theme="oscuro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guía ilustrada: Colab y Gemini</title>
<meta name="description" content="Guía paso a paso para el desafío de cartografía censal «para seguir aprendiendo» en Google Colab con apoyo de Gemini, sin saber programar.">
<style>{CSS}{CSS_IDEAS}</style>
</head>
<body>
<div class="barra">
  <div class="marca">Guía <span>Colab + Gemini</span></div>
  <div class="progreso" aria-hidden="true"><i></i></div>
  <div class="cuenta">0 de 5 pasos</div>
  <button class="tema" id="tema" type="button">☀ Tema claro</button>
</div>

<header class="hero">
  <span class="eyebrow">Magíster en Metodologías Críticas para la Investigación Social · Desafío para seguir aprendiendo</span>
  <h1>Tu mapa del Censo 2024,<br><em>sin saber programar</em></h1>
  <p class="bajada">Una guía ilustrada, paso a paso, para hacer tu propio mapa con Google Colab y Gemini. Son cinco pasos: marca cada uno como <b>hecho</b> y avanza a tu ritmo.</p>
  <div class="chips"><span>⏱ 20 a 30 minutos</span><span>💻 Sin instalar nada</span><span>👤 Cuenta personal de Gmail</span><span>🌐 Navegador Chrome</span></div>
  <figure class="recorrido">
    <img class="solo-oscuro" src="{uri('guia_oscuro', '00_recorrido')}" alt="Recorrido en cinco pasos">
    <img class="solo-claro" src="{uri('guia', '00_recorrido')}" alt="Recorrido en cinco pasos">
  </figure>
</header>

<div class="layout">
  <nav class="indice" aria-label="Pasos">
    <p>Pasos</p>
    <ol>{NAV}</ol>
    <ol class="extra">
      <li><a href="#ideas"><span class="nav-n">?</span>Tres ideas</a></li>
      <li><a href="#problemas"><span class="nav-n">!</span>Problemas</a></li>
      <li><a href="#glosario"><span class="nav-n">A</span>Glosario</a></li>
    </ol>
  </nav>
  <main>
    <section class="tarjeta-sec" id="ideas">
      <h2 style="margin-bottom:16px">Antes de empezar: tres ideas</h2>
      <div class="ideas">
        <div class="idea" style="--c:var(--azul)"><div class="ico">🍳</div><h4>Colab es una cocina equipada</h4><p>Tú traes la receta (el notebook) y Google pone la cocina: el computador que hace los cálculos está en la nube. Por eso <b>no instalas nada</b> y funciona incluso en un computador antiguo.</p></div>
        <div class="idea" style="--c:var(--verde)"><div class="ico">📓</div><h4>Un notebook es un cuaderno</h4><p>Mezcla texto explicativo con <b>bloques</b> (o celdas) de código. Cada bloque se <b>ejecuta</b> por separado con el botón ▶, de arriba hacia abajo, como seguir una receta en orden.</p></div>
        <div class="idea" style="--c:var(--morado)"><div class="ico">✦</div><h4>Gemini es un asistente, no un oráculo</h4><p>Es la inteligencia artificial de Google. Te ayuda a <b>traducir tu pregunta</b> al lenguaje del Censo, pero puede equivocarse. La última palabra siempre es tuya.</p></div>
      </div>
      {caja("tip", "Lo que necesitas", "Una <b>cuenta personal de Gmail</b> (las institucionales a veces tienen Colab o Gemini bloqueados), el navegador <b>Chrome</b>, <b>30 minutos</b> y una conexión a internet estable.")}
    </section>
    {''.join(PASOS)}
    <section class="tarjeta-sec" id="problemas">
      <h2 style="margin-bottom:16px">Problemas frecuentes</h2>
      <div class="tabla"><table><thead><tr><th>Lo que ves</th><th>Qué significa</th><th>Qué hacer</th></tr></thead><tbody>{FILAS}</tbody></table></div>
      <h3 id="descarga">Si la descarga falla</h3>
      <ol class="pasitos">
        <li>Abre la <a href="{DRIVE_DOCENTE}" target="_blank" rel="noopener">carpeta de datos del docente ↗</a> y descarga los archivos.</li>
        <li>En tu Google Drive, dentro de <b>Mi unidad</b>, crea una carpeta llamada <code>censo2024</code> y sube ahí los archivos.</li>
        <li>Ejecuta de nuevo el Bloque 1. Te pedirá permiso para acceder a tu Drive: acéptalo.</li>
      </ol>
    </section>
    <section class="tarjeta-sec" id="glosario">
      <h2 style="margin-bottom:12px">Pequeño glosario</h2>
      <dl class="glosario">
        <div><dt>Notebook (cuaderno)</dt><dd>Documento que mezcla texto y código.</dd></div>
        <div><dt>Bloque (celda)</dt><dd>Cada caja del notebook que se ejecuta por separado.</dd></div>
        <div><dt>Ejecutar</dt><dd>Pedirle al computador que haga lo que dice un bloque (botón ▶).</dd></div>
        <div><dt>Sesión o entorno de ejecución</dt><dd>El computador prestado por Google mientras trabajas; se apaga si no lo usas.</dd></div>
        <div><dt>Prompt</dt><dd>La instrucción que le escribes a la IA.</dd></div>
        <div><dt>Denominador</dt><dd>El total contra el que comparas (por ejemplo, el total de personas) para obtener un porcentaje.</dd></div>
      </dl>
    </section>
  </main>
</div>
<footer>Benjamín Julio · Ingeniería Civil en Geografía, Minor en Ciencia de Datos · Universidad de Santiago de Chile<br>
Magíster en Metodologías Críticas para la Investigación Social · Datos: INE, Censo de Población y Vivienda 2024</footer>
<script>{JS}</script><script>{JS_IDEAS}</script>
</body>
</html>"""

SALIDA.write_text(HTML, encoding="utf-8")
print("ok", SALIDA, round(len(HTML) / 1024), "KB")
