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
    return re.findall(r'\b\w+\b', texto.lower())

def generar_indice_posicional(rutas):
    indice = collections.defaultdict(lambda: collections.defaultdict(list))

    for i, ruta in enumerate(rutas):
        try:
            doc = fitz.open(ruta)
            pos = 0
            for pagina in doc:
                palabras = limpiar_texto(pagina.get_text())
                for palabra in palabras:
                    if palabra not in STOP_WORDS:
                        indice[palabra][f"PDF_{i+1}"].append(pos)
                    pos += 1
            doc.close()
        except:
            pass

    return indice

def consultar(palabra, indice):
    return dict(indice.get(palabra.lower(), {}))

# ------------------ UI ------------------
def main(page: ft.Page):
    page.title = "Índice Posicional"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0f1c"

    archivos = ["1.pdf","2.pdf","3.pdf","4.pdf","5.pdf"]
    indice = generar_indice_posicional(archivos)

    input_txt = ft.TextField(label="INGRESE CONSULTA", bgcolor="#11182b", color="white")

    resultado = ft.Text(color="white")

    def buscar(e):
        palabra = input_txt.value.strip()
        res = consultar(palabra, indice)
        
        if not palabra:
            resultado.value = "⚠️ Ingrese una palabra"
        elif not res:
            resultado.value = "❌ La palabra no se encontró en ningún documento"
        else:
            salida = f"Resultado de búsqueda: '{palabra}'\n\n"

            for doc, posiciones in res.items():
                num = doc.split("_")[1]

                salida += f"Palabra encontrada en el documento {num}\n"
                salida += "En la/s posición/es: "
                salida += " ".join(str(p) for p in posiciones)
                salida += "\n\n"

            resultado.value = salida

        page.update()

    def salir(e):
        page.window_close()

    logo = ft.Image(src="1.webp", width=140, height=140)

    izquierda = ft.Column(
        [logo, input_txt,
         ft.ElevatedButton("Buscar", on_click=buscar, bgcolor="#4cc9f0"),
         ft.ElevatedButton("Salir", on_click=salir, bgcolor="#7209b7")],
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

ft.app(target=main)