"""Armador del prompt para Gemini: widget HTML/CSS/JS autocontenido.

Lo usan la guía autónoma (guia_html.py) y el Bloque 1 del notebook del desafío.
Funciona con los colores de la guía (--sup, --borde…) o con los de Bootstrap/Quarto (--bs-*).
"""
from pathlib import Path

PLANTILLA = """Hola Gemini. Estoy en Google Colab haciendo un ejercicio con datos del Censo 2024 de Chile. No sé programar: explícame todo en palabras simples.

Ya ejecuté los bloques 1 a 3 de este notebook: cargaron los datos y dejaron lista la función hacer_mapa(). NO escribas otro código, NO instales paquetes y NO cargues datos: solo necesito que prepares UNA línea que use esa función.

LO QUE QUIERO
- ¿Qué quiero mapear?: {que}
- ¿Dónde?: {nivel} de {lugar}
- ¿Lo cruzo con otro tema?: {cruce}
- Mi pregunta de investigación: {pregunta}
- Mi nombre (para el mapa): {autor}

LO QUE NECESITO DE TI
1. Busca en el diccionario (al final de este mensaje) la variable que mejor representa lo que quiero mapear y, si corresponde, la del cruce. Usa solo nombres que aparezcan textualmente en el diccionario; no inventes nombres.
2. Para cada variable usa como denominador el "denominador sugerido" del diccionario, salvo que haya una buena razón para cambiarlo (explícala).
3. Busca el código del territorio en la lista "TERRITORIOS DE CHILE": 5 dígitos si es una comuna, 3 si es una provincia, 2 si es una región. Ojo: muchas comunas se llaman igual que su provincia o su región; usa el nivel que te indiqué.
4. Si algo no está claro o hay más de una opción razonable, pregúntame antes de responder.

RESPONDE EN TRES PARTES
PARTE 1 · Lo que entendí: en 2 o 3 líneas simples, qué se va a mapear, dónde (nivel, nombre y código) y con qué cruce.
PARTE 2 · La línea para ejecutar: una celda de código con UNA sola línea, con este formato exacto (deja "" en lo que no corresponda, por ejemplo la segunda variable si no hay cruce):
hacer_mapa(escala="Comunal", territorio="05101", variable_1="...", denominador_1="...", nombre_1="...", variable_2="", denominador_2="", nombre_2="", titulo="...", autor="...")
(escala puede ser "Regional", "Provincial" o "Comunal"; territorio es el código; nombre_1 y nombre_2 son etiquetas breves en español de máximo 40 caracteres; titulo es una pregunta corta que no adelante resultados.)
PARTE 3 · Explicación simple: qué mide cada variable y a quiénes incluye, por qué ese denominador, qué cuidados tener al interpretar (datos faltantes, zonas con pocas personas, zonas rurales) y cómo leer el gráfico que se generará (ranking de comunas, distribución o dispersión).

DICCIONARIO Y TERRITORIOS:"""

CSS = r"""
.ap{--ap-sup:var(--sup,var(--bs-body-bg,#fff));--ap-sup2:var(--sup2,var(--bs-tertiary-bg,#f1f3f5));
  --ap-borde:var(--borde,var(--bs-border-color,#dee2e6));--ap-texto:var(--texto,var(--bs-body-color,#212529));
  --ap-suave:var(--suave,var(--bs-secondary-color,#6c757d));--ap-acento:var(--acento,#e8590c);--ap-ok:var(--verde,#2f9e44);
  border:1px solid var(--ap-borde);border-radius:16px;background:var(--ap-sup);color:var(--ap-texto);margin:18px 0;overflow:hidden}
.ap-cab{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 18px;border-bottom:1px solid var(--ap-borde);background:var(--ap-sup2)}
.ap-cab b{font-size:1.02rem} .ap-cab small{color:var(--ap-suave);display:block;font-size:.83rem}
.ap-cuerpo{display:grid;grid-template-columns:1fr 1fr;gap:0}
.ap-campos{padding:16px 18px;display:flex;flex-direction:column;gap:14px;border-right:1px solid var(--ap-borde)}
.ap label{display:block;font-weight:600;font-size:.92rem;margin-bottom:5px}
.ap label .n{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--ap-acento);color:#fff;font-size:.75rem;margin-right:6px}
.ap label .op{font-weight:400;color:var(--ap-suave);font-size:.82rem}
.ap input[type=text],.ap textarea,.ap select{width:100%;box-sizing:border-box;font:inherit;font-size:.93rem;color:var(--ap-texto);background:var(--ap-sup2);border:1px solid var(--ap-borde);border-radius:10px;padding:9px 11px}
.ap textarea{min-height:64px;resize:vertical}
.ap input:focus,.ap textarea:focus,.ap select:focus{outline:2px solid var(--ap-acento);outline-offset:1px}
.ap-fila{display:grid;grid-template-columns:150px 1fr;gap:8px}
.ap-seg{display:flex;gap:6px;margin-bottom:6px}
.ap-seg button{flex:1;font:inherit;font-size:.88rem;padding:7px;border-radius:10px;border:1px solid var(--ap-borde);background:var(--ap-sup2);color:var(--ap-texto);cursor:pointer}
.ap-seg button.on{background:var(--ap-acento);border-color:var(--ap-acento);color:#fff;font-weight:700}
.ap-ayuda{font-size:.8rem;color:var(--ap-suave);margin:4px 0 0}
.ap-salida{display:flex;flex-direction:column;min-width:0}
.ap-salida pre{flex:1;margin:0;padding:16px 18px;white-space:pre-wrap;word-break:break-word;font:12.5px/1.55 ui-monospace,Menlo,Consolas,monospace;color:var(--ap-texto);background:transparent;max-height:620px;overflow:auto;border:0}
.ap-salida pre mark{background:color-mix(in srgb,var(--ap-acento) 22%,transparent);color:inherit;border-radius:4px;padding:0 2px}
.ap-acciones{display:flex;gap:8px;flex-wrap:wrap;padding:12px 18px;border-top:1px solid var(--ap-borde);background:var(--ap-sup2)}
.ap-btn{font:inherit;font-weight:700;font-size:.9rem;border-radius:10px;padding:8px 14px;cursor:pointer;border:1px solid var(--ap-borde);background:var(--ap-sup);color:var(--ap-texto)}
.ap-btn.prim{background:var(--ap-acento);border-color:var(--ap-acento);color:#fff}
.ap-btn.ok{background:var(--ap-ok);border-color:var(--ap-ok);color:#fff}
.ap-sig{flex-basis:100%;margin:6px 0 0;font-size:.86rem;color:var(--ap-suave)}
.ap-respaldo{flex-basis:100%;height:90px;font:12px ui-monospace,Menlo,monospace;margin-top:6px}
.ap-dic{color:var(--ap-suave);font-style:italic}
.ap-ideas{border:1px dashed var(--ap-borde);border-radius:12px;padding:10px 12px;background:var(--ap-sup2)}
.ap-ideas p{margin:0 0 6px;font-size:.82rem;font-weight:700}
.ap-ideas div{display:flex;flex-wrap:wrap;gap:6px}
.ap-ideas button{font:inherit;font-size:.78rem;padding:4px 10px;border-radius:99px;border:1px solid var(--ap-borde);background:var(--ap-sup);color:var(--ap-texto);cursor:pointer}
.ap-ideas button.on,.ap-ideas button:hover{border-color:var(--ap-acento);color:var(--ap-acento)}
.ap-falta{font-size:.82rem;color:var(--ap-acento);align-self:center}
@media (max-width:800px){.ap-cuerpo{grid-template-columns:1fr}.ap-campos{border-right:0;border-bottom:1px solid var(--ap-borde)}.ap-fila{grid-template-columns:1fr}}
"""

HTML = r"""
<div class="ap" data-armador>
  <div class="ap-cab"><div><b>✦ Arma tu mensaje para Gemini</b><small>Responde con tus palabras. El mensaje de la derecha se arma solo (el diccionario se agrega al copiar).</small></div>
    <button type="button" class="ap-btn" data-ej>Ver un ejemplo</button></div>
  <div class="ap-cuerpo">
    <div class="ap-campos">
      __IDEAS__
      <div><label><span class="n">1</span>¿Qué quieres mapear?</label>
        <input type="text" data-k="que" placeholder="Ej.: dónde vive más gente mayor de 60 años">
        <p class="ap-ayuda">Dilo como se lo contarías a alguien. No necesitas saber el nombre de la variable.</p></div>
      <div><label><span class="n">2</span>¿Dónde?</label>
        <div class="ap-fila"><select data-k="nivel"><option value="la comuna">Una comuna</option><option value="la provincia">Una provincia</option><option value="la región">Una región</option></select>
        <input type="text" data-k="lugar" placeholder="Ej.: Valparaíso"></div>
        <p class="ap-ayuda">Elige el nivel: Santiago o Valparaíso, por ejemplo, son comuna y también provincia.</p></div>
      <div><label><span class="n">3</span>¿Lo quieres cruzar con otro tema?</label>
        <div class="ap-seg"><button type="button" class="on" data-cruce="no">No, un solo tema</button><button type="button" data-cruce="si">Sí, con otro tema</button></div>
        <input type="text" data-k="cruce" placeholder="Ej.: el nivel de escolaridad" hidden></div>
      <div><label><span class="n">4</span>Tu pregunta de investigación <span class="op">(opcional)</span></label>
        <textarea data-k="pregunta" placeholder="Ej.: ¿Las personas mayores se concentran en los cerros o en el plan de Valparaíso?"></textarea></div>
      <div><label><span class="n">5</span>Tu nombre <span class="op">(aparece en el mapa)</span></label>
        <input type="text" data-k="autor" placeholder="Ej.: Camila Rojas"></div>
    </div>
    <div class="ap-salida"><pre data-salida></pre>
      <div class="ap-acciones"><button type="button" class="ap-btn prim" data-copiar>📋 Copiar mensaje para Gemini</button>
        <span class="ap-falta" data-falta></span>
        <p class="ap-sig">Después: abre <b>✦ Gemini</b> (arriba a la derecha de Colab), pega con <b>Ctrl + V</b> y presiona <b>Enter</b>.</p>
        <textarea class="ap-respaldo" data-respaldo readonly hidden></textarea></div></div>
  </div>
</div>
"""

JS = r"""
(function(){
  const PLANTILLA = %s;
  const DICCIONARIO = %s;
  const esc = s => s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  document.querySelectorAll('[data-armador]').forEach(function(w){
    const campo = k => w.querySelector('[data-k="'+k+'"]');
    let cruce = 'no';
    const valores = () => ({
      que: campo('que').value.trim(), nivel: campo('nivel').value, lugar: campo('lugar').value.trim(),
      cruce: cruce === 'no' ? 'No, solo un tema' : ('Sí, con ' + (campo('cruce').value.trim() || '[¿con qué tema?]')),
      pregunta: campo('pregunta').value.trim() || '(todavía no la tengo; ayúdame a formularla al final)',
      autor: campo('autor').value.trim() || '[mi nombre]'
    });
    function armar(marcar){
      const v = valores();
      const rell = {que: v.que || '[¿qué quieres mapear?]', nivel: v.nivel, lugar: v.lugar || '[¿cuál?]', cruce: v.cruce, pregunta: v.pregunta, autor: v.autor};
      let t = PLANTILLA.replace(/\{(\w+)\}/g, (m, k) => marcar ? '\u0001' + rell[k] + '\u0002' : rell[k]);
      return t;
    }
    function pintar(){
      const t = esc(armar(true)).replace(/\u0001/g, '<mark>').replace(/\u0002/g, '</mark>')
        + '\n<span class="ap-dic">[+ diccionario y territorios: ' + Math.round(DICCIONARIO.length / 1000) + ' mil caracteres que se agregan al copiar]</span>';
      w.querySelector('[data-salida]').innerHTML = t;
      const v = valores(), falta = [];
      if (!v.que) falta.push('qué mapear'); if (!v.lugar) falta.push('dónde');
      if (cruce === 'si' && !campo('cruce').value.trim()) falta.push('con qué cruzar');
      w.querySelector('[data-falta]').textContent = falta.length ? 'Falta: ' + falta.join(', ') : '';
    }
    w.querySelectorAll('input,select,textarea').forEach(e => e.addEventListener('input', pintar));
    w.querySelectorAll('[data-cruce]').forEach(b => b.addEventListener('click', function(){
      cruce = b.dataset.cruce;
      w.querySelectorAll('[data-cruce]').forEach(x => x.classList.toggle('on', x === b));
      campo('cruce').hidden = cruce === 'no'; if (cruce === 'si') campo('cruce').focus(); pintar();
    }));
    w.querySelectorAll('[data-idea]').forEach(function(b){ b.addEventListener('click', function(){
      campo('que').value = b.dataset.idea; w.querySelectorAll('[data-idea]').forEach(x => x.classList.toggle('on', x === b)); pintar(); }); });
    w.querySelector('[data-ej]').addEventListener('click', function(){
      campo('que').value = 'dónde vive más gente mayor de 60 años';
      campo('nivel').value = 'la comuna'; campo('lugar').value = 'Valparaíso';
      w.querySelector('[data-cruce="si"]').click(); campo('cruce').value = 'el nivel de escolaridad';
      campo('pregunta').value = '¿Las personas mayores se concentran donde la escolaridad es más baja?'; campo('autor').value = 'Camila Rojas'; pintar();
    });
    w.querySelector('[data-copiar]').addEventListener('click', function(){
      const b = this, texto = armar(false) + '\n\n' + DICCIONARIO, original = b.textContent;
      const listo = () => { b.textContent = '✓ Copiado: ahora pégalo en Gemini'; b.classList.add('ok');
        setTimeout(() => { b.textContent = original; b.classList.remove('ok'); }, 3500); };
      const respaldo = () => { const a = w.querySelector('[data-respaldo]'); a.value = texto; a.hidden = false; a.focus(); a.select();
        let ok = false; try { ok = document.execCommand('copy'); } catch(e) {}
        if (ok) { listo(); } else { b.textContent = 'Selecciona el texto de abajo y cópialo con Ctrl + C'; } };
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(texto).then(listo, respaldo); } else { respaldo(); }
    });
    pintar();
  });
})();
"""


def ideas_html():
    from catalogo_variables import IDEAS
    chips = "".join(f'<button type="button" data-idea="{frase}" title="{var}">{idea}</button>'
                    for _, idea, frase, var, *_ in IDEAS)
    return f'<div class="ap-ideas"><p>💡 ¿No sabes qué mapear? Toca una idea</p><div>{chips}</div></div>'


def widget(diccionario_js='"__DICCIONARIO_JSON__"'):
    """Armador completo. En Colab, el Bloque 1 reemplaza "__DICCIONARIO_JSON__" por el texto real."""
    import json
    html = HTML.replace("__IDEAS__", ideas_html())
    js = JS % (json.dumps(PLANTILLA, ensure_ascii=False), diccionario_js)
    return f"<style>{CSS}</style>{html}<script>{js}</script>"


def widget_demo():
    """Versión de muestra para la guía y el sitio (sin diccionario real)."""
    import json
    demo = json.dumps("(Aquí va el diccionario completo: en Colab se agrega automáticamente al copiar.)")
    return widget(demo)


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent / "vista_armador.html"
    destino.write_text(widget_demo(), encoding="utf-8")
    print("ok", destino)
