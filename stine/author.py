def execute(code, ctx=None, args=None):
    """
    Procesa múltiples $author[Texto;Indice opcional] y devuelve una lista de tuplas con los textos y sus índices.
    """
    print(f"Procesando código: {code}")  # Debug
    authors = []
    start = 0

    while True:
        start_idx = code.find("$author[", start)
        if start_idx == -1:
            break

        if start_idx > 0 and code[start_idx - 1].isalnum():
            raise ValueError(f"❌ Formato inválido cerca de '{code[start_idx-1:start_idx+10]}...' (Se esperaba '$author[...]')")

        end_idx = code.find("]", start_idx)
        if end_idx == -1:
            raise ValueError("❌ '$author[' no está cerrado con ']'")

        content = code[start_idx + len("$author["):end_idx]
        parts = content.split(";")
        text = parts[0].strip()
        index = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 1

        if not text:
            raise ValueError("❌ '$author[]' debe contener un texto.")

        authors.append((text, index))  # Agrega el texto con su índice
        start = end_idx + 1  # Continuar la búsqueda después del último cierre de ']'

    print(f"Autores procesados: {authors}")  # Debug
    return authors
