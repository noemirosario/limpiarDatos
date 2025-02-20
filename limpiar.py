import os  # Librería OPENPYXL para gestionar archivos y carpetas en la computadora
import pandas as pd  # Librería PANDAS para manipular archivos de Excel y convertirlos en CSV

CARPETA_ENTRADA = r"C:\Users\Juan\Downloads\pruebas"  # Carpeta donde están los archivos de Excel originales
CARPETA_SALIDA = r"C:\Users\Juan\Downloads\pruebas\1"  # Carpeta donde se guardarán los archivos procesados en formato CSV

# Asegurar que la carpeta de salida es realmente un directorio y no un archivo
if not os.path.isdir(CARPETA_SALIDA):
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

# Variables agregadas para corregir el código
# 1. Columnas a eliminar
COLUMNAS_A_ELIMINAR = ["Pag Ant", "Catalogo Anterior", "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                      "Tallas reales", "Equivalencia", "Corte", "Calzado = Suela Ropa = Composicion", "Forro",
                       "Altura Tacón / Alt Sin Plataforma","Comprador", "Sección", "Seccion", "Tipo de Seguridad", "Publico Objetivo",
                       "Ubicación", "Calzado = Suela Ropa = Composicion"]

# 2. Mapeo de nombres de columnas
MAPEADO_COLUMNAS = {
    "Articulo": "@foto",
    "Marca Price": "Marca",
    "Estilo Prov": "Estilo",
    "RANGO DE TALLAS": "Tallas",
    "1/2#": "Enteros",
    "Observacion": "Modelo"
}

# 3. Orden deseado de las columnas en el archivo final
ORDEN_COLUMNAS = ["@foto", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N", "Pag Act"]

def ajustar_tallas(valor):
    """
    Identifica si la celda corresponde a tallas de calzado o de ropa y aplica la transformación adecuada.
    """
    if pd.isnull(valor):
        return valor

    valor = str(valor).replace("-", "/")
    tallas = valor.split("/")

    # Verificar si el valor sigue el patrón de tallas de calzado (números con un guion intermedio)
    if all(talla.replace(".", "").isdigit() for talla in tallas):
        tallas = [str(int(float(t))) if float(t).is_integer() else str(float(t)) for t in tallas]
        return "=" + "\"" + "-".join(tallas) + "\""  # Prevención de conversión a fecha en Excel

    # Lista ordenada de tallas de ropa
    lista_tallas = ["XXCH", "XCH", "CH", "M", "G", "XG", "XXG", "XXXG"]

    # Verificar si el valor corresponde a una corrida de tallas de ropa
    if tallas[0] in lista_tallas and tallas[-1] in lista_tallas:
        try:
            inicio = lista_tallas.index(tallas[0])
            fin = lista_tallas.index(tallas[-1])
            return "/".join(lista_tallas[inicio:fin + 1])
        except ValueError:
            return valor

    return valor


def ajustar_enteros(valor_tallas, valor_enteros):
    """
    Ajusta la columna "Enteros" en función del contenido de las tallas.
    """
    if valor_enteros in ["Sí", "Si"]:
        return ""

    if valor_enteros == "No":
        # Verificar si el valor en "Tallas" es un rango de números enteros
        if isinstance(valor_tallas, str) and "-" in valor_tallas:
            partes = valor_tallas.replace("=\"", "").replace("\"", "").split("-")
            if all(parte.isdigit() for parte in partes):
                return "solo enteros"
        return ""  # Si no cumple la condición, dejar vacío

    return valor_enteros


def limpiar_y_guardar_archivo(ruta_entrada, ruta_salida):
    """
    Procesa el archivo de Excel aplicando las transformaciones necesarias y lo guarda en formato CSV.
    """
    try:
        # 1. Eliminar las primeras 4 filas
        df = pd.read_excel(ruta_entrada, engine="openpyxl", skiprows=4)

        # 1.1 Eliminar primera columna si solo contiene índices sin encabezado
        if df.columns[0] == df.index.name or df.iloc[:, 0].is_monotonic_increasing:
            df.drop(df.columns[0], axis=1, inplace=True)

        # 2. Eliminar columnas innecesarias
        df.columns = df.columns.str.replace("\n", "", regex=True)  # Reemplazar saltos de línea en los nombres de las columnas
        df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True)

        # 3. Duplicar la primera columna y colocarla en la segunda posición
        df.insert(1, "ID", df.iloc[:, 0])

        # 4. Renombrar columnas según mapeo
        for columna_actual, nueva_columna in MAPEADO_COLUMNAS.items():
            if columna_actual in df.columns:
                df.rename(columns={columna_actual: nueva_columna}, inplace=True)
            else:
                print(f"⚠️ Advertencia: La columna '{columna_actual}' no se encontró en el archivo y no se pudo renombrar.")

        # 5. Reordenar columnas según el orden especificado, ignorando las que no estén en el DataFrame
        columnas_validas = [col for col in ORDEN_COLUMNAS if col in df.columns]
        df = df[columnas_validas + [col for col in df.columns if col not in columnas_validas]]

        # 6. Concatenar valores de la primera columna con .psd
        df.iloc[:, 0] = df.iloc[:, 0].astype(str) + ".psd"
        df.iloc[:, 0] = df.iloc[:, 0].astype("string")  # Asegurar compatibilidad con pandas moderno

        # 7. Aplicar ajustes a la columna de tallas
        if "Tallas" in df.columns:
            df["Tallas"] = df["Tallas"].apply(ajustar_tallas)

        # 8. Aplicar ajustes a la columna de enteros
        if "Enteros" in df.columns and "Tallas" in df.columns:
            df["Enteros"] = df.apply(lambda row: ajustar_enteros(row["Tallas"], row["Enteros"]), axis=1)

        # Guardar el archivo procesado en CSV
        df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
        print(f"✅ Archivo procesado y guardado en: {ruta_salida}")
    except Exception as e:
        print(f"⚠️ Error al procesar {ruta_entrada}: {e}")


# Procesar todos los archivos en la carpeta de entrada
for nombre_archivo in os.listdir(CARPETA_ENTRADA):
    # Ignorar archivos temporales de Excel que comienzan con '~$'
    if nombre_archivo.startswith('~$'):
        print(f"⚠️ Archivo temporal ignorado: {nombre_archivo}")
        continue
    if nombre_archivo.endswith(".xlsx") or nombre_archivo.endswith(".xls"):
        ruta_entrada = os.path.join(CARPETA_ENTRADA, nombre_archivo)
        ruta_salida = os.path.join(CARPETA_SALIDA,
                                   nombre_archivo.replace(".xlsx", ".csv").replace(".xls", ".csv"))
        limpiar_y_guardar_archivo(ruta_entrada, ruta_salida)

print("🎯 Proceso finalizado.")
