import nltk
import os
from nltk.util import ngrams
nltk.download('punkt')
nltk.download('punkt_tab')

# Ruta correcta al archivo
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "data", "texto1.txt") #Utilizado para que siempre se encuentre el archivo sin importar desde donde se ejecute el script
initial_text = open(file_path, encoding="utf-8").read() 

puntuacion= ["¿","?",";",".",":","!","¡",",","[","]"]
lower_text=initial_text.lower()

def clean(text):
    for word in puntuacion:
        text = text.replace(word, "")
    return text

def n_gramas(text,n):
    n_grams = ngrams(nltk.word_tokenize(text), n)
    return [' '.join(grams) for grams in n_grams]

def mostrar_en_pantalla(n_grama,text):
    print("{0:20}{1:20}".format(text, "~~~~~~~~~~Palabras del texto proporcionado~~~~~~~~~~"))
    for word in n_grama:
        print("{0:20}{1:20}".format(text + ": ", word))

print("RESOLUCIÓN PUNTO 4")
text = clean(lower_text)
dos_grama= n_gramas(text,2)
mostrar_en_pantalla(dos_grama,"2-gramas")
print("##########################################################################################################")
tres_grama= n_gramas(text,3)
mostrar_en_pantalla(tres_grama,"3-gramas")
