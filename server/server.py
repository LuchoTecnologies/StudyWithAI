from flask import Flask, request
import iaTools.pdf2questions as ai
from iaTools.pdf2questions import Quiz

import time, random, json, sys, os

app = Flask("StudyWithAI backend")

testMode = False

def getDummyFile(name):
    with open(f'server/dummyResponses/{name}', 'r', encoding='utf-8') as file:
        return file.read()


@app.get("/ping")
def ping():
    return "Hello from StudyWithAI server!", 200

@app.route("/generalQuiz")
def generalQuiz():
    if testMode:
        time.sleep(random.randrange(2,4))
        return getDummyFile('quiz.json')
    
    quiz, json = ai.generateQuiz(None, False, app.config["PDF_PATH"] )
    if not quiz:
        return f"Error during quiz creation: {json}", 500
    return json, 200

@app.route("/feedback", methods=['POST'])
def getFeedback():
    jsonquiz = request.form['jsonq']
    answers = json.loads(request.form['answers']) #exaple content: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    quiz = Quiz.model_validate_json(jsonquiz)

    print(f"recived quiz json: {jsonquiz[:40]}\nStatus: {'Valid?' if quiz != None else 'Not valid'}\nResponse list: {answers}")

    if testMode:
        time.sleep(random.randrange(2,4))
        return getDummyFile('feedback.txt')

    feedback = ai.generateFeedback(quiz, answers)

    if not feedback or len(feedback) < 1:
        return "No feedback generated", 400

    jsonRet = json.dumps(feedback) #una lista de strings
    return jsonRet

@app.route("/customQuiz/<topic>")
def customQuiz(topic):
    if testMode:
        time.sleep(random.randrange(2,4))
        return getDummyFile('quiz.json')
    
    quiz, json = ai.generateQuiz(topic, False, app.config["PDF_PATH"] )
    if not quiz:
        return f"Error during quiz creation: {json}", 500
    return json, 200

def get_base_path():
    """Obtiene la ruta del directorio donde reside el ejecutable o el script."""
    if getattr(sys, 'frozen', False):
        # Si es un ejecutable, sys.executable da la ruta del .exe
        return os.path.dirname(sys.executable)
    else:
        # Si es un script .py, __file__ da la ruta del script
        return os.path.dirname(os.path.abspath(__file__))








if __name__ == '__main__':
    if not testMode:
        base_dir = get_base_path()
        folder_path = os.path.join(base_dir, 'apuntes')

        filenames = next(os.walk(folder_path), (None, None, []))[2]  # [] if no file

        pdfPath = ""

        if(len(filenames) > 1):
            print("Elige un archivo de apuntes: (solo pdf)")
            for i, name in enumerate(filenames):
                print(f"[{i + 1}] - {name}")
            while True:
                try:
                    inp = int(input(">>> "))
                    pdfPath = os.path.join(folder_path, filenames[inp - 1])
                    break
                except:
                    print("Error al parsear tu entrada...")
                    continue
        elif len(filenames) == 1:
            print(f"Usando '{filenames[0]}' como apuntes...")
            pdfPath = os.path.join(folder_path, filenames[0])
        else:
            print("No se han encontrado apuntes!")
            exit()

        app.config["PDF_PATH"] = pdfPath
 

    app.run('0.0.0.0', 9033)