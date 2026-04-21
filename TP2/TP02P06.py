import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

nltk.download('brown')
nltk.download('stopwords')
nltk.download('wordnet')

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
        oracion = oracion.rstrip()
        oraciones.append(oracion + ".")
        oracion = ""

tokens = []
for i in range(0, 10):
    tokens.extend(word_tokenize(oraciones[i]))
    
puntuaciones = ",.?!;:()''“”"
comillas = "``"

tokens_limpios= [t for t in tokens if t not in stopwords.words('english') and t not in puntuaciones]
tokens_normalizados = []
tokens_frecuencia = {}

for palabra in tokens_limpios:
    if not palabra in comillas:
        if palabra.lower() not in tokens_frecuencia:
            tokens_frecuencia[palabra.lower()] = 1
        else:
            tokens_frecuencia[palabra.lower()] +=1
        


tokens_ordenados = {k: v for k, v in sorted(tokens_frecuencia.items(), key=lambda item: item[1], reverse=True)}

# for i, (palabra, frecuencia) in enumerate(list(tokens_ordenados.items())[:50]):
#     print(f"{i +1 } : {palabra} -> {frecuencia}")

#INCISO F
porter = PorterStemmer()

tokens_steming = {}
for palabra in tokens_ordenados:
    stem = porter.stem(palabra)
    if not stem in tokens_steming:
        tokens_steming[stem] = 1
    else:
        tokens_steming[stem] += 1
    
# print(tokens_steming)

#INCISO G
lemmatizer = WordNetLemmatizer()
tokens_lemmatizer = {}
for palabra in tokens_ordenados:
    lemma = lemmatizer.lemmatize(palabra)
    if not lemma in tokens_lemmatizer:
        tokens_lemmatizer[lemma] = 1
    else:
        tokens_lemmatizer[lemma] += 1

# print(tokens_lemmatizer)


#INCISO H
tokens_lemmatizer_v = {}

for palabra in tokens_ordenados:
    lemma = lemmatizer.lemmatize(palabra, pos='v')
    if not lemma in tokens_lemmatizer_v:
        tokens_lemmatizer_v[lemma] = 1
    else:
        tokens_lemmatizer_v[lemma] += 1

# print(tokens_lemmatizer_v)

#INCISO I
print("{0:20}{1:20}{2:20}{3:20}".format("Palabra", "Stemming", "Lemmatization", "Lemmatization (Verb)"))

for i in range(0,30):
    palabra = list(tokens_ordenados.keys())[i]
    stemming = porter.stem(palabra)
    lemmatization = lemmatizer.lemmatize(palabra)
    lemmatization_v = lemmatizer.lemmatize(palabra, pos='v')
    print("{0:20}{1:20}{2:20}{3:20}".format(palabra, stemming, lemmatization, lemmatization_v))

