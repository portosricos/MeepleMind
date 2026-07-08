import requests

username = "portos"
# BGG XML API v1 collection endpoint
url1 = f"https://boardgamegeek.com/xmlapi/collection/{username}"
url2 = f"https://boardgamegeek.com/xmlapi/collection?username={username}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for url in [url1, url2]:
    print(f"\nQuerying BGG XML API v1 URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print("Status Code:", response.status_code)
        print("Response Length:", len(response.text))
        print("Response Snippet (first 300 chars):")
        print(response.text[:300])
    except Exception as e:
        print("Error:", str(e))
