import os
import pandas as pd
import streamlit as st
import io


# Configuración de la app
st.title("📂 ETL de Dummys de Artículos para su integración hacia InDesign")
st.write("Sube un archivo de Excel y procesa la información para generar un CSV limpio.")

folder_selected = st.text_input("Ingrese la ruta de la carpeta que contiene los archivos Excel:")


# Columnas a eliminar
COLUMNAS_A_ELIMINAR = [
    "Pag Ant", "Catalogo Anterior", "Descripción", "Frase", "Diseño", "MARCA COMERCIAL", "Estilo Price",
    "Tallas reales", "Equivalencia", "Corte", "Calzado = Suela Ropa = Composicion", "Forro",
    "Altura Tacón / Alt Sin Plataforma", "Comprador", "Sección", "Seccion", "Tipo de Seguridad", "Publico Objetivo",
    "Ubicación", "Calzado = Suela Ropa = Composicion"
]
# Mapeo de nombres de columnas
MAPEADO_COLUMNAS = {
    "Articulo": "@foto",
    "Marca Price": "Marca",
    "Estilo Prov": "Estilo",
    "RANGO DE TALLAS": "Tallas",
    "1/2#": "Enteros",
    "Observacion": "Modelo"
}
# Orden de columnas
ORDEN_COLUMNAS = ["@foto", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N", "Pag Act"]

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
            return "/".join(lista_tallas[inicio:fin+1])
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

        df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True, errors='ignore')

        df.insert(1, "ID", df.iloc[:, 0])

        for columna_actual, nueva_columna in MAPEADO_COLUMNAS.items():
            if columna_actual in df.columns:
                df.rename(columns={columna_actual: nueva_columna}, inplace=True)

        columnas_validas = [col for col in ORDEN_COLUMNAS if col in df.columns]
        df = df[columnas_validas + [col for col in df.columns if col not in columnas_validas]]

        if "@foto" in df.columns:
            df["@foto"] = df["@foto"].astype(str) + ".psd"

        if "Tallas" in df.columns:
            df["Tallas"] = df["Tallas"].apply(ajustar_tallas)

        if "Enteros" in df.columns and "Tallas" in df.columns:
            df["Enteros"] = df.apply(lambda row: ajustar_enteros(row["Tallas"], row["Enteros"]), axis=1)

        return df
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return None


if folder_selected:
    if os.path.isdir(folder_selected):
        archivos_excel = [f for f in os.listdir(folder_selected) if f.endswith((".xlsx", ".xls"))]

        if archivos_excel:
            st.write(f"Archivos encontrados: {archivos_excel}")

            for archivo in archivos_excel:
                ruta_completa = os.path.join(folder_selected, archivo)
                df_procesado = limpiar_archivo(ruta_completa)

                if df_procesado is not None:
                    st.write(f"📊 Vista previa de {archivo}:")
                    st.dataframe(df_procesado)

                    # Generar CSV con codificación UTF-8 con BOM
                    csv_buffer = io.StringIO()
                    df_procesado.to_csv(csv_buffer, index=False, encoding="utf-8-sig", sep=",", quotechar='"')
                    csv_data = "\ufeff" + csv_buffer.getvalue()
                    csv_buffer.close()

                    st.download_button(
                        label=f"📥 Descargar CSV de {archivo}",
                        data=csv_data,
                        file_name=f"{archivo.replace('.xlsx', '.csv').replace('.xls', '.csv')}",
                        mime="text/csv"
                    )



                    st.download_button(
                        label=f"📥 Descargar Excel de {archivo}",
                        data=excel_output,
                        file_name=f"{archivo.replace('.xlsx', '_procesado.xlsx').replace('.xls', '_procesado.xlsx')}",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.warning("No se encontraron archivos Excel en la carpeta seleccionada.")
    else:
        st.error("La ruta ingresada no es válida. Verifique e intente nuevamente.")