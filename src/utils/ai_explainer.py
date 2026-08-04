import requests

def ask_ollama(prompt: str, model: str = "phi3") -> str:
    """Send prompt to local Ollama API model and return text response."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"Error communicating with local AI model: {str(e)}. Please make sure Ollama is running and has the '{model}' model pulled."

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
