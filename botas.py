if "botas" in file_name_lower:
    COLUMNAS_A_ELIMINAR = [
        "V/N","Pag Act","Pag Ant","Catalogo Anterior","Descripción","Frase",
        "Proveedor","Marca Price","Estilo Price","Estilo Prov","Color","Talla",
        "Tallas reales","Equivalencia","Corrida","1/2#","Corte",
        "Calzado = Suela Ropa = Composicion","Forro","Altura Tacón / Alt Sin Plataforma",
        "Observacion","Comprador","Seccion","Categoria","Atributo","Tipo de Seguridad","Publico Objetivo","Ubicación"

    ]


    MAPEADO_COLUMNAS = {
        "Articulo": "@foto",
        "Marca Price": "Marca",
        "Estilo Prov": "Estilo",
        "RANGO DE TALLAS": "Tallas",
        "1/2#": "Enteros",
        "Observacion": "Modelo"
    }
    ORDEN_COLUMNAS = ["@foto", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N",
                      "Pag Act"]



    #sandalias
    elif "sandalias" in file_name_lower:
    COLUMNAS_A_ELIMINAR = [
        "Descripción",
        "Frase",
        "Diseño",
        "MARCA COMERCIAL",
        "Estilo Price",
        "Tallas reales",
        "Equivalencia",
        "Comprador",
        "Seccion",
        "Categoria",
        "Tipo de Seguridad",
        "Publico Objetivo",
        "Ubicación"
    ]
    MAPEADO_COLUMNAS = {
        "Articulo": "@foto",
        "RANGO DE TALLAS": "Tallas",
        "Tipo de Seguridad": "Suela",
        "Calzado = Suela Ropa = Composicion": "Forro",
        "1/2#": "Enteros"
    }

    ORDEN_COLUMNAS = ["ID",
                      "V/N",
                      "Pag Act",
                      "Pag Ant",
                      "Catalogo Anterior",
                      "Marca Price",
                      "Estilo Prov",
                      "Color",
                      "RANGO DE TALLAS",
                      "Enteros",
                      "Corte",
                      "Suela",
                      "Plantilla",
                      "Forro",
                      "Altura Tacón / Alt Sin Plataforma",
                      "Observacion",
                      "@foto"
                      ]

    # Crear el archivo Excel en memoria
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df_procesado.to_excel(writer, index=False, sheet_name="Hoja1")
    excel_file.seek(0)  # Volver al inicio del archivo

    # Botón para descargar el archivo Excel
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_file,
        file_name=f"procesado_{file_name_base}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )