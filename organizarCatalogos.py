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
