from google import genai

import os, sys


try:
    from dotenv import load_dotenv
    load_dotenv()
    client = genai.Client(api_key=os.getenv('GEMMA_API'))
except:
    p = ""
    """Obtiene la ruta del directorio donde reside el ejecutable o el script."""
    if getattr(sys, 'frozen', False):
        # Si es un ejecutable, sys.executable da la ruta del .exe
        p = os.path.dirname(sys.executable)
    else:
        # Si es un script .py, __file__ da la ruta del script
        p = os.path.dirname(os.path.abspath(__file__))

    key = ""
    with open(os.path.join(p, "key.txt")) as file:
        key = file.read()
    
    client = genai.Client(api_key=key)


def ask(text):
    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it", contents=text #gemini-2.5-flash
        )

        return response.text
    except Exception as e:
        print(e)
        return "ERROR"
    

if __name__ == "__main__":
    print(ask(input("Ask gemma: >>> ")))