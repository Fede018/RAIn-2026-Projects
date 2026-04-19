import nltk
nltk.download('brown')

archivos = nltk.corpus.brown.fileids()

texto = nltk.corpus.brown.words('cg58')
oraciones =[]
oracion=""

for palabra in texto:
    if not palabra in ".?!":
        if palabra in ",":
            oracion = oracion.rstrip()
            oracion += palabra + " "
        else:    
            oracion += palabra + " "
    else:
        oraciones.append(oracion + ".")
        oracion = ""
    
for i in range(0, 10):
    print(f"{i+1}: {oraciones[i]}")

