import pandas as pd
from spellchecker import SpellChecker

spell = SpellChecker(language='es')
cache_correcciones = {}

def corregir_acentos_automatico(texto):
    if not isinstance(texto, str):
        return texto
    palabras = texto.split()
    palabras_corregidas = []
    for palabra in palabras:
        if palabra in cache_correcciones:
            palabras_corregidas.append(cache_correcciones[palabra])
        elif palabra in spell:  # Si la palabra ya es correcta, no se cambia
            cache_correcciones[palabra] = palabra
            palabras_corregidas.append(palabra)
        else:
            palabra_corregida = spell.correction(palabra) or palabra
            cache_correcciones[palabra] = palabra_corregida
            palabras_corregidas.append(palabra_corregida)
    return " ".join(palabras_corregidas)

ruta_archivo = r'C:\Users\Juan\Documents\DUMMY CATALOGOS\BOTAS 24-25 1E.xlsx'
df = pd.read_excel(ruta_archivo, dtype=str)

# Se asume que la columna que deseas corregir se encuentra en la posición N (índice 13)
columna_index = 12
if columna_index < len(df.columns):
    print(f"Corrigiendo la columna en la posición N (índice {columna_index})")
    df.iloc[:, columna_index] = df.iloc[:, columna_index].map(lambda x: corregir_acentos_automatico(x) if pd.notna(x) else "")
else:
    print(f"La columna con índice {columna_index} no existe en el DataFrame.")

df.to_excel(r'C:\Users\Juan\Documents\DUMMY CATALOGOS\BOTA2S.xlsx', index=False)
print("Corrección completada. Archivo guardado como 'archivo_corregido.xlsx'.")
