import pdf2txt
import ai_provider as ai_provider
import json
import re

from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

pdfFile = "pdf2questions/test2.pdf"


class QuizAnswer(BaseModel):
    answer: str = Field(description="Respuesta de pregunta")

class QuizQuestion(BaseModel):
    question: str = Field(description="Pregunta tipo test")
    correct: int = Field(description="El index de la respuesta correcta (0, 1, 2, etc.)")
    answers: List[QuizAnswer]

class Quiz(BaseModel):
    quiz_name: str = Field(description="El nombre del quiz")
    questions: List[QuizQuestion]



def loadQuiz():
    jsonquiz = ""
    with open('results/quiz_ttt.json', 'r') as file:
        jsonquiz = file.read()
    return Quiz.model_validate_json(jsonquiz)

def quizSaved():
    try:
        loadQuiz()
        return True
    except FileNotFoundError:
        return False

import re
import json

def clean_json_response(text: str) -> str:

    text = text.strip()
    match = re.search(r'```(?:json)?\s*([\[\{].*?[\]\}])\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    match_raw = re.search(r'([\[\{].*[\]\}])', text, re.DOTALL)
    if match_raw:
        return match_raw.group(1)
    return text

def generateQuiz(feedback = None, save = True):
    print("Generando quiz con modelo Text-to-Text puro...")
    
    schema_structure = json.dumps(Quiz.model_json_schema(), indent=2)

    if feedback and len(feedback) > 0:
        
        topics_str = ", ".join(feedback)
        instruction_scope = f"""
        ### ENFOQUE DEL QUIZ (PRIORIDAD ALTA)
        El alumno ha fallado anteriormente en los siguientes temas: [{topics_str}].
        Tu objetivo es REFORZAR estos conocimientos.
        Genera las preguntas EXCLUSIVAMENTE relacionadas con estos temas específicos.
        Ignora el resto del contenido del texto que no esté relacionado con estos fallos.
        """
    else:
        instruction_scope = """
        ### ENFOQUE DEL QUIZ
        Genera un examen general que cubra los puntos clave de todo el texto proporcionado de manera equilibrada.
        """


    prompt = f"""
    Actúa como un generador de datos API estricto y un diseñador instruccional experto.

    Tu tarea es crear un quiz educativo de alta calidad basado en el texto proporcionado al final.

    {instruction_scope}

    ### REGLAS DE DISEÑO DE PREGUNTAS
    1. **Cantidad:** Genera exactamente 10 preguntas.
    2. **Distractores Plausibles:** Las respuestas incorrectas deben ser verosímiles y gramaticalmente similares a la correcta. Evita opciones obvias o ridículas.
    3. **Aleatoriedad:** La respuesta correcta NO debe seguir un patrón (ej. no pongas siempre la primera opción). Distribuye el índice `correct` aleatoriamente.
    4. **Dificultad:** Las preguntas deben evaluar comprensión, no solo memorización literal.

    ### FORMATO DE SALIDA (ESTRICTO)
    1. La salida debe ser ÚNICAMENTE un objeto JSON válido.
    2. No incluyas texto conversacional, markdown (```json), ni explicaciones.
    3. El JSON debe cumplir estrictamente con el siguiente esquema:
    
    {schema_structure}
    
    --- CONTENIDO EDUCATIVO BASE ---
    """
    

    prompt += pdf2txt.getText(pdfFile)


    response = ai_provider.client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,

    )

    try:

        raw_text = response.text
        clean_text = clean_json_response(raw_text)

        quiz = Quiz.model_validate_json(clean_text)

        if save == True:
            with open('results/quiz_ttt.json', 'w') as file:
                file.write(clean_text) 
            
        return quiz

    except Exception as e:
        print(f"Error al procesar la respuesta del modelo: {e}")
        print(f"Respuesta cruda recibida: {response.text}")
        raise e
def generateFeedback(quiz: Quiz, responses: List[int]):
    # 1. FILTRADO DETERMINISTA EN PYTHON
    # Creamos una lista solo con los errores para enviarsela a la IA
    errores_para_analisis = []

    for i, question in enumerate(quiz.questions):

        if i >= len(responses):
            break
            
        user_idx = responses[i]
        
        if user_idx != question.correct:

            try:
                texto_respuesta_alumno = question.answers[user_idx].answer
            except IndexError:
                texto_respuesta_alumno = "Respuesta fuera de rango/Inválida"
                
            texto_respuesta_correcta = question.answers[question.correct].answer
            
            errores_para_analisis.append({
                "pregunta": question.question,
                "respuesta_elegida_erronea": texto_respuesta_alumno,
                "respuesta_correcta_real": texto_respuesta_correcta
            })

    if not errores_para_analisis:
        print("No errors -> No feedback")
        return []

    json_errores = json.dumps(errores_para_analisis, indent=2)

    prompt = f'''
    ### ROL
    Actúa como un tutor experto. Tu objetivo es ayudar a un estudiante a mejorar identificando qué temas debe estudiar basándote en sus ERRORES.

    ### TAREA
    Recibirás una lista de preguntas que el alumno ha FALLADO.
    Para cada error, analiza la pregunta y la confusión del alumno, y extrae el "Tema Clave" que necesita repasar.

    ### FORMATO DE SALIDA (ESTRICTO)
    - Debes devolver ÚNICAMENTE una lista JSON de strings (Array of Strings).
    - Cada string debe ser una frase breve y directa sobre el tema a estudiar (ej: "Ciclo de vida de los componentes en React", "Diferencia entre virus y bacteria").
    - NO uses bloques de código markdown.
    - NO incluyas introducciones.
    
    ### DATOS DE ENTRADA (ERRORES DEL ALUMNO)
    {json_errores}
    '''

    with open("results/feedbackprompt.txt", 'w') as file:
        file.write(prompt)

    print(f"Generando feedback sobre {len(errores_para_analisis)} errores...")
    

    response = ai_provider.client.models.generate_content(
        model="gemma-3-27b-it", # O gemini-3-flash-preview
        contents=prompt,
    )

    try:
        raw_text = response.text
        clean_text = clean_json_response(raw_text)
        items = json.loads(clean_text)
        

        if isinstance(items, list):
            return items
        else:
            print("No list returned. Packaging...")
            return [str(items)]

    except Exception as e:
        print(f"Error al procesar el feedback: {e}")
        print(f"Respuesta cruda: {response.text}")

        return []
    
def printQuiz(quiz: Quiz):
    print(f"QUIZ: '{quiz.quiz_name}'\n")
    for i, q in enumerate(quiz.questions):
        print(f"PREGUNTA {i+1}: {q.question}")
        correct = q.correct
        indexs = "abcdefghijklmnopqrstuvwxyz"
        for j, a in enumerate(q.answers): 
            idx = indexs[j]
            if j == correct:
                idx = idx.upper()
            print(f'[{idx}] - {a.answer}')
        print("\n\n")

def makeQuiz(quiz: Quiz):
    print(f"QUIZ: '{quiz.quiz_name}'\n")

    responses = []
    grade = 0

    for i, q in enumerate(quiz.questions):
        print(f"PREGUNTA {i+1}: {q.question}")
        correct = q.correct
        indexs = "abcdefghijklmnopqrstuvwxyz"
        for j, a in enumerate(q.answers): 
            idx = indexs[j]
            if j == correct:
                idx = idx.upper()
            print(f'[{idx}] - {a.answer}')

        answer = input(f'\nTu respuesta es: [{",".join(indexs[n] for n in range(len(q.answers)))}]: ')
        ansIdx = indexs.index(answer.strip().lower())
        responses.append(ansIdx)

        if ansIdx == correct:
            print("\nBien hecho! Has acertado")

            grade += float(100) / len(quiz.questions)
        else:
            print(f"\nVaya... La respuesta correcta era '{q.answers[correct].answer}'")

        print('\n\n')
    
    return responses, grade



quiz = None

if quizSaved():
    inp = input("Load saved quiz (Y/n): ")
    if len(inp) == 0 or inp.strip().lower() == 'y':
        quiz = loadQuiz()
    else:
        quiz = generateQuiz()
else:
    quiz = generateQuiz()

while True:
    #HACER EL QUIZ:
    responses, grade = makeQuiz(quiz)

    print(f"Has sacado un {grade} sobre 100")

    inp = input("Generar feedback (Y/n): ")
    if len(inp) == 0 or inp.strip().lower() == 'y':
        feedback = generateFeedback(quiz, responses)

        print(f"Tus temas a mejorar son {','.join(feedback)}.")
        print("Se tendra en cuenta en proximos quizes")
    else:
        break

    inp = input("Generar cuestionario de refuerzo? (Y/n): ") #esto sera decidido por el programa en un loop de estudio normal, en base a la nota que saques
    if len(inp) == 0 or inp.strip().lower() == 'y':
        quiz = generateQuiz(feedback, False)
    else:
        inp = input("Prefieres uno nuevo general, como ultimo repaso? (Y/n): ") #esto sera decidido por el programa en un loop de estudio normal, en base a la nota que saques
        if len(inp) == 0 or inp.strip().lower() == 'y':
            quiz = generateQuiz()
        else:
            break
                
