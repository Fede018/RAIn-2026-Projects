import flet as ft
import fitz
import re
import collections
import os

# ─────────────────────────────────────────────
#  STOP WORDS
# ─────────────────────────────────────────────
STOP_WORDS = {
    "a","acerca","actualmente","adelante","además","adonde","al","algo","algunos",
    "ante","antes","aquí","bajo","cada","casi","cerca","como","con","contra",
    "de","del","desde","donde","durante","el","él","ellsa","ellos","en","entre",
    "es","esta","está","este","esto","estos","fue","había","hasta","hay","la",
    "las","le","les","lo","los","más","me","mi","mismo","muy","no","nos",
    "o","otro","para","pero","por","que","qué","se","si","sí","sobre","su",
    "sus","también","tan","un","una","unas","uno","unos","y","ya","e","ni",
    "sin","según","tras","mediante","aunque","porque","pues","así","ser","sido",
    "tiene","tienen","tener","hacer","hace","han","haber","puede","pueden",
    "debe","deben","cuando","cual","cuales","todo","todos","toda","todas",
    "era","eran","son","nos","ellas","nosotros","vosotros","dicho","forma",
    "modo","parte","caso","vez","bien","solo","sólo","cabo","fin","través"
}

def limpiar_texto(texto):
    return re.findall(r'\b[a-záéíóúüñ]{2,}\b', texto.lower())

def resolver_rutas(nombres):
    candidatos_base = [
        "",                          # carpeta actual
        os.path.dirname(os.path.abspath(__file__)),  # carpeta del script
        os.path.expanduser("~"),     # home
        "/mnt/user-data/uploads/",   # uploads del entorno
        "/tmp/",
    ]
    rutas_ok = []
    for nombre in nombres:
        encontrado = False
        for base in candidatos_base:
            ruta = os.path.join(base, nombre) if base else nombre
            if os.path.isfile(ruta):
                rutas_ok.append(ruta)
                encontrado = True
                break
        if not encontrado:
            print(f"[WARN] No se encontró: {nombre}")
    return rutas_ok

# ─────────────────────────────────────────────
#  CONSTRUCCIÓN DE ÍNDICES
# ─────────────────────────────────────────────
def generar_indices(rutas):
    indice_pos  = collections.defaultdict(lambda: collections.defaultdict(list))
    indice_freq = collections.defaultdict(lambda: collections.defaultdict(int))

    for i, ruta in enumerate(rutas):
        doc_id = f"PDF_{i+1}"
        try:
            doc = fitz.open(ruta)
            pos_global     = 0
            oracion_global = 0
            for pagina in doc:
                texto = pagina.get_text()
                oraciones = re.split(r'(?<=[.!?])\s+', texto)
                for oracion in oraciones:
                    palabras = limpiar_texto(oracion)
                    for palabra in palabras:
                        if palabra not in STOP_WORDS:
                            indice_pos[palabra][doc_id].append((pos_global, oracion_global))
                            indice_freq[palabra][doc_id] += 1
                            pos_global += 1
                    oracion_global += 1
            doc.close()
        except Exception as ex:
            print(f"[ERROR] {ruta}: {ex}")

    return indice_pos, indice_freq

# ─────────────────────────────────────────────
#  BÚSQUEDA DE SIMILARES
# ─────────────────────────────────────────────
def buscar_similares(termino, indice, max_resultados=10):
    t = termino.lower().strip()
    prefijo = t[:4] if len(t) >= 4 else t
    candidatos = {p for p in indice if t in p or p.startswith(prefijo)}
    return sorted(candidatos, key=lambda p: sum(indice[p][d] for d in indice[p]), reverse=True)[:max_resultados]

# ─────────────────────────────────────────────
#  LAS 4 CONSULTAS POSICIONALES
# ─────────────────────────────────────────────
def _proximidad(p1, p2, distancia, indice_pos):
    resultados = {}
    for doc in set(indice_pos.get(p1, {})) & set(indice_pos.get(p2, {})):
        matches = [(pos1, pos2, abs(pos1-pos2))
                   for pos1, _ in indice_pos[p1][doc]
                   for pos2, _ in indice_pos[p2][doc]
                   if abs(pos1-pos2) <= distancia]
        if matches:
            resultados[doc] = sorted(matches, key=lambda x: x[2])
    return resultados

def q1_adyacente(p1, p2, ip):   return _proximidad(p1, p2, 1, ip)
def q2_cerca(p1, p2, ip):       return _proximidad(p1, p2, 3, ip)
def q3_n(p1, p2, n, ip):        return _proximidad(p1, p2, n, ip)

def q4_misma_oracion(p1, p2, ip):
    resultados = {}
    for doc in set(ip.get(p1, {})) & set(ip.get(p2, {})):
        matches = [(pos1, pos2, or1)
                   for pos1, or1 in ip[p1][doc]
                   for pos2, or2 in ip[p2][doc]
                   if or1 == or2]
        if matches:
            resultados[doc] = matches
    return resultados

# ─────────────────────────────────────────────
#  PROCESADOR
# ─────────────────────────────────────────────
def procesar(texto, indice_pos, indice_freq):
    partes = texto.lower().strip().split()
    if not partes:
        return None

    # 1 palabra → frecuencia
    if len(partes) == 1:
        t = partes[0]
        freq = dict(indice_freq.get(t, {}))
        pos  = {doc: indice_pos[t][doc] for doc in indice_pos.get(t, {})}
        if freq:
            return {"modo": "simple", "termino": t, "freq": freq, "pos": pos}
        return {"modo": "no_encontrado", "termino": t,
                "sugs": buscar_similares(t, indice_freq)}

    # 2 palabras → 4 consultas automáticas
    if len(partes) == 2:
        p1, p2 = partes
        s1 = [] if p1 in indice_pos else buscar_similares(p1, indice_freq)
        s2 = [] if p2 in indice_pos else buscar_similares(p2, indice_freq)
        if s1 or s2:
            return {"modo": "sugerencias", "p1": p1, "p2": p2, "sugs1": s1, "sugs2": s2}
        return {
            "modo": "auto4", "p1": p1, "p2": p2,
            "q1": q1_adyacente(p1, p2, indice_pos),
            "q2": q2_cerca(p1, p2, indice_pos),
            "q3": q3_n(p1, p2, 10, indice_pos),
            "q4": q4_misma_oracion(p1, p2, indice_pos),
        }

    # 2 palabras + modificador
    if len(partes) == 3:
        p1, p2, mod = partes
        s1 = [] if p1 in indice_pos else buscar_similares(p1, indice_freq)
        s2 = [] if p2 in indice_pos else buscar_similares(p2, indice_freq)
        if s1 or s2:
            return {"modo": "sugerencias", "p1": p1, "p2": p2, "sugs1": s1, "sugs2": s2}
        if mod == "adyacente":
            return {"modo":"q1","p1":p1,"p2":p2,"res":q1_adyacente(p1,p2,indice_pos)}
        if mod == "cerca":
            return {"modo":"q2","p1":p1,"p2":p2,"res":q2_cerca(p1,p2,indice_pos)}
        if mod == "oracion":
            return {"modo":"q4","p1":p1,"p2":p2,"res":q4_misma_oracion(p1,p2,indice_pos)}
        if mod.lstrip('-').isdigit():
            n = abs(int(mod))
            return {"modo":"q3","p1":p1,"p2":p2,"n":n,"res":q3_n(p1,p2,n,indice_pos)}

    return None

# ─────────────────────────────────────────────
#  FORMATEO
# ─────────────────────────────────────────────
SEP = "─" * 50

def fmt_matches(datos, max_show=8):
    if not datos:
        return "    (sin ocurrencias)"
    total = sum(len(v) for v in datos.values())
    lineas = []
    for doc, matches in sorted(datos.items()):
        lineas.append(f"  📄 {doc}  ({len(matches)} ocurrencia{'s' if len(matches)>1 else ''})")
        for t in matches[:max_show]:
            pos1, pos2, extra = t
            lineas.append(f"     pos({pos1}) ↔ pos({pos2})  dist/or={extra}")
        if len(matches) > max_show:
            lineas.append(f"     ... y {len(matches)-max_show} más")
    lineas.append(f"\n  ✅ Total: {total} ocurrencia{'s' if total!=1 else ''} en {len(datos)} doc(s)")
    return "\n".join(lineas)

def formatear(r):
    if r is None:
        return "⚠️  Formato no reconocido.\nEjemplos:\n  chatgpt\n  chatgpt estudiantes\n  chatgpt docentes oracion"

    modo = r["modo"]

    if modo == "no_encontrado":
        t, sugs = r["termino"], r.get("sugs", [])
        txt = f"❌  «{t}» no está en el índice.\n"
        if sugs:
            txt += "\n¿Quisiste decir?\n" + "\n".join(f"  • {s}" for s in sugs)
        return txt

    if modo == "sugerencias":
        txt = ""
        if r["sugs1"]:
            txt += f"⚠️  «{r['p1']}» no encontrado. ¿Quisiste decir?\n"
            txt += "\n".join(f"  • {s}" for s in r["sugs1"]) + "\n\n"
        if r["sugs2"]:
            txt += f"⚠️  «{r['p2']}» no encontrado. ¿Quisiste decir?\n"
            txt += "\n".join(f"  • {s}" for s in r["sugs2"])
        return txt

    if modo == "simple":
        t, freq, pos = r["termino"], r["freq"], r["pos"]
        lineas = [f"🔎  Frecuencia de «{t}»", SEP]
        for doc, f in sorted(freq.items()):
            ps = [str(p[0]) for p in pos.get(doc, [])][:20]
            sufijo = "..." if f > 20 else ""
            lineas.append(f"  📄 {doc}   freq: {f}")
            lineas.append(f"     posiciones: [{', '.join(ps)}{sufijo}]")
        return "\n".join(lineas)

    if modo == "auto4":
        p1, p2 = r["p1"], r["p2"]
        lineas = [
            f"🔎  «{p1}» + «{p2}»  —  4 consultas posicionales",
            SEP, "",
            "Q1  ADYACENTE  (distancia = 1)",
            fmt_matches(r["q1"]), "",
            "Q2  CERCA-DE   (distancia ≤ 3)",
            fmt_matches(r["q2"]), "",
            "Q3  A-10-TÉRMINOS (distancia ≤ 10)",
            fmt_matches(r["q3"]), "",
            "Q4  MISMA ORACIÓN",
            fmt_matches(r["q4"]),
        ]
        return "\n".join(lineas)

    etiquetas = {
        "q1": "Q1 ADYACENTE (dist=1)",
        "q2": "Q2 CERCA-DE (dist≤3)",
        "q3": f"Q3 A-{r.get('n','?')}-TÉRMINOS",
        "q4": "Q4 MISMA ORACIÓN",
    }
    label = etiquetas.get(modo, modo.upper())
    res = r["res"]
    lineas = [f"🔎  {label} — «{r['p1']}» | «{r['p2']}»", SEP]
    if not res:
        lineas.append("❌  Sin resultados con esa relación.")
        if modo == "q1":
            lineas.append("   Probá con 'cerca' o un número mayor.")
    else:
        lineas.append(fmt_matches(res))
    return "\n".join(lineas)

# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────
def main(page: ft.Page):
    page.title = "Índice Invertido Posicional"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0f1c"
    page.padding = 0
    page.window_width  = 1100
    page.window_height = 700

    # Carga
    carga = ft.Text("⏳  Indexando documentos...", color="#4cc9f0", size=14)
    page.add(ft.Container(carga, padding=40))
    page.update()

    nombres = ["1.pdf","2.pdf","3.pdf","4.pdf","5.pdf"]
    rutas = resolver_rutas(nombres)
    indice_pos, indice_freq = generar_indices(rutas)
    total_t = len(indice_freq)
    page.controls.clear()

    # ── Widgets ───────────────────────────────
    input_txt = ft.TextField(
        label="INGRESE CONSULTA",
        bgcolor="#11182b",
        color="white",
        label_style=ft.TextStyle(color="#4cc9f0"),
        border_color="#1e3a5f",
        focused_border_color="#4cc9f0",
        on_submit=lambda e: buscar(e),
    )

    resultado = ft.Text(
        value='Ingresá una consulta para comenzar.\n\nEjemplos que funcionan:\n'
              '  chatgpt\n  chatgpt estudiantes\n  inteligencia artificial\n'
              '  chatgpt docentes oracion\n  aprendizaje programacion 15',
        color="white",
        selectable=True,
        font_family="monospace",
        size=12,
    )

    ayuda = ft.Text(
        "Consultas disponibles:\n"
        "• palabra\n"
        "• palabra1 palabra2              (4 consultas auto)\n"
        "• palabra1 palabra2 adyacente    (Q1)\n"
        "• palabra1 palabra2 cerca        (Q2)\n"
        "• palabra1 palabra2 5            (Q3)\n"
        "• palabra1 palabra2 oracion      (Q4)\n",
        color="#9ca3af",
        size=12,
    )

    estado = ft.Text(
        f"📚 {len(rutas)} docs · {total_t} términos indexados",
        color="#4cc9f0" if total_t > 0 else "#ef4444",
        size=11,
        font_family="monospace",
    )

    def buscar(e):
        consulta = input_txt.value.strip()
        if not consulta:
            resultado.value = "⚠️ Ingrese una consulta"
        else:
            r = procesar(consulta, indice_pos, indice_freq)
            resultado.value = formatear(r)
        page.update()

    def salir(e):
        page.window_close()

    # Logo (opcional — si existe)
    logo_path = "1.webp"
    try:
        logo = ft.Image(src="1.webp", width=140, height=140)
    except:
        logo = ft.Text("📚", size=60)

    izquierda = ft.Column(
        [
            logo,
            estado,
            input_txt,
            ayuda,
            ft.ElevatedButton(
                "Buscar", on_click=buscar,
                bgcolor="#4cc9f0", color="#0a0f1c"
            ),
            ft.ElevatedButton(
                "Salir", on_click=salir,
                bgcolor="#7209b7", color="white"
            ),
        ],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    derecha = ft.Container(
        content=ft.Column(
            [resultado],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        bgcolor="#11182b",
        padding=20,
        border_radius=10,
        expand=True,
    )

    page.add(
        ft.Row([
            ft.Container(izquierda, width=320, padding=20),
            derecha,
        ], expand=True)
    )
    page.update()


ft.app(target=main)