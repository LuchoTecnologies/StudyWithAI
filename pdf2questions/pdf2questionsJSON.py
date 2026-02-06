import pdf2txt
import ai_provider as ai_provider

from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

import json

pdfFile = "pdf2questions/test.pdf"

class QuizAnswer(BaseModel):
    answer: str = Field(description="Respuesta de pregunta")
class QuizQuestion(BaseModel):
    question: str = Field(description="Pregunta tipo test")
    correct: int = Field(description="El index de la respuesta correcta")
    answers: List[QuizAnswer]

class Quiz(BaseModel):
    quiz_name: str = Field(description="El nombre del quiz")
    questions: List[QuizQuestion]


def loadQuiz():
    jsonquiz = ""
    with open('quiz.json', 'r') as file:
        jsonquiz = file.read()
    return Quiz.model_validate_json(jsonquiz)

def quizSaved():
    try:
        loadQuiz()
        return True
    except FileNotFoundError:
        return False

def generateQuiz():
    prompt = """
    Crea un quiz para evaluar el nivel de conocimiento del alumno sobre los siguientes contenidos:


    """
    prompt += pdf2txt.getText(pdfFile)

    response = ai_provider.client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Quiz.model_json_schema(),
        },
    )

    quiz = Quiz.model_validate_json(response.text)

    with open('quiz.json', 'w') as file:
        file.write(response.text)
    return quiz


def printQuiz(quiz: Quiz):
    print(f"QUIZ: '{quiz.quiz_name}'\n")
    for i, q in enumerate(quiz.questions):
        print(f"PREGUNTA {i}: {q.question}")
        correct = q.correct
        indexs = "abcdefghijklmnopqrstuvwxyz"
        for i, a in enumerate(q.answers):
            idx = indexs[i]
            if i == correct:
                idx = idx.upper()
            print(f'[{idx}] - {a.answer}')
        print("\n\n")



quiz = None

if quizSaved():
    inp = input("Load saved quiz (Y/n): ")
    if len(inp) == 0 or inp.strip().lower() == 'y':
        quiz = loadQuiz()
    else:
        quiz = generateQuiz()
else:
    quiz = generateQuiz()

printQuiz(quiz)