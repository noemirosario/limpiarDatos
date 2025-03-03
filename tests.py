import pandas as pd
import spacy
from spellchecker import SpellChecker

# Cargar modelo en español
nlp = spacy.load("es_core_news_sm")

# Corrector ortográfico en español
spell = SpellChecker(language="es")

def corregir_acentos(texto):
    palabras = texto.split()  # Dividir en palabras
    palabras_corregidas = []

    for palabra in palabras:
        # Si la palabra sin acento está mal, corregirla
        palabra_correcta = spell.correction(palabra)
        if palabra_correcta:
            palabras_corregidas.append(palabra_correcta)
        else:
            palabras_corregidas.append(palabra)

    return " ".join(palabras_corregidas)  # Unir palabras corregidas

# Ejemplo de DataFrame con palabras sin acento
df = pd.DataFrame({'texto': ['cancion bonita', 'arbol grande', 'corazon feliz', 'pasion intensa']})

# Aplicar corrección
df['texto_corregido'] = df['texto'].apply(corregir_acentos)

print(df)
