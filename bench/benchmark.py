import apifreellm
import gemmagoogle
import openrouter

import pandas as pd
import statistics

import random, time

providers = {
    "apifreellm": apifreellm.ask,
    "gemmagoogle": gemmagoogle.ask,
    "openrouter": openrouter.ask
}

preguntas = [
    "Explica con tus propias palabras qué es la inteligencia artificial.",
    "¿Por qué el cielo es azul?",
    "Resume la Segunda Guerra Mundial en cinco frases.",
    "¿Qué pesa más, un kilo de hierro o un kilo de plumas? Explica tu razonamiento.",
    "Si tengo 3 manzanas y regalo 2, ¿cuántas me quedan?",
    "Inventa un final alternativo para Caperucita Roja.",
    "Escribe un haiku sobre la programación.",
    "¿Qué es una función recursiva? Da un ejemplo sencillo.",
    "Traduce la frase 'El conocimiento es poder' al inglés.",
    "Ordena estos números de menor a mayor: 42, 7, 19, 3, 25.",
    "¿Puede un pingüino vivir en el desierto? Justifica tu respuesta.",
    "Explica la diferencia entre una lista y un diccionario en Python.",
    "Si hoy es lunes, ¿qué día será dentro de 100 días?",
    "Define la palabra 'empatía' como si se lo explicaras a un niño de 8 años.",
    "¿Qué harías si fueras presidente durante un día?",
    "Detecta el error en este código: for i in range(10) print(i)",
    "¿Qué significa que un modelo tenga sesgo?",
    "Escribe un chiste sobre robots.",
    "Convierte 150 grados Celsius a Fahrenheit.",
    "¿Qué es más importante, la libertad o la seguridad? Argumenta tu respuesta.",
    "Genera una contraseña segura de 12 caracteres.",
    "Explica un concepto difícil usando una metáfora sencilla.",
    "¿Cómo funciona un motor de combustión interna?",
    "Si un tren sale a las 10:00 y tarda 2h 35min, ¿a qué hora llega?",
    "¿Qué diferencia hay entre aprendizaje supervisado y no supervisado?",
    "Escribe un pseudocódigo para buscar un número en una lista.",
    "¿Qué es un agujero negro?",
    "Imagina una sociedad sin dinero. ¿Cómo funcionaría?",
    "Clasifica estas palabras en sustantivo, verbo o adjetivo: correr, azul, mesa.",
    "¿Puede una máquina ser creativa? Explica tu punto de vista."
]


TEST_MODE = False

def bench(iterations = 10):
    retData = {}
    timesElapsed = []
    requestsDone = 0
    for providerName in providers:
        benchData = []
        for i in range(iterations):
            if TEST_MODE:
                benchData.append(("TESTMODE", random.random() * 10))
            else:
                print(f"[{providerName}] - Making question {i + 1} out of {iterations}")
                start = time.monotonic()

                resp = providers[providerName](preguntas[i%len(preguntas)])
                if resp == "ERROR":
                    print(f"[{providerName}] Request failed!")
                elapsed = time.monotonic() - start
                benchData.append((resp, elapsed))

                timesElapsed.append(elapsed)
                requestsDone += 1

                time.sleep(5)

                estimatedTime = ((iterations * len(providers)) - requestsDone) * (statistics.mean(timesElapsed) + 5)

                minutos = int(estimatedTime // 60)
                segundos = estimatedTime % 60


                print(f"Tiempo restante aproximado: {minutos:02d} Minutos y {segundos:05.2f} Segundos")
        retData[providerName] = benchData
    return retData

if __name__ == "__main__":
    benchdata = bench()

    data = {}

    for item in benchdata:
        print(item)
        print(benchdata[item])
        data[f"{item}Time"] = [t for _, t in benchdata[item]]
        data[f"{item}Answer"] = [a for a, _ in benchdata[item]]
    
    data["Questions"] = preguntas[:10]
    
    df = pd.DataFrame(data)

    filename = "benchResult.csv"
    if TEST_MODE:
        filename = "benchResultTest.csv"
    df.to_csv(filename, index=True, decimal=",",float_format="%.2f")

    print(df)