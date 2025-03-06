import os
import pandas as pd
import streamlit as st
import re
import numpy as np
from io import BytesIO


# Configuración de la app
st.title("📂 ETL de Dummys de Artículos para su integración hacia InDesign")
st.write("Sube un archivo de Excel y procesa la información para generar un CSV limpio.")

# Castaña, Coñac, Olivo, Frappe, Crema, Terracota, Latte

diccionario_palabras = {
    "SINTETICO": "SINTÉTICO",
    "CAFE": "CAFÉ",
    "CARMIN": "CARMÍN",
    "NEON": "NEÓN",
    "TURQUESA": "TURQUESA",  # No requiere acento
    "BALON": "BALÓN",
    "AMBAR": "ÁMBAR",
    "OSTION": "OSTIÓN",
    "FIUSHA": "FIUSHA",  # Verifica si la forma correcta es esta o "FIUŠA" según el término que uses
    "MARRON": "MARRÓN",
    "INDIGO": "ÍNDIGO",
    "PURPURA": "PÚRPURA",
    "COMPOSICION": "COMPOSICIÓN",
    "ALGODON": "ALGODÓN",
    "POLIESTER": "POLIÉSTER",
    "RAYON": "RAYÓN",
    "ACRILICO": "ACRÍLICO",
    "CANAMO": "CÁÑAMO",
    "LYOCELL": "LYOCELL",  # Se escribe igual
    "ETNICO": "ÉTNICO",
    "MELON": "MELÓN",
    "ELECTRICO": "ELÉCTRICO",
    "SANDALO": "SÁNDALO",
    "CINTURON": "CINTURÓN",
    "BOXER": "BÓXER",
    "UNICO": "ÚNICO",
    "BATERIA": "BATERÍA",
    "NACAR": "NÁCAR",
    "METALICO": "METÁLICO",
    "LASER": "LÁSER"
}

def agregar_tildes_upper(texto):
    if not isinstance(texto, str):
        return texto
    # Recorremos el diccionario y usamos expresiones regulares para reemplazar palabras completas
    for sin_acento, con_acento in diccionario_palabras.items():
        texto = re.sub(rf'\b{sin_acento}\b', con_acento, texto)
    return texto

# Función para formatear tallas
def es_talla_numerica(valor_tallas):
    if pd.isnull(valor_tallas):
        return False
    # Convierte a string
    txt = str(valor_tallas).strip()
    # Quita posibles '="' al inicio y '"' al final, p.e. '="7-10"'
    txt = re.sub(r'^="|"$', '', txt)
    # Reemplaza '-' por '/', para manejar rangos como '7-10'
    txt = txt.replace('-', '/')
    # Separa por '/'
    partes = txt.split('/')
    # Verifica que cada parte sea numérica (int o float)
    for p in partes:
        # Elimina un posible punto decimal para usar isdigit()
        # o, si prefieres, podrías intentar un float(p) y atrapar ValueError
        p_limpio = p.replace('.', '', 1)  # Solo un punto posible
        if not p_limpio.isdigit():
            return False
    return True
def ajustar_tallas(valor):
    if pd.isnull(valor):
        return ""

    valor = str(valor).replace("-", "/")
    tallas = valor.split("/")

    # Verificar si el valor sigue el patrón de tallas de calzado (numérico)
    if all(talla.replace(".", "").isdigit() for talla in tallas):
        # Convertir a float, eliminar duplicados y ordenar
        tallas_float = sorted(set(float(t) for t in tallas))
        # Convertir enteros a str sin decimales
        tallas_str = [str(int(t)) if t.is_integer() else str(t) for t in tallas_float]
        if len(tallas_str) > 1:
            return f'="{tallas_str[0]}-{tallas_str[-1]}"'
        else:
            return f'="{tallas_str[0]}"'

    # Lista de tallas tipo ropa
    lista_tallas = ["XXCH", "XCH", "CH", "M", "G", "XG", "XXG", "XXXG"]

    # Verificar si son tallas de ropa en la lista y podemos "expandir"
    if tallas[0] in lista_tallas and tallas[-1] in lista_tallas:
        try:
            inicio = lista_tallas.index(tallas[0])
            fin = lista_tallas.index(tallas[-1])
            return "-".join(lista_tallas[inicio:fin+1])
        except ValueError:
            return valor
    return valor
def ajustar_enteros(valor_enteros, valor_tallas):
    # Si la columna "1/2#" contiene "Sí" o "Si", retorna ""
    if valor_enteros in ["Sí", "Si"]:
        return ""

    # Si la columna "1/2#" contiene "No", revisamos si las tallas son numéricas
    if valor_enteros == "No":
        if es_talla_numerica(valor_tallas):
            return "solo enteros"
        else:
            # Si no es numérico, devolvemos cadena vacía en lugar de "No"
            return ""

    # En cualquier otro caso, dejamos el valor tal cual
    return valor_enteros
def modificar_descripcion(descripcion):
    if isinstance(descripcion, float):
        descripcion = str(descripcion)
    descripcion = descripcion.strip().lower()

    mapeo_descripciones = {
        "bota corta": "BC",
        "bota larga": "BL",
        "botin": "BN",
        "bota extra larga": "BXL",
        "bota 3/4": "BOTA 3/4",
        "sueco": "SUECO",
        "cerrado": "CERRADO",
        "agujeta": "AGUJETA",
        "contactel / agujeta": "CONTACTEL / AGUJETA",
        "contactel": "CONTACTEL",
        "no aplica": "NO APLICA",
        "protector de callos de gel 4 pzas": "PROTECTOR DE CALLOS DE GEL 4 PZAS",
        "protector de juanete": "PROTECTOR DE JUANETE"
    }
    # Retornar el valor formateado si existe en el diccionario, de lo contrario, retornar el valor original
    return mapeo_descripciones.get(descripcion, descripcion)
def concatenar_altura(altura):
    # Si la altura es 0 en cualquier forma (0, 0.0, 0.00), devolver una cadena vacía
    if altura == 0 or altura == 0.0:
        return ""

    # Si la altura es un número decimal y termina en .0, eliminamos el ".0"
    if isinstance(altura, float):
        if altura.is_integer():  # Si el número tiene parte decimal igual a 0 (9.0, 100.0, etc.)
            altura = int(altura)  # Convertimos a entero para eliminar la parte decimal

    # Convertimos la altura a cadena y agregamos "cm"
    return str(altura) + "cm"
def modificar_suela(suela):
    if suela == "NO APLICA":
        return ""
    else:
        return suela
def extraer_palabra_plantilla(texto):
    # Convertir a string si no es ya una cadena
    if not isinstance(texto, str):
        texto = str(texto)
    palabras = texto.split()  # Dividimos el texto en palabras
    if 'PLANTILLA' in palabras and len(palabras) >= 3:
        return palabras[2]
    return ""
def limpiar_forro(texto, nombre_catalogo_min=""):
    if pd.isnull(texto):
        return texto
    texto = str(texto).replace('"', '').replace("'", "")
    if ',' in texto:
        texto = texto.split(',')[0]
    texto = texto.strip()

    # Convertir nombre_catalogo_min a minúsculas para consistencia
    nombre_catalogo_min = nombre_catalogo_min.lower()

    # Si el nombre del archivo contiene "botas" o "confort", solo se permite "PIEL"
    if "botas" in nombre_catalogo_min or "confort" in nombre_catalogo_min or "escolar" in nombre_catalogo_min or "caballeros" in nombre_catalogo_min:
        if texto.upper() == "PIEL":
            return "PIEL"
        else:
            return ""

    return texto
def limpiar_observacion_plantilla(observacion):
    # Si observacion es nula, retorna cadena vacía
    if observacion is None:
        return ""
    # Convertir a cadena en caso de que no lo sea
    observacion = str(observacion)
    # Verificar si "plantilla" está presente, ignorando mayúsculas/minúsculas y espacios extras
    if "plantilla" in observacion.strip().lower():
        return ""
    else:
        return observacion
def separar_composicion_custom(texto):
    # Verifica que sea string
    if not isinstance(texto, str):
        return texto

    # Limpieza previa: quitar comillas dobles y comas
    texto = texto.replace('"', '')
    texto = texto.replace(",", "")

    # 1. Insertar un espacio después de "%" si no existe.
    texto = re.sub(r'(%)(\S)', r'\1 \2', texto)
    # 2. Reemplazar "/" por espacio.
    texto = texto.replace("/", " ")

    # Dividir en tokens
    tokens = texto.split()
    bloques = []
    bloque_actual = []

    for token in tokens:
        # Cada token que contiene "%" inicia un nuevo bloque
        if "%" in token:
            if bloque_actual:
                bloques.append(" ".join(bloque_actual))
            bloque_actual = [token]
        else:
            bloque_actual.append(token)
    if bloque_actual:
        bloques.append(" ".join(bloque_actual))

    resultado = ", ".join(bloques)
    return resultado
def limpiar_archivo(file):
    try:
        df = pd.read_excel(file, engine="openpyxl", skiprows=4)
        # Mostrar columnas del archivo
        # st.write("Columnas en el archivo:", df.columns.tolist())

        # Verificar si la primera columna es un índice mal colocado
        if df.columns[0] == df.index.name or df.iloc[:, 0].is_monotonic_increasing:
            df.drop(df.columns[0], axis=1, inplace=True)

        df.columns = df.columns.str.replace("\n", "", regex=True)

        # Verificar si la columna "Articulo" o "ARTICULO" está presente
        if "Articulo" not in df.columns and "ARTICULO" not in df.columns:
            st.warning(f"La columna 'Articulo' no se encuentra en el archivo {file.name}.")
            return None

        # Renombrar "ARTICULO" a "Articulo" si es necesario
        if "ARTICULO" in df.columns:
            df.rename(columns={"ARTICULO": "Articulo"}, inplace=True)

        # Definir las palabras clave esperadas
        nombres_catalogos = ["confort","man", "urbano","sandalias", "botas", "importados", "man", "accesorios", "vestir casual", "mochilas", "escolar", "navidad"]

        # Eliminar espacios extras y normalizar el nombre del archivo
        nombre_catalogo_min = file.name.lower().strip()

        # Reemplazar múltiples espacios por uno solo (por si hay espacios dobles)
        nombre_catalogo_min = " ".join(nombre_catalogo_min.split())

        nombre_catalogo_min = file.name.lower()  # Convertir a minúsculas

        if "sandalias" in nombre_catalogo_min or "vestir casual" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Descripción",
                "Frase",
                "Diseño",
                "MARCA COMERCIAL",
                "Estilo Price",
                "Tallas reales",
                "Equivalencia",
                "Calzado = Suela Ropa = Composicion"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "RANGO DE TALLAS": "Tallas",
                "1/2#": "Enteros",
                "Tipo de Seguridad": "Suela",
                "Altura Tacón / Alt Sin Plataforma": "Altura",
            }
            ORDEN_COLUMNAS = [
                "ID",
                "V/N",
                "Pag Act",
                "Pag Ant",
                "Catalogo Anterior",
                "Marca Price",
                "Estilo Prov",
                "Color",
                "Tallas",  # "RANGO DE TALLAS",
                "Enteros",
                "Corte",
                "Suela",
                "Plantilla",
                "Forro",
                "Altura",
                "Observacion",
                "@imagen"
            ]

        elif "botas" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Frase",
                "Diseño",
                "MARCA COMERCIAL",
                "Estilo Price",
                "Tallas reales",
                "Equivalencia",
                "Atributo"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "Talla": "Tallas",
                "1/2#": "Enteros",
                "Altura Tacón / Alt Sin Plataforma": "Altura",
                "Marca Price": "Marca",
                "Estilo Prov": "Estilo",
                "Calzado = Suela Ropa = Composicion": "Suela"
            }
            ORDEN_COLUMNAS = [
                "ID",
                "V/N",
                "Pag Act",
                "Pag Ant",
                "Catalogo Anterior",
                "Descripción",
                "Marca",
                "Estilo",
                "Color",
                "Tallas",  # "RANGO DE TALLAS",
                "Enteros",
                "Corte",
                "Suela",
                "Forro",
                "Altura",
                "Observacion",
                "@imagen"
            ]

            # ✅ Aplicar la función para modificar la descripción
            if "Descripción" in df.columns:
                df["Descripción"] = df["Descripción"].apply(modificar_descripcion)

        elif "importados" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Pag Ant", "Catalogo Anterior", "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                "Tallas reales", "Equivalencia", "Corte", "Calzado = Suela Ropa = Composicion", "Forro",
                "Altura Tacón / Alt Sin Plataforma", "Comprador", "Sección", "Seccion", "Tipo de Seguridad", "Publico Objetivo",
                "Ubicación"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "Marca Price": "Marca",
                "Estilo Prov": "Estilo",
                "RANGO DE TALLAS": "Tallas",
                "1/2#": "Enteros",
                "Observacion": "Modelo"
            }
            ORDEN_COLUMNAS = ["@imagen", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N", "Pag Act"]

        elif "man" in nombre_catalogo_min:

            if "Articulo" in df.columns:
                df["ID"] = df["Articulo"]  # Asigna Articulo a ID

                df["@imagen"] = df["Articulo"].astype(str) + ".tif"  # Genera @imagen correctamente

            COLUMNAS_A_ELIMINAR = [

                "Articulo", "V/N", "Pag Ant", "Catalogo Anterior", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",

                "Tallas reales", "Equivalencia", "1/2#", "Corte", "Altura Tacón / Alt Sin Plataforma", "Observacion",

                "Comprador", "Seccion", "Categoria", "Tipo de Seguridad", "Publico Objetivo"

            ]

            MAPEADO_COLUMNAS = {

                "Pag Act": "Pag",

                "Estilo Prov": "Mod",

                "Marca Price": "Marca",

                "Descripción": "Rubro",  # SOLO SE ASIGNA UNA VEZ

                "Color": "Color",

                "RANGO DE TALLAS": "Tallas",

                "Calzado = Suela Ropa = Composicion": "Composicion",

                "Forro": "Forro",

                "Ubicación": "@Ubicación"

            }

            # Aplicar el mapeo de nombres de columnas

            df.rename(columns=MAPEADO_COLUMNAS, inplace=True)

            # Eliminar columnas innecesarias

            df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True)

            # Duplicar la columna "Rubro" en "Observacion 1"

            if "Rubro" in df.columns:
                df["Observacion 1"] = df["Rubro"]

            # Asegurar que COMPO y FORRO estén entre comillas si contienen comas

            if "Composicion" in df.columns:
                df["Composicion"] = df["Composicion"].apply(lambda x: f'"{x}"' if "," in str(x) else x)

            if "Forro" in df.columns:
                df["Forro"] = df["Forro"].apply(lambda x: f'"{x}"' if "," in str(x) else x)

            # Definir el orden de las columnas en la salida

            ORDEN_COLUMNAS = ["@imagen", "Pag", "ID", "Mod", "Marca", "Rubro", "Color", "Tallas", "Composicion", "Forro",

                              "@Ubicación", "Observacion 1", "Observacion 2"]

            # Asegurar que solo se mantengan las columnas deseadas y que existan en df

            df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        elif "accesorios" in nombre_catalogo_min:
            if "Articulo" in df.columns:
                df["ID"] = df["Articulo"]  # Asigna Articulo a ID

                # Genera @imagen correctamente como número entero sin decimales
                df["@imagen"] = df["Articulo"].astype(str).str.split('.').str[0] + ".tif"

            COLUMNAS_A_ELIMINAR = [
                "Articulo", "V/N", "Pag Ant", "Catalogo Anterior", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Prov", "RANGO DE TALLAS",
                "Tallas reales", "Equivalencia", "1/2#", "Corte", "Altura Tacón / Alt Sin Plataforma",
                "Comprador", "Seccion", "Categoria", "Tipo de Seguridad", "Publico Objetivo"
            ]

            MAPEADO_COLUMNAS = {
                "Pag Act": "Pag",
                "Estilo Price": "Mod",
                "Marca Price": "Marca",
                "Descripción": "Rubro",
                "Color": "Color",
                "Calzado = Suela Ropa = Composicion": "Composicion"
            }

            # Aplicar el mapeo de nombres de columnas
            df.rename(columns=MAPEADO_COLUMNAS, inplace=True)

            # Eliminar columnas innecesarias
            df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True)

            # Convertir ID a entero, manejando errores
            if "ID" in df.columns:
                df["ID"] = pd.to_numeric(df["ID"], errors="coerce").fillna(0).astype(int)

            # Convertir Pag a entero, manejando errores
            if "Pag" in df.columns:
                df["Pag"] = pd.to_numeric(df["Pag"], errors="coerce").fillna(0).astype(int)

            # Duplicar la columna "Rubro" en "Observacion" ANTES de ordenar
            if "Rubro" in df.columns:
                df["Observacion"] = df["Rubro"]

            # Asegurar que Composicion esté entre comillas si contiene comas
            if "Composicion" in df.columns:
                df["Composicion"] = df["Composicion"].apply(lambda x: f'"{x}"' if "," in str(x) else x)

            # Definir el orden de las columnas en la salida
            ORDEN_COLUMNAS = ["@imagen", "Pag", "ID", "Mod", "Marca", "Rubro", "Color", "Composicion", "Observacion"]

            # Asegurar que solo se mantengan las columnas deseadas y que existan en df
            df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        elif "urbano" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Pag Ant", "Catalogo Anterior", "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Prov",
                "Tallas reales", "Equivalencia", "Corte", "Calzado = Suela Ropa = Composicion", "Forro",
                "Altura Tacón / Alt Sin Plataforma", "Comprador", "Seccion", "Tipo de Seguridad", "Publico Objetivo",
                "Ubicación", "Calzado = Suela Ropa = Composicion"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "Marca Price": "Marca",
                "RANGO DE TALLAS": "Tallas",
                "Estilo Price": "Estilo Prov",
                "1/2#": "Enteros"
            }
            ORDEN_COLUMNAS = ["ID", "Pag Act", "Marca", "Estilo", "Color", "Tallas", "Enteros Prov", "@imagen", "Observacion"]

        elif "caballeros" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                "Tallas reales", "Equivalencia",
                "Altura Tacón / Alt Sin Plataforma", "Comprador", "Sección", "Calzado = Suela Ropa = Composicion", "Publico Objetivo",
                "Ubicación"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "Marca Price": "Marca",
                "RANGO DE TALLAS": "Tallas",
                "1/2#": "Enteros",
                "Estilo Prov": "Estilo",
                "Tipo de Seguridad": "Suela"
            }

            ORDEN_COLUMNAS = [
                    "ID",
                  "V/N",
                  "Pag Act",
                  "Pag Ant",
                  "Catalogo Anterior",
                  "Marca",
                  "Estilo",
                  "Color",
                  "Tallas",
                  "Enteros",
                  "Corte",
                  "Suela",
                  "Forro",
                  "Plantilla",
                  "Observacion",
                  "@imagen"
            ]

        elif "confort" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Descripción",
                "Frase",
                "Diseño",
                "MARCA COMERCIAL",
                "Estilo Price",
                "Tallas reales",
                "Equivalencia",
                "Comprador",
                "Sección",
                "Publico Objetivo",
                "Ubicación",
                "Calzado = Suela Ropa = Composicion"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "RANGO DE TALLAS": "Tallas",
                "Marca Price": "Marca",
                "Tipo de Seguridad": "Suela",
                "Estilo Prov": "Estilo",
                "Calzado = Suela Ropa = Composicion": "Forro",
                "1/2#": "Enteros",
                "Altura Tacón / Alt Sin Plataforma": "Altura"
            }

            ORDEN_COLUMNAS = [
                "ID",
                  "@imagen",
                  "V/N",
                  "Pag Act",
                  "Marca",
                   "Estilo",
                  "Color",
                  "Tallas",
                  "Enteros",
                  "Corte",
                  "Forro",
                  "Plantilla",
                  "Suela",
                  "Altura",
                  "Observacion"
            ]

        elif "escolar" in nombre_catalogo_min:

            COLUMNAS_A_ELIMINAR = [

                "Pag Ant",

                "Catalogo Anterior",

                "Descripción",

                "Frase",

                "Diseño",

                "MARCA COMERCIAL",

                "Estilo Price",

                "Tallas reales",

                "Equivalencia",

                "Calzado = Suela Ropa = Composicion",

                "Altura Tacón/Alt Sin Plataforma",

                "Comprador",

                "Publico Objetivo",

                "Ubicacion"

            ]

            MAPEADO_COLUMNAS = {

                "Articulo": "@imagen",

                "RANGO DE TALLAS": "Tallas",

                "1/2#": "Enteros",

                "Marca Price": "Marca",

                "Estilo Prov": "Estilo",

                "Tipo de Seguridad": "Suela"

            }

            ORDEN_COLUMNAS = [

                "ID",

                "V/N",

                "Pag Act",

                "Marca",

                "Estilo",

                "Color",

                "Tallas",  # "RANGO DE TALLAS",

                "Enteros",

                "Corte",

                "Suela",

                "Forro",

                "Plantilla",

                "Observacion",

                "@imagen"

            ]

        elif "mochilas" in nombre_catalogo_min:

            COLUMNAS_A_ELIMINAR = [
                "Pag Ant",
                "Catalogo Anterior",
                "Frase",
                "Diseño",
                "MARCA COMERCIAL",
                "Estilo Price",
                "RANGO DE TALLAS",
                "Equivalencia",
                "1/2#",
                "Corte",
                "Calzado = Suela Ropa = Composicion",
                "Forro",
                "Altura Tacón/Alt Sin Plataforma",
                "Observacion",
                "Comprador",
                "Seccion",
                "Categoria",
                "Tipo de Seguridad",
                "Publico Objetivo",
                "Ubicacion"
            ]

            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "Marca Price": "Marca",
                "Estilo Prov": "Estilo",
                "Tallas reales": "Tallas"
            }

            ORDEN_COLUMNAS = [
                "ID",
                "V/N",
                "Pag Act",
                "Descripción",
                "Marca",
                "Estilo",
                "Color",
                "Tallas"
            ]

        elif "navidad" in nombre_catalogo_min:
            COLUMNAS_A_ELIMINAR = [
                "Pag Ant",
                "Catalogo Anterior",
                "Frase",
                "Diseño",
                "MARCA COMERCIAL",
                "Estilo Price",
                "Tallas reales",
                "Equivalencia",
                "1/2#",
                "Corte",
                "Calzado = Suela Ropa = Composicion",
                "Forro",
                "Altura Tacón / Alt Sin Plataforma",
                "Observacion",
                "Comprador",
                "Seccion",
                "Categoria",
                "Tipo de Seguridad",
                "Publico Objetivo",
                "Ubicación"
            ]

            MAPEADO_COLUMNAS = {
                "Articulo": "@imagen",
                "Marca Price": "Marca",
                "Estilo Prov": "Estilo",
                "RANGO DE TALLAS": "Tallas"
            }

            ORDEN_COLUMNAS = [
                "ID",
                "V/N",
                "Pag Act",
                "Descripción",
                "Marca",
                "Estilo",
                "Color",
                "Tallas",
                "@imagen"
            ]

        else:
            st.warning(f"El archivo '{file.name}' no coincide con los tipos esperados {nombres_catalogos}.")
            st.write(f"Nombre del archivo procesado: {nombre_catalogo_min}")

            return None

        # Eliminar columnas innecesarias
        df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True, errors='ignore')

        if "Observacion" in df.columns:
            df["Observacion"] = df["Observacion"].fillna("")

        if "ID" not in df.columns:
            df.insert(1, "ID", pd.to_numeric(df["Articulo"], errors="coerce")
                      .replace([np.inf, -np.inf], 0)
                      .fillna(0)
                      .astype(int))

        for columna_actual, nueva_columna in MAPEADO_COLUMNAS.items():
            if columna_actual in df.columns:
                df.rename(columns={columna_actual: nueva_columna}, inplace=True)

        df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        if "@imagen" in df.columns:
            if ("importados" in nombre_catalogo_min or
                    "botas" in nombre_catalogo_min or
                    "urbano" in nombre_catalogo_min or
                    "confort" in nombre_catalogo_min or
                    "caballeros" in nombre_catalogo_min or
                    "escolar" in nombre_catalogo_min or
                    "navidad" in nombre_catalogo_min or
                    "sandalias" in nombre_catalogo_min):
                df["@imagen"] = pd.to_numeric(df["@imagen"], errors='coerce').fillna(0).astype(int).astype(str) + ".psd"

        if "Tallas" in df.columns:
            df["Tallas"] = df["Tallas"].astype(str).apply(ajustar_tallas)

        if "Enteros" in df.columns and "Tallas" in df.columns:
            df["Enteros"] = df.apply(lambda row: ajustar_enteros(row["Enteros"], row["Tallas"]), axis=1)

        if "Plantilla" in ORDEN_COLUMNAS:  # Verifica si 'Plantilla' se espera en el orden final
            # Crear la columna "Plantilla" si no existe
            if "Plantilla" not in df.columns:
                df["Plantilla"] = ""
            # Recorrer las columnas que pueden aportar valor a "Plantilla"
            for columna in ['Forro', 'Calzado = Suela Ropa = Composicion', 'Observacion']:
                if columna in df.columns:
                    # Aquí se sobreescribe la columna "Plantilla" en cada iteración.
                    # Si lo que deseas es combinar resultados, tal vez necesites concatenar o condicionar la asignación.
                    df["Plantilla"] = df[columna].apply(extraer_palabra_plantilla)

            df["Plantilla"] = df["Plantilla"].fillna("")

        # Procesar la columna "Forro"
        if "Forro" in df.columns:
            if "botas" in nombre_catalogo_min or "confort" in nombre_catalogo_min or "escolar" in nombre_catalogo_min or "caballeros" in nombre_catalogo_min:
                df["Forro"] = df["Forro"].apply(lambda x: limpiar_forro(x, nombre_catalogo_min))
            else:
                df["Forro"] = df["Forro"].apply(limpiar_forro)
        else:
            df["Forro"] = ""

        if "Observacion" in df.columns:
            df["Observacion"] = df["Observacion"].apply(limpiar_observacion_plantilla)

        if "Suela" in df.columns:
            df["Suela"] = df["Suela"].apply(modificar_suela)

        if "Altura" in df.columns:
            df["Altura"] = df["Altura"].apply(concatenar_altura)

        if "Color" in df.columns:
            df["Color"] = df["Color"].astype(str).apply(agregar_tildes_upper)


        df.replace("**", "", inplace=True)

        df.update(
            df.drop(columns=['@imagen', 'Altura'], errors='ignore')
            .applymap(lambda x: x.upper() if isinstance(x, str) else x)
        )

        if "Composicion" in df.columns:
            df["Composicion"] = (
                df["Composicion"]
                .astype(str)
                .apply(lambda x: "" if x.strip().lower() in ["nan", "nan."] else separar_composicion_custom(x))
            )

        if "Forro" in df.columns:
            df["Forro"] = (
                df["Forro"]
                .astype(str)
                .apply(lambda x: "" if x.strip().lower() in ["nan", "nan."]
                else separar_composicion_custom(limpiar_forro(x)))
            )

        df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]
        return df

    except Exception as e:
        st.error(f"Error al procesar el archivo {file.name}: {e}")
        return None

subir_archivos = st.file_uploader("Sube uno o más archivos Excel o CSV", type=["xlsx", "csv"], accept_multiple_files=True)

if subir_archivos:
    for file in subir_archivos:
        df_procesado = limpiar_archivo(file)
        if df_procesado is not None:
            st.write(f"Vista previa de: {file.name}")
            st.dataframe(df_procesado)
            file_name_base = os.path.splitext(file.name)[0]

            # Generar CSV
            csv = df_procesado.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"procesado_{file_name_base}.csv",
                mime="text/csv"
            )

            # Generar XLSX
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_procesado.to_excel(writer, index=False, sheet_name='Sheet1')
            xlsx_data = output.getvalue()
            st.download_button(
                label="📥 Descargar XLSX",
                data=xlsx_data,
                file_name=f"procesado_{file_name_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )