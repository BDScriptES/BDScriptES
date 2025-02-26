def execute(code, ctx=None, args=None):
    """
    Extrae y retorna todo el texto fuera de funciones.
    """
    texto_sin_funciones = ""
    start = 0

    while start < len(code):
        start_idx = code.find("$", start)
        if start_idx == -1:
            texto_sin_funciones += code[start:].strip()
            break

        texto_sin_funciones += code[start:start_idx].strip() + " "
        end_idx = code.find("]", start_idx)
        if end_idx == -1:
            break  # Si no hay cierre de función, salimos.

        start = end_idx + 1

    return texto_sin_funciones.strip() if texto_sin_funciones.strip() else None
