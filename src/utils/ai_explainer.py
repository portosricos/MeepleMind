import os
import requests

def ask_ollama(prompt: str, model: str = "phi3") -> str:
    """Send prompt to Ollama API model with automatic host discovery and fallback."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    # Candidate Ollama endpoint URLs to try in order
    candidate_hosts = []
    env_host = os.getenv("OLLAMA_HOST")
    if env_host:
        candidate_hosts.append(env_host)
    
    candidate_hosts.extend([
        "http://ollama:11434",
        "http://host.docker.internal:11434",
        "http://localhost:11434",
        "http://127.0.0.1:11434"
    ])
    
    # Remove duplicate candidate URLs while preserving order
    candidate_hosts = list(dict.fromkeys(candidate_hosts))
    
    last_error = None
    for host in candidate_hosts:
        try:
            url = f"{host.rstrip('/')}/api/generate"
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()["response"].strip()
        except Exception as e:
            last_error = e
            continue
            
    return (
        f"Error communicating with local AI model ({str(last_error)}). "
        f"Please make sure Ollama is running (e.g. `ollama serve`) and has pulled the '{model}' model (`ollama pull {model}`)."
    )

def generate_game_explanation(rec: dict, liked_games: list, model: str = "phi3") -> str:
    """Construct prompt and query Ollama for why the user will love a specific recommended game."""
    prompt = f"""
You are a board game expert and enthusiast. 
Explain to a user why they would love the board game: "{rec['Name']}".
The user currently loves these board games: {', '.join(liked_games)}.

Details for "{rec['Name']}":
- Complexity (Weight): {rec['GameWeight']}/5
- Average User Rating: {rec['AvgRating']}/10
- Play Time: {rec['MinPlaytime']}-{rec['MaxPlaytime']} minutes
- Players: {rec['MinPlayers']}-{rec['MaxPlayers']}
- Categories: {', '.join(rec['Categories'])}
- Mechanics: {', '.join(rec['Mechanics'])}
- Themes: {', '.join(rec['Themes'])}

Shared features with their liked games:
- Shared Categories: {', '.join(rec['SharedCategories'])}
- Shared Mechanics: {', '.join(rec['SharedMechanics'])}
- Shared Themes: {', '.join(rec['SharedThemes'])}

Instructions:
- Write a friendly, enthusiastic, and concise response (maximum 3 sentences).
- Explain the gameplay feel and how it leverages the shared features.
- Answer directly without starting with "Sure, here is the explanation".
"""
    return ask_ollama(prompt, model=model)
