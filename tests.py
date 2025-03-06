import re

def separar_composicion_custom(texto):
    # Insertar espacio después de '%' si no existe y reemplazar '/' por espacio
    texto = re.sub(r'(%)(\S)', r'\1 \2', texto)
    texto = texto.replace("/", " ")

    tokens = texto.split()
    grupos = []
    grupo_actual = []

    for token in tokens:
        # Cada token que contiene '%' inicia un nuevo grupo
        if "%" in token:
            if grupo_actual:
                grupos.append(" ".join(grupo_actual))
            grupo_actual = [token]
        else:
            grupo_actual.append(token)
    if grupo_actual:
        grupos.append(" ".join(grupo_actual))

    return ", ".join(grupos)


def separar_subcomposicion(texto):
    """
    Procesa la parte de subcomposiciones después de "COPAS:".
    Por ejemplo:
      "EXTERIOR: 100% POLIESTER INTERIOR: 100% POLIURETANO"
    se transforma en:
      "EXTERIOR: 100% POLIESTER, INTERIOR: 100% POLIURETANO"
    La lógica es: cada token que termina en ":" inicia un nuevo grupo.
    """
    # Insertar espacio después de '%' si fuera necesario
    texto = re.sub(r'(%)(\S)', r'\1 \2', texto)
    texto = texto.replace("/", " ")

    tokens = texto.split()
    grupos = []
    grupo_actual = []

    for token in tokens:
        # Si el token termina en ":", se considera inicio de un nuevo grupo
        if token.endswith(":"):
            if grupo_actual:
                grupos.append(" ".join(grupo_actual))
            grupo_actual = [token]
        else:
            grupo_actual.append(token)
    if grupo_actual:
        grupos.append(" ".join(grupo_actual))

    return ", ".join(grupos)


def separar_composicion_complex(texto):
    if "COPAS:" in texto:
        partes = texto.split("COPAS:")
        base = partes[0].strip()
        sub = partes[1].strip()

        base_formateada = separar_composicion_custom(base)
        sub_formateada = separar_subcomposicion(sub)
        # Reconstruir la cadena, manteniendo "COPAS:" en mayúsculas
        return f"{base_formateada}, COPAS: {sub_formateada}."
    else:
        # Si no hay subcomposiciones, solo procesar la parte base
        return separar_composicion_custom(texto) + "."

# Ejemplo de uso:
print(separar_composicion_custom("61%VISCOSA/39%POLIESTER"))
print(separar_composicion_custom("84% POLIAMIDA 16% ELASTANO"))
print(separar_composicion_custom("Poliéster"))
print(separar_composicion_complex(("88% POLIAMIDA 12% ELASTANO COPAS: EXTERIOR: 100% POLIESTER INTERIOR: 100% POLIURETANO")))
# salida esperada: 88% Poliamida, 12% Elastano. Copas: Exterior: 100% Poliéster. Interior: 100% Poliuretano.
print(separar_composicion_custom("56%MODAL/38%ALGODON/6%ELASTANO"))


