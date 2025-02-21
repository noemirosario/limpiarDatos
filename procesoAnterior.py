
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
        return valor
    valor = str(valor).replace("-", "/")
    tallas = valor.split("/")

    # Verificar si el valor sigue el patrón de tallas de calzado
    if all(talla.replace(".", "").isdigit() for talla in tallas):
        tallas = [str(int(float(t))) if float(t).is_integer() else str(float(t)) for t in tallas]
        return "=" + "\"" + "-".join(tallas) + "\""

    lista_tallas = ["XXCH", "XCH", "CH", "M", "G", "XG", "XXG", "XXXG"]

    if tallas[0] in lista_tallas and tallas[-1] in lista_tallas:
        try:
            inicio = lista_tallas.index(tallas[0])
            fin = lista_tallas.index(tallas[-1])
            return ",".join(lista_tallas[inicio:fin+1])
        except ValueError:
            return valor

    return valor

# Función para ajustar la columna "Enteros"
def ajustar_enteros(valor_tallas, valor_enteros):
    if valor_enteros in ["Sí", "Si"]:
        return ""
    if valor_enteros == "No":
        if isinstance(valor_tallas, str) and "-" in valor_tallas:
            partes = valor_tallas.replace("=\"", "").replace("\"", "").split("-")
            if all(parte.isdigit() for parte in partes):
                return "solo enteros"
        return ""
    return valor_enteros

# Función para procesar el archivo
def limpiar_archivo(file):
    try:
        df = pd.read_excel(file, engine="openpyxl", skiprows=4)

        # Verificar si la primera columna es un índice mal colocado
        if df.columns[0] == df.index.name or df.iloc[:, 0].is_monotonic_increasing:
            df.drop(df.columns[0], axis=1, inplace=True)

        df.columns = df.columns.str.replace("\n", "", regex=True)

        file_name_lower = file.name.lower()  # Convertir el nombre del archivo a minúsculas

        # Definir variables según el tipo de archivo
        if "importados" in file_name_lower:
            COLUMNAS_A_ELIMINAR = [
                "Pag Ant", "Catalogo Anterior", "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                "Tallas reales", "Equivalencia", "Corte", "Calzado = Suela Ropa = Composicion", "Forro",
                "Altura Tacón / Alt Sin Plataforma", "Comprador", "Sección", "Seccion", "Tipo de Seguridad", "Publico Objetivo",
                "Ubicación", "Calzado = Suela Ropa = Composicion"
            ]
            MAPEADO_COLUMNAS = {
                "Articulo": "@foto",
                "Marca Price": "Marca",
                "Estilo Prov": "Estilo",
                "RANGO DE TALLAS": "Tallas",
                "1/2#": "Enteros",
                "Observacion": "Modelo"
            }
            ORDEN_COLUMNAS = ["@foto", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N", "Pag Act"]

        elif "man" in file_name_lower:
            if "Articulo" in df.columns:
                df["ID"] = df["Articulo"]  # Asigna Articulo a ID
                df["@foto"] = df["Articulo"].astype(str) + ".tif"  # Genera @foto correctamente

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

            # Formatear Tallas (Separar por ", " en lugar de "/")
            if "Tallas" in df.columns:
                df["Tallas"] = df["Tallas"].astype(str).str.replace("/", ", ")

            # Asegurar que COMPO y FORRO estén entre comillas si contienen comas
            if "Compo" in df.columns:
                df["Compo"] = df["Compo"].apply(lambda x: f'"{x}"' if "," in str(x) else x)
            if "Forro" in df.columns:
                df["Forro"] = df["Forro"].apply(lambda x: f'"{x}"' if "," in str(x) else x)

            # Definir el orden de las columnas en la salida
            ORDEN_COLUMNAS = ["@foto", "Pag", "ID", "Mod", "Marca", "Rubro", "Color", "Tallas", "Compo", "Forro",
                              "@Ubicación", "Observacion 1", "Observacion 2"]

            # Asegurar que solo se mantengan las columnas deseadas y que existan en df
            df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]



        elif "accesorios" in file_name_lower:
            if "Articulo" in df.columns:
                df["ID"] = df["Articulo"]  # Asigna Articulo a ID

                # Genera @foto correctamente como número entero sin decimales
                df["@foto"] = df["Articulo"].astype(str).str.split('.').str[0] + ".tif"

            COLUMNAS_A_ELIMINAR = [
                "Articulo", "V/N", "Pag Ant", "Catalogo Anterior", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
                "Tallas reales", "Equivalencia", "1/2#", "Corte", "Altura Tacón / Alt Sin Plataforma",
                "Comprador", "Seccion", "Categoria", "Tipo de Seguridad", "Publico Objetivo"
            ]

            MAPEADO_COLUMNAS = {
                "Pag Act": "Pag",
                "Estilo Prov": "Mod",
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
            ORDEN_COLUMNAS = ["@foto", "Pag", "ID", "Mod", "Marca", "Rubro", "Color", "Compo", "Observacion"]

            # Asegurar que solo se mantengan las columnas deseadas y que existan en df
            df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        else:
            st.warning(f"El archivo {file.name} no corresponde a los tipos esperados.")
            return None

        # ✅ Eliminar columnas innecesarias si existen en el DataFrame
        df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True, errors='ignore')

        # ✅ Insertar columna "ID" si no existe
        if "ID" not in df.columns:
            df.insert(1, "ID", df.iloc[:, 0])

        # ✅ Renombrar columnas según el mapeo
        for columna_actual, nueva_columna in MAPEADO_COLUMNAS.items():
            if columna_actual in df.columns:
                df.rename(columns={columna_actual: nueva_columna}, inplace=True)

        # ✅ Reordenar columnas asegurando que existan en el DataFrame
        df = df[[col for col in ORDEN_COLUMNAS if col in df.columns]]

        # ✅ Ajustar formato de la columna "@foto"
        if "@foto" in df.columns:
            if "importados" in file_name_lower:
                df["@foto"] = df["@foto"].astype(str) + ".psd"

        # ✅ Ajustar tallas y enteros si las columnas existen
        if "Tallas" in df.columns:
            df["Tallas"] = df["Tallas"].apply(ajustar_tallas)

        if "Enteros" in df.columns and "Tallas" in df.columns:
            df["Enteros"] = df.apply(lambda row: ajustar_enteros(row["Tallas"], row["Enteros"]), axis=1)

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
