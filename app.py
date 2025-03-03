import os
import pandas as pd
import streamlit as st
import io

# Configuración de la app
st.title("📂 ETL de Dummys de Artículos para su integración hacia InDesign")
st.write("Sube un archivo de Excel y procesa la información para generar un CSV limpio.")

# Función para formatear tallas
def ajustar_tallas(valor):
    if pd.isnull(valor):
        return ""
    valor = str(valor).replace("-", "/")
    tallas = valor.split("/")

    # Verificar si el valor sigue el patrón de tallas de calzado
    if all(talla.replace(".", "").isdigit() for talla in tallas):
        tallas = sorted(set(float(t) for t in tallas))  # Convertir a float, eliminar duplicados y ordenar
        tallas = [str(int(t)) if t.is_integer() else str(t) for t in tallas]  # Convertir enteros a str sin decimales
        return f'="{tallas[0]}-{tallas[-1]}"' if len(tallas) > 1 else f'="{tallas[0]}"'

    lista_tallas = ["XXCH", "XCH", "CH", "M", "G", "XG", "XXG", "XXXG"]

    if tallas[0] in lista_tallas and tallas[-1] in lista_tallas:
        try:
            inicio = lista_tallas.index(tallas[0])
            fin = lista_tallas.index(tallas[-1])
            return "/".join(lista_tallas[inicio:fin+1])
        except ValueError:
            return valor

    return valor
# Función para ajustar la columna Enteros
def ajustar_enteros(valor_enteros):
    # Si la columna "1/2#" contiene "Sí" o "Si", retorna ""
    if valor_enteros in ["Sí", "Si"]:
        return ""
    # Si la columna "1/2#" contiene "No", retorna "solo enteros"
    if valor_enteros == "No":
        return "solo enteros"
    return valor_enteros



#Modificar descripcion del catalogo de botas
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
    palabras = texto.split()  # Dividimos el texto en palabras
    if 'PLANTILLA' in palabras and len(palabras) >= 3:  # Verificamos que hay al menos 3 palabras
        return palabras[2]  # Devolvemos la palabra que sigue a "Plantilla"
    return None  # Si no se encuentra "Plantilla" o no hay suficientes palabras, devolvemos None
def limpiar_forro(texto):
    if pd.isnull(texto):
        return texto
    texto = str(texto).replace('"', '').replace("'", "")

    # Si el texto contiene una coma, quedarnos solo con lo que está antes de la coma
    if ',' in texto:
        texto = texto.split(',')[0]  # Tomar solo la primera parte antes de la coma

    return texto.strip()  # Eliminar espacios extra al principio y al final

def limpiar_observacion_plantilla(observacion):
    # Comprobamos si "Plantilla" está presente en el texto, sin importar mayúsculas/minúsculas
    if isinstance(observacion, float):
        observacion = str(observacion)
    if "plantilla" in observacion.strip().lower():
        return ""  # Si contiene la palabra "Plantilla", retornamos una cadena vacía
    else:
        return observacion  # Si no contiene "Plantilla", retornamos el valor original

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
        palabras_clave = ["confort","man", "urbano","sandalias", "botas", "importados", "man", "accesorios"]

        # Eliminar espacios extras y normalizar el nombre del archivo
        file_name_lower = file.name.lower().strip()

        # Reemplazar múltiples espacios por uno solo (por si hay espacios dobles)
        file_name_lower = " ".join(file_name_lower.split())

        file_name_lower = file.name.lower()  # Convertir a minúsculas

        if "sandalias" in file_name_lower:
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

        elif "botas" in file_name_lower:
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

        elif "importados" in file_name_lower:
            COLUMNAS_A_ELIMINAR = [
                "Pag Ant", "Catalogo Anterior", "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                "Tallas reales", "Equivalencia", "Corte", "Calzado = Suela Ropa = Composicion", "Forro",
                "Altura Tacón / Alt Sin Plataforma", "Comprador", "Sección", "Seccion", "Tipo de Seguridad", "Publico Objetivo",
                "Ubicación", "Calzado = Suela Ropa = Composicion"
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

        elif "man" in file_name_lower:
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
                "Calzado = Suela Ropa = Composicion": "Compo",
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
            if "Compo" in df.columns:
                df["Compo"] = df["Compo"].apply(lambda x: f'"{x}"' if "," in str(x) else x)
            if "Forro" in df.columns:
                df["Forro"] = df["Forro"].apply(lambda x: f'"{x}"' if "," in str(x) else x)

            # Definir el orden de las columnas en la salida
            ORDEN_COLUMNAS = ["@imagen", "Pag", "ID", "Mod", "Marca", "Rubro", "Color", "Tallas", "Compo", "Forro",
                              "@Ubicación", "Observacion 1", "Observacion 2"]

            # Asegurar que solo se mantengan las columnas deseadas y que existan en df
            df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        elif "accesorios" in file_name_lower:
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
                "Calzado = Suela Ropa = Composicion": "Compo"
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

            # Asegurar que COMPO esté entre comillas si contiene comas
            if "Compo" in df.columns:
                df["Compo"] = df["Compo"].apply(lambda x: f'"{x}"' if "," in str(x) else x)

            # Definir el orden de las columnas en la salida
            ORDEN_COLUMNAS = ["@imagen", "Pag", "ID", "Mod", "Marca", "Rubro", "Color", "Compo", "Observacion"]

            # Asegurar que solo se mantengan las columnas deseadas y que existan en df
            df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        elif "urbano" in file_name_lower:
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
                "Estilo Price": "Estilo",
                "1/2#": "Enteros"
            }
            ORDEN_COLUMNAS = ["ID", "Pag Act", "Marca", "Estilo", "Color", "Tallas", "Enteros", "@imagen", "Observacion"]

        elif "caballeros" in file_name_lower:
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

        elif "confort" in file_name_lower:
            COLUMNAS_A_ELIMINAR = [
                "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                "Tallas reales", "Equivalencia",
                "Comprador", "Sección", "Publico Objetivo",
                "Ubicación", "Calzado = Suela Ropa = Composicion",

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

            ORDEN_COLUMNAS = ["ID", "@imagen", "V/N", "Pag Act","Marca",
                               "Estilo", "Color", "Tallas", "Enteros", "Corte", "Forro","Plantilla",
                              "Suela", "Altura","Observacion"]

        elif "sandalias" in file_name_lower:
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
                "Marca Price": "Marca",
                "Estilo Prov": "Estilo",
                "Tipo de Seguridad": "Suela",
                "Altura Tacón / Alt Sin Plataforma": "Altura"
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

        else:
            st.warning(f"El archivo '{file.name}' no coincide con los tipos esperados {palabras_clave}.")
            st.write(f"Nombre del archivo procesado: {file_name_lower}")

            return None

        # Eliminar columnas innecesarias
        df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True, errors='ignore')

        # Reemplazar NaN en la columna Observacion con una cadena vacía
        if "Observacion" in df.columns:
            df["Observacion"] = df["Observacion"].fillna("")


        # Insertar columna "ID" si no existe
        if "ID" not in df.columns:
            df.insert(1, "ID", df["Articulo"])

        # Renombrar columnas según el mapeo
        for columna_actual, nueva_columna in MAPEADO_COLUMNAS.items():
            if columna_actual in df.columns:
                df.rename(columns={columna_actual: nueva_columna}, inplace=True)

        # Reordenar columnas asegurando que existan en el DataFrame
        df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        # Ajustar formato de la columna "@imagen"
        if "@imagen" in df.columns:
            if ("importados" in file_name_lower or
                    "botas" in file_name_lower or
                    "urbano" in file_name_lower or
                    "confort" in file_name_lower or
                    "caballeros" in file_name_lower or
                    "sandalias" in file_name_lower):
                df["@imagen"] = df["@imagen"].astype(str) + ".psd"

        # Ajustar tallas y enteros si las columnas existen
        if "Enteros" in df.columns:
            if "Tallas" in df.columns and df["Tallas"].astype(str).str.contains("-").any():
                df["Enteros"] = df["Enteros"].astype(str).apply(ajustar_enteros)
            else:
                return ""

        if "Tallas" in df.columns:
            df["Tallas"] = df["Tallas"].astype(str).apply(ajustar_tallas)
            #df["Tallas"] = df["Tallas"].astype(str).str.replace('="', '', regex=False).str.replace('"', '', regex=False)
            #df["Tallas"] = df["Tallas"].apply(lambda x: "-".join(
            #   [str(int(float(t))) if t.replace(".0", "").isdigit() else t for t in x.split("-")]
            #))

        # Asegurar que "Plantilla" esté en el DataFrame aunque no exista en los datos originales
        if "Plantilla" in df.columns:
            df["Plantilla"] = ""

        # Verificar si la columna "Plantilla" está presente
        if "Plantilla" in df.columns:
            # Buscar la palabra clave en las columnas "Calzado", "Ropa" y "Observacion" para extraer la plantilla
            for columna in ['Forro', 'Calzado = Suela Ropa = Composicion', 'Observacion']:
                if columna in df.columns:
                    df['Plantilla'] = df[columna].apply(extraer_palabra_plantilla)

        if "Forro" in df.columns:
            df["Forro"] = df["Forro"].apply(limpiar_forro)

        if "Observacion" in df.columns:
            df["Observacion"] = df["Observacion"].apply(limpiar_observacion_plantilla)

        if "Suela" in df.columns:
            df["Suela"] = df["Suela"].apply(modificar_suela)

        if "Altura" in df.columns:
            df["Altura"] = df["Altura"].apply(concatenar_altura)

        df.replace("**", "", inplace=True)

        df.update(df.drop(columns=['@imagen'], errors='ignore').applymap(lambda x: x.upper() if isinstance(x, str) else x))

        # Reordenar nuevamente para incluir "Plantilla" en la posición correcta
        df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        return df

    except Exception as e:
        st.error(f"Error al procesar el archivo {file.name}: {e}")
        return None

# Subir archivos Excel
uploaded_files = st.file_uploader("Sube uno o más archivos Excel", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        df_procesado = limpiar_archivo(file)
        if df_procesado is not None:
            st.write(f"Vista previa de: {file.name}")
            st.dataframe(df_procesado)

            # Descargar CSV
            file_name_base = os.path.splitext(file.name)[0]
            csv = df_procesado.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"procesado_{file_name_base}.csv",
                mime="text/csv"
            )




