from pypdf import PdfReader

def getText(filename):
    reader = PdfReader(filename)

    texto_completo = ""
    for page in reader.pages:
        texto_completo += page.extract_text() + "\n"

    return texto_completo