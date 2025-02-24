if "importados" in file_name_lower:
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

elif "man" in file_name_lower:
    # Man
    COLUMNAS_A_ELIMINAR = [
        "Articulo",
        "V/N",
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
        "Altura Tacón / Alt Sin Plataforma",
        "Observacion",
        "Comprador",
        "Seccion",
        "Categoria",
        "Tipo de Seguridad",
        "Publico Objetivo"
    ]
    # Mapeo de nombres de columnas
    MAPEADO_COLUMNAS = {
        "Articulo": "@foto",
        "Pag Act": "PAG",
        "Estilo Prov": "MOD",
        "Marca Price": "MARCA",
        "Descripción": "RUBRO",
        "Color": "COLOR",
        "RANGO DE TALLAS": "TALLAS",
        "Calzado = Suela Ropa = Composicion": "COMPO",
        "Forro": "FORRO",
        "Ubicación": "@UBICACION",
        "Descripción": "OBSERVACION 1"
    }
    # Orden de columnas
    ORDEN_COLUMNAS = ["@foto", "PAG", "ID", "MOD", "MARCA", "RUBRO", "COLOR", "TALLAS", "COMPO", "FORRO", "@UBICACION",
                      "OBSERVACION 1"]

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
    ORDEN_COLUMNAS = ["@foto", "ID", "Categoria", "Marca", "Estilo", "Color", "Tallas", "Enteros", "Modelo", "V/N",
                      "Pag Act"]

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