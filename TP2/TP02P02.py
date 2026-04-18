import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, LancasterStemmer
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

porter = PorterStemmer()
lancaster = LancasterStemmer()

parrafo = """Information retrieval is the process of obtaining relevant information from a collection of
data. It involves searching for and retrieving information from various sources, such as
databases, the Internet, and digital libraries. Information retrieval is a vital aspect of many
fields, including business, education, and healthcare. In recent years, technological advances
have led to the development of sophisticated information retrieval systems that use artificial
intelligence and machine learning algorithms to provide more efficient and accurate results.
These systems can understand natural language queries and retrieve information from large
and complex data sets. As the amount of data available continues to grow exponentially, the
need for effective information retrieval systems becomes increasingly important.
Organizations are constantly seeking ways to improve their information retrieval processes to
gain a competitive edge and make better-informed decisions. With the right tools and strategies, 
information retrieval can provide valuable insights and help drive success in various industries."""

parrafoTokenizado = word_tokenize(parrafo)
puntuaciones = ",.?!;:()\""

for palabra in parrafoTokenizado:
    if palabra in stopwords.words('english') or palabra in puntuaciones:
        parrafoTokenizado.remove(palabra)


print("{0:20}{1:20}{2:20}".format("Palabra", "Porter", "Lancaster"))
for palabra in parrafoTokenizado:
    print("{0:20}{1:20}{2:20}".format(palabra, porter.stem(palabra), lancaster.stem(palabra)))


