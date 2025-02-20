import os
import pandas as pd
import streamlit as st
import io

# Configuración de la app
st.title("📂 Procesador de Archivos Excel a CSV")
st.write("Sube un archivo de Excel y procesa la información para generar un CSV limpio.")

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
ORDEN_COLUMNAS = ["@foto", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N",
                  "Pag Act"]


# Función para procesar el archivo
def limpiar_archivo(file):
    try:
        df = pd.read_excel(file, engine="openpyxl", skiprows=4)

        # Verificar si la primera columna es un índice mal colocado y eliminarla si es necesario
        if df.columns[0] == df.index.name or df.iloc[:, 0].is_monotonic_increasing:
            df.drop(df.columns[0], axis=1, inplace=True)

        # Limpiar nombres de columnas
        df.columns = df.columns.str.replace("\n", "", regex=True)

        # Eliminar columnas no necesarias
        df.drop(columns=[col for col in COLUMNAS_A_ELIMINAR if col in df.columns], inplace=True, errors='ignore')

        # Insertar ID en la segunda columna
        df.insert(1, "ID", df.iloc[:, 0])

        # Renombrar columnas según mapeo
        for columna_actual, nueva_columna in MAPEADO_COLUMNAS.items():
            if columna_actual in df.columns:
                df.rename(columns={columna_actual: nueva_columna}, inplace=True)

        # Asegurar el orden correcto de las columnas
        columnas_validas = [col for col in ORDEN_COLUMNAS if col in df.columns]
        df = df[columnas_validas + [col for col in df.columns if col not in columnas_validas]]

        # Agregar extensión .psd a la columna @foto
        if "@foto" in df.columns:
            df["@foto"] = df["@foto"].astype(str) + ".psd"

        # Procesar tallas
        if "Tallas" in df.columns:
            df["Tallas"] = df["Tallas"].astype(str).apply(formatear_tallas)

        return df
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return None


# Función para formatear tallas
def formatear_tallas(valor):
    if not isinstance(valor, str):
        return valor  # Si no es una cadena, devolver tal cual

    tallas = valor.split("-")  # Separar por guion en caso de corrida de tallas

    # Lista ordenada de tallas de ropa
    lista_tallas = ["XXCH", "XCH", "CH", "M", "G", "XG", "XXG", "XXXG"]

    # Si el valor parece ser una corrida de tallas de ropa
    if tallas[0] in lista_tallas and tallas[-1] in lista_tallas:
        try:
            inicio = lista_tallas.index(tallas[0])
            fin = lista_tallas.index(tallas[-1])
            return "-".join(lista_tallas[inicio:fin + 1])  # Unir en el orden correcto
        except ValueError:
            return valor  # Si hay un error, devolver original

    # Si es una corrida de tallas de calzado, eliminar ".0" de los números
    if all(talla.replace(".", "").isdigit() for talla in tallas):
        return "-".join(talla.replace(".0", "") for talla in tallas)

    return valor  # Si no coincide con ningún caso, devolver original


# Subir archivo
uploaded_file = st.file_uploader("Sube un archivo de Excel", type=["xlsx", "xls"])
if uploaded_file:
    df_procesado = limpiar_archivo(uploaded_file)
    if df_procesado is not None:
        st.write("📊 Vista previa de los datos procesados:")
        st.dataframe(df_procesado)

        # Generar CSV con separación por ";"
        csv = df_procesado.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name="archivo_procesado.csv",
            mime="text/csv"
        )

        # Generar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_procesado.to_excel(writer, index=False)
        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name="archivo_procesado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
