"""Catálogo de ideas de variables para la tarea (fuente única para el sitio y la guía autónoma).

Genera `_catalogo_variables.qmd` (incluido en 04-tarea.qmd y guia-colab.qmd) y la función `html_ideas()`
que usa guia_html.py. Los denominadores corresponden al "Denominador sugerido" según el universo del
diccionario del INE, salvo donde se indica.
"""
from pathlib import Path

EXCEL = "https://github.com/benjajul/clase-mapeo-censo/raw/main/datos/diccionario_variables_glosas_censo2024.xlsx"

# (tema, idea en lenguaje simple, frase para el armador, variable, denominador, nota)
IDEAS = [
    ("👥 Población", "Personas mayores (60 años y más)", "dónde vive más gente mayor de 60 años", "n_edad_60_mas", "n_per", ""),
    ("👥 Población", "Primera infancia (0 a 5 años)", "dónde viven más niñas y niños de 0 a 5 años", "n_edad_0_5", "n_per", ""),
    ("👥 Población", "Población inmigrante internacional", "dónde vive más población inmigrante", "n_inmigrantes", "n_per", ""),
    ("👥 Población", "Pueblos originarios", "dónde vive más gente que pertenece a un pueblo originario", "n_pueblos_orig", "n_per", ""),
    ("👥 Población", "Población afrodescendiente", "dónde vive más población afrodescendiente", "n_afrodescendencia", "n_per", ""),
    ("👥 Población", "Personas con discapacidad", "dónde vive más gente con discapacidad", "n_discapacidad", "n_per-n_edad_0_5", "Universo: 5 años o más"),
    ("🎓 Educación y trabajo", "Escolaridad promedio (18+)", "dónde la escolaridad promedio es más alta o más baja", "prom_escolaridad18", "", "Ya es un promedio"),
    ("🎓 Educación y trabajo", "Educación superior completa", "dónde vive más gente con educación superior", "n_cine_terciaria_maestria_doctorado", "n_per", "Discute si conviene otro denominador (por edad)"),
    ("🎓 Educación y trabajo", "Analfabetismo (15+)", "dónde hay más personas que no saben leer ni escribir", "n_analfabet", "n_ocupado+n_desocupado+n_fuera_fuerza_trabajo", "Universo: 15 años o más"),
    ("🎓 Educación y trabajo", "Desocupación", "dónde hay más personas desocupadas", "n_desocupado", "n_ocupado+n_desocupado", "Tasa sobre la fuerza de trabajo"),
    ("🎓 Educación y trabajo", "Jóvenes en educación superior (18–24)", "dónde más jóvenes de 18 a 24 años estudian en la educación superior", "n_asistencia_superior", "n_edad_18_24", ""),
    ("🎓 Educación y trabajo", "Ocupaciones elementales", "dónde vive más gente que trabaja en ocupaciones elementales", "n_ciuo_9", "n_ocupado", ""),
    ("🚌 Movilidad", "Viaje al trabajo en transporte público", "dónde más gente viaja al trabajo en transporte público", "n_transporte_publico", "(suma de n_transporte_*)", "El código lo calcula solo"),
    ("🚌 Movilidad", "Viaje al trabajo en bicicleta", "dónde más gente viaja al trabajo en bicicleta", "n_transporte_bicicleta", "(suma de n_transporte_*)", "El código lo calcula solo"),
    ("🏠 Hogares", "Jefatura de hogar femenina", "dónde hay más hogares con jefatura femenina", "n_jefatura_mujer", "n_hog", ""),
    ("🏠 Hogares", "Hogares unipersonales", "dónde hay más hogares de una sola persona", "n_hog_unipersonales", "n_hog", ""),
    ("🏠 Hogares", "Hogares solo de personas mayores", "dónde hay más hogares formados solo por personas de 60 años o más", "n_hog_60", "n_hog", ""),
    ("🏠 Hogares", "Arriendo sin contrato", "dónde hay más hogares que arriendan sin contrato", "n_tenencia_arrendada_sin_contrato", "n_hog", ""),
    ("🏠 Hogares", "Calefacción a leña", "dónde más hogares se calefaccionan con leña", "n_comb_calefaccion_lena", "n_hog", ""),
    ("🏠 Hogares", "Acceso a internet", "dónde hay más (o menos) hogares con internet", "n_internet", "n_hog", ""),
    ("🧱 Vivienda", "Hacinamiento", "dónde hay más viviendas hacinadas", "n_viv_hacinadas", "n_vp_ocupada", ""),
    ("🧱 Vivienda", "Viviendas irrecuperables", "dónde hay más viviendas irrecuperables", "n_viv_irrecuperables", "n_vp_ocupada", ""),
    ("🧱 Vivienda", "Agua por camión aljibe", "dónde más viviendas reciben agua de camión aljibe", "n_fuente_agua_camion", "n_vp_ocupada", ""),
]

CRUCES = [
    ("Personas mayores", "Hogares unipersonales", "¿Envejecer en soledad tiene una geografía?"),
    ("Población inmigrante", "Hacinamiento", "¿Coinciden migración y precariedad habitacional?"),
    ("Calefacción a leña", "Escolaridad promedio", "¿La leña es una cuestión de clima o de desigualdad?"),
    ("Jefatura de hogar femenina", "Arriendo sin contrato", "¿Dónde se cruzan género e inseguridad en la vivienda?"),
    ("Transporte público", "Ocupaciones elementales", "¿Quiénes dependen más del transporte público?"),
]

MAS = ("Hay **189 variables** en total, sobre población, hogares y viviendas: estas son solo algunas ideas. "
       "Para ver todas: abre `diccionario_para_IA.txt` en Colab, descarga el "
       f"[diccionario del INE en Excel]({EXCEL}), o pregúntale a Gemini: *«Con este diccionario, muéstrame "
       "todas las variables sobre [tema] y explícamelas en simple»*.")


def qmd():
    temas = list(dict.fromkeys(t for t, *_ in IDEAS))
    partes = ["::: {.panel-tabset}\n"]
    for tema in temas:
        partes.append(f"### {tema}\n\n| Idea | Variable | Denominador sugerido |\n|---|---|---|")
        for t, idea, _, var, den, nota in IDEAS:
            if t == tema:
                d = f"`{den}`" if den and not den.startswith("(") else (den or "—")
                partes.append(f"| {idea}{' · *' + nota + '*' if nota else ''} | `{var}` | {d} |")
        partes.append("")
    partes.append("### 🔀 Cruces\n\nIdeas para un mapa de **dos temas** (mapa bivariado):\n\n| Tema 1 | Tema 2 | Pregunta posible |\n|---|---|---|")
    partes += [f"| {a} | {b} | *{c}* |" for a, b, c in CRUCES]
    partes.append("\n:::\n")
    partes.append(f"::: {{.callout-note}}\n## ¿Quieres otra variable?\n{MAS}\n:::\n")
    return "\n".join(partes)


def html_ideas():
    import re
    temas = list(dict.fromkeys(t for t, *_ in IDEAS))
    bloques = []
    for tema in temas:
        chips = "".join(
            f'<button type="button" class="idea-chip" data-idea="{frase}" title="{var}">{idea}</button>'
            for t, idea, frase, var, *_ in IDEAS if t == tema)
        bloques.append(f'<div class="ideas-grupo"><p>{tema}</p><div>{chips}</div></div>')
    cruces = "".join(f'<li><b>{a}</b> × <b>{b}</b> — <i>{c}</i></li>' for a, b, c in CRUCES)
    mas = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", MAS)
    mas = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" rel="noopener">\1 ↗</a>', mas)
    mas = re.sub(r"\*(.+?)\*", r"<i>\1</i>", re.sub(r"`(.+?)`", r"<code>\1</code>", mas))
    return f'''
<div class="ideas-panel">
  <p class="ideas-tit">💡 ¿No sabes qué mapear? Toca una idea y se escribe sola en la pregunta 1</p>
  {"".join(bloques)}
  <details class="ideas-cruces"><summary>🔀 Ideas para cruzar dos temas</summary><ul>{cruces}</ul></details>
  <p class="ideas-mas">{mas}</p>
</div>'''


CSS = r"""
.ideas-panel{border:1px dashed var(--borde);border-radius:16px;padding:16px 18px;margin:16px 0;background:var(--sup2)}
.ideas-tit{margin:0 0 10px;font-weight:700}
.ideas-grupo{margin:10px 0}
.ideas-grupo p{margin:0 0 6px;font-size:.8rem;text-transform:uppercase;letter-spacing:.8px;color:var(--suave);font-weight:700}
.ideas-grupo div{display:flex;flex-wrap:wrap;gap:8px}
.idea-chip{font:inherit;font-size:.86rem;padding:6px 12px;border-radius:99px;border:1px solid var(--borde);background:var(--sup);color:var(--texto);cursor:pointer;transition:.15s}
.idea-chip:hover{border-color:var(--acento);color:var(--acento)}
.idea-chip.elegida{background:var(--acento);border-color:var(--acento);color:#fff}
.ideas-cruces{margin:12px 0 0}
.ideas-cruces summary{cursor:pointer;font-weight:600}
.ideas-cruces ul{margin:8px 0 0;padding-left:1.2em}
.ideas-mas{margin:12px 0 0;font-size:.9rem;color:var(--suave)}
"""

JS = r"""
document.querySelectorAll('[data-idea]').forEach(function(b){
  b.addEventListener('click', function(){
    var w = document.querySelector('[data-armador]'); if (!w) return;
    var campo = w.querySelector('[data-k="que"]'); campo.value = b.dataset.idea;
    campo.dispatchEvent(new Event('input', {bubbles: true}));
    document.querySelectorAll('[data-idea]').forEach(function(x){ x.classList.toggle('elegida', x === b); });
    w.scrollIntoView({behavior: 'smooth', block: 'center'});
  });
});
"""

if __name__ == "__main__":
    destino = Path(__file__).resolve().parent.parent / "_catalogo_variables.qmd"
    destino.write_text(qmd(), encoding="utf-8")
    print("ok", destino, len(IDEAS), "ideas")
