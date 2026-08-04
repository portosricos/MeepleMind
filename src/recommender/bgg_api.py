import time
import requests
import xml.etree.ElementTree as ET
from typing import Tuple, List
from src.utils.config import get_bgg_api_token

def fetch_bgg_collection(username: str, all_catalog_names: List[str]) -> Tuple[bool, str, List[str]]:
    """
    Queries BGG XML API2 for owned games of a given username.
    Returns tuple: (success: bool, error_message: str, matched_catalog_games: List[str])
    """
    token = get_bgg_api_token()
    url = f"https://boardgamegeek.com/xmlapi2/collection?username={username.strip()}&own=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Authorization': f'Bearer {token}'
    }
    
    success = False
    error_msg = ""
    owned_games = []
    
    # BGG API can return HTTP 202 if preparing data. We retry up to 4 times with short delays.
    for attempt in range(4):
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                # Check for API error response
                error_elem = root.find('error')
                if error_elem is not None:
                    error_msg = "User not found"
                    break
                
                items = root.findall('item')
                for item in items:
                    name_elem = item.find('name')
                    if name_elem is not None and name_elem.text:
                        owned_games.append(name_elem.text)
                success = True
                break
            elif res.status_code == 202:
                time.sleep(3) # Wait for BGG to compile the list
                continue
            else:
                error_msg = "User not found"
                break
        except Exception:
            error_msg = "User not found"
            time.sleep(2)
            
    if success:
        all_names_lower = {n.lower(): n for n in all_catalog_names}
        matched = []
        for g_name in owned_games:
            if g_name.lower() in all_names_lower:
                matched.append(all_names_lower[g_name.lower()])
        return True, "", matched
    else:
        return False, error_msg if error_msg else "User not found", []
