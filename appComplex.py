import re

def separar_composicion_custom(texto):
    # Verifica que sea string
    if not isinstance(texto, str):
        return texto

    # Define un patrón que solo permita cadenas del tipo:
    # "60% ALGODON" o "60% ALGODON 40% POLIESTER" etc.
    patron = r'^\d+%\s*\w+(?:\s+\d+%\s*\w+)*$'

    # Si el texto no coincide con el patrón, se retorna sin modificar
    if not re.match(patron, texto.strip()):
        return texto

    # Limpieza previa: quitar comillas dobles y comas
    texto = texto.replace('"', '')
    texto = texto.replace(",", "")

    # Insertar un espacio después de "%" si no existe.
    texto = re.sub(r'(%)(\S)', r'\1 \2', texto)
    # Reemplazar "/" por espacio.
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


# Ejemplo de uso:
texto1 = "60%ALGODON 40%POLIESTER"
texto2 = "Texto no formateable"
print(separar_composicion_custom(texto1))  # "60% ALGODON, 40% POLIESTER"
print(separar_composicion_custom(texto2))  # "Texto no formateable"
