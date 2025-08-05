import requests
import json

def process_message(db, msg):
    OLLAMA_URL = "http://ollama:11434/api/generate"
    MODEL_NAME = "qwen3:1.7b"

    classification_prompt = f"""
    Analyze the following message and determine if it's an apartment/room rental announcement.
    Respond only with "YES" if it's clearly an apartment/room rental announcement and "NO" otherwise. 
    Respond with "NO" if it is an announcement for people LOOKING for apartments.
    If it's a strange message that doesn't fall into any category clearly or doesn't contain key information (especially PRICE), then respond with MALFORMED and explain why.

    Example 1:
    Stanza doppia o singola uso doppio via Matteotti - per studentesse universitarie. 
    A TRENTO - Via Matteotti - in luminoso e bell’appartamento al V piano con ascensore affitto un  stanza doppia (2 posti letto) solo a ragazze. Si può prendere anche come singola uso doppio. L’appartamento è composto da 2 stanze, bagno con lavatrice, nuova cucina abitabile, ingresso, terrazzino, internet Wi-Fi con fibra FTTH. Ottima posizione centrale, zona ben servita, 10 minuti a piedi dall'università, fermata dell’autobus comoda per Povo e Mesiano.
    Costo posto letto 260 € al mese spese comprese eccetto piccola bolletta luce ( circa 15 € al mese). Se si prende come singola uso doppio 480€ + bolletta luce. 
    Solo per studentesse universitarie, contratto transitorio per studenti di 12 mesi. Disponibile da settembre.
    Output 1:
    YES

    Example 2:
    #cerco
    Ciao!

    Sono uno studente internazionale che sta facendo ricerca estiva e sto cercando un posto solo per il mese di settembre, a Rovereto o Trento, per trascorrere l’ultimo mese del mio tirocinio qui.

    Se qualcuno ha una stanza disponibile, per favore fatemelo sapere.
    Inoltre, se qualcuno è in viaggio e potesse subaffittare il suo posto per settembre, sarebbe fantastico!

    Grazie! 🙃
    Output 2:
    NO

    Example 3:
    Ciao! Sono in cerca di una nuova coinquilina per il mio appartamento in centro a Trento.
    Scrivetemi se interessati!
    Output 3:
    MALFORMED, no price detected.

    The following text is the message to be analyzed:
    {msg}
    """

    res = call_ollama(OLLAMA_URL, MODEL_NAME, classification_prompt)
    print("for fuck's sake")
    print(res)
    classification_res = res.strip().upper() == "YES"
    return {
            "is_announcement": classification_res
    }

def call_ollama(url, model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 200,
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print("fuck you")
    print(response)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "").strip()
