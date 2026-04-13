import flet as ft
import fitz
import re
import collections

STOP_WORDS = {
    "a","acerca","actualmente","adelante","además","adonde","al","algo","algunos",
    "ante","antes","aquí","bajo","cada","casi","cerca","como","con","contra",
    "de","del","desde","donde","durante","el","él","ella","ellos","en","entre",
    "es","esta","está","este","esto","estos","fue","había","hasta","hay","la",
    "las","le","les","lo","los","más","me","mi","mismo","muy","no","nos",
    "o","otro","para","pero","por","que","qué","se","si","sí","sobre","su",
    "sus","también","tan","un","una","unas","uno","unos","y","ya"
}

def limpiar_texto(texto):
    texto = texto.lower()
    return re.findall(r'\b\w+\b', texto)

def generar_indice_frecuencia(rutas):
    indice = collections.defaultdict(lambda: collections.defaultdict(int))

    for i, ruta in enumerate(rutas):
        try:
            doc = fitz.open(ruta)
            for pagina in doc:
                palabras = limpiar_texto(pagina.get_text())
                for palabra in palabras:
                    if palabra not in STOP_WORDS:
                        indice[palabra][f"Documento {i+1}"] += 1
            doc.close()
        except:
            pass

    return indice

def consultar(palabra, indice):
    return dict(indice.get(palabra.lower(), {}))

# ------------------ UI ------------------
def main(page: ft.Page):
    page.title = "Frecuencia Pandora"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0f1c"

    archivos = ["data/1.pdf","data/2.pdf","data3.pdf","data/4.pdf","data/5.pdf"]
    indice = generar_indice_frecuencia(archivos)

    input_txt = ft.TextField(
        label="INGRESE CONSULTA",
        bgcolor="#11182b",
        color="white",
        border_color="#4cc9f0"
    )

    resultado = ft.Text(color="white")

    def buscar(e):
        palabra = input_txt.value.strip()
        res = consultar(palabra, indice)

        salida = f"Resultados para: {palabra}\n\n"

        for i in range(1,6):
            doc = f"Documento {i}"
            if doc in res:
                salida += f"✔ Encontrado en {doc} ({res[doc]} veces)\n"
            else:
                salida += f"✖ No se encontró en {doc}\n"

        resultado.value = salida
        page.update()

    def salir(e):
        page.window_close()

    # logo (cambiá la ruta)
    logo = ft.Image(src="/1.webp", width=140, height=140)

    boton_buscar = ft.ElevatedButton("Buscar", on_click=buscar, bgcolor="#4cc9f0", color="black")
    boton_salir = ft.ElevatedButton("Salir", on_click=salir, bgcolor="#7209b7", color="white")

    izquierda = ft.Column(
        [logo, input_txt, boton_buscar, boton_salir],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    derecha = ft.Container(
        content=resultado,
        bgcolor="#11182b",
        padding=20,
        border_radius=10,
        expand=True
    )

    page.add(
        ft.Row([
            ft.Container(izquierda, width=300, padding=20),
            derecha
        ], expand=True)
    )

ft.app(target=main, assets_dir="assets")