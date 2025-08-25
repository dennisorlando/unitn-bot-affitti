import requests
import json
import re

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "gemma3:4b"

def process_message(db, msg, model='ollama', gemini_key=None):
   
    classification_res = classify_message(msg, model, gemini_key)
    
    
    if not classification_res:
        return {
            "message": msg["text"],
            "extracted_features": None,
        }

    extracted_features = extract_features(msg, model, gemini_key)
    return {
        "message": msg["text"],
        "extracted_features": extracted_features
    }

def extract_features(msg, model, gemini_key):
    extraction_prompt = f"""
    Extract rental features from this apartment/room announcement and output ONLY valid JSON.

    Required JSON structure:
    {{
        "price_per_month": number or null,
        "room_type": "single" | "double" | null,
        "location": "string description" or null,
        "target_gender": "male" | "female" | "any" | null,
        "target_audience": "students" | "professionals" | "any" | null,
        "available_from": "string date/month" or null,
        "contract_duration": "string duration" or null,
        "utilities_included": true | false | null,
        "amenities": ["wifi", "laundry", "parking", "elevator", "balcony", "kitchen"],
        "other": ["string", "string2"...],
    }}
    
    Rules:
    - Extract exact prices in euros (use numbers only, no currency symbols)
    - For room_type: "single" = one person, "double" = two people, "shared" = shared room
    - Put any non-standard features in "other" object
    - Use null for missing information
    - Output ONLY the JSON, no explanations
    
    Example:
    Input: "Stanza doppia via Matteotti - per studentesse, al secondo piano. Costo 260€ al mese spese incluse. Wifi, ascensore. Disponibile settembre.
    Output:
    {{
        "price_per_month": 260,
        "room_type": "double", 
        "location": "via Matteotti",
        "target_gender": "female",
        "target_audience": "students",
        "available_from": "settembre",
        "contract_duration": null,
        "utilities_included": true,
        "amenities": ["wifi", "elevator"],
        "other": [ "Second floor" ]
    }}
    
    Extract from this message:
    {msg}
    """
   
    if model == "ollama":
        res = call_ollama(OLLAMA_URL, MODEL_NAME, extraction_prompt)
    elif model == "gemini":
        res = call_gemini(extraction_prompt, gemini_key)

    try:
        # Strip any thinking tags and extra content
        cleaned_response = re.sub(r'<think>.*?</think>', '', res, flags=re.DOTALL).strip()
        
        # Try to find JSON in the response
        import json
        
        # Look for JSON object in the response
        json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # Fallback: try to parse the entire cleaned response
            return json.loads(cleaned_response)
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {res}")
        return {
            "price_per_month": None,
            "room_type": None,
            "location": None,
            "target_gender": None,
            "target_audience": None,
            "available_from": None,
            "contract_duration": None,
            "utilities_included": None,
            "amenities": [],
            "other": {"extraction_error": "Failed to parse response", "raw_response": res}
        }

def classify_message(msg, model, gemini_key):
    classification_prompt = f"""
        Analyze the following message and determine if it's an apartment/room rental announcement.
        Respond only with "YES" if it's clearly an apartment/room rental announcement and "NO" otherwise.
        Respond with "NO" if it is an announcement for people LOOKING for apartments.
        If it's a strange message that doesn't fall into any category clearly or doesn't contain key information (especially PRICE), then respond with MALFORMED and explain why.
        Remember to stick to this format, as any other output format will mess a processor which will read your message.
    
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
   
    if model == "ollama":
        res = call_ollama(OLLAMA_URL, MODEL_NAME, classification_prompt)
    elif model == "gemini":
        res = call_gemini(classification_prompt, gemini_key)
    classification_res = res.strip().upper().startswith("YES")
    return classification_res # for now, we only handle positives


def call_gemini(prompt_text, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_text
                    }
                ]
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()

    # Gemini response structure example:
    # {
    #   "candidates": [
    #     {
    #       "content": "Generated answer text"
    #     }
    #   ],
    #   ...
    # }

    raw_response = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip().replace("\n", "")
    # Optionally clean <think> tags if Gemini uses them (unlikely, but for parity)
    cleaned_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()

    return cleaned_response

def call_ollama(url, model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()

    raw_response = result.get("response", "").strip().replace("\n", "")
    # strip thinking process
    cleaned_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()

    return cleaned_response
