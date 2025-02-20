
import pandas as pd

# Rutas de los archivos de entrada y salida (modifícalas según sea necesario)

archivo_1 = r"C:\Users\Juan\Downloads\Libro1.xlsx"  # Primer archivo (base)

archivo_2 = r"C:\Users\Juan\Downloads\vacantes20.xlsx"  # Segundo archivo (datos adicionales)

archivo_salida = r"C:\Users\Juan\Downloads\unido.xlsx"  # Archivo final combinado

# Cargar ambos archivos

df1 = pd.read_excel(archivo_1, dtype=str)  # Primer archivo (base)

df2 = pd.read_excel(archivo_2, dtype=str)  # Segundo archivo (datos adicionales)

# Filtrar las columnas coincidentes entre los dos archivos

columnas_comunes = df1.columns.intersection(df2.columns)

# Mantener solo las columnas que existen en ambos archivos

df2_filtrado = df2[columnas_comunes]

# Concatenar los datos: agregar df2 después de df1

df_final = pd.concat([df1, df2_filtrado], ignore_index=True)

# Guardar el resultado en un nuevo archivo de Excel

df_final.to_excel(archivo_salida, index=False)

print(f"Archivo combinado guardado en: {archivo_salida}")

