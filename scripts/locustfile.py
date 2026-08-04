import random
from locust import HttpUser, task, between

SAMPLE_LOCKED_GAMES = [
    "Catan",
    "Pandemic",
    "Wingspan",
    "Terraforming Mars",
    "Gloomhaven",
    "7 Wonders",
    "Codenames",
    "Azul",
    "Carcassonne",
    "Ticket to Ride",
    "Scythe",
    "Brass: Birmingham"
]

PLAYTIME_OPTIONS = [
    "Any Duration",
    "Short (< 30 min)",
    "Medium (30 - 60 min)",
    "Long (60 - 120 min)",
    "Epic (120 - 200 min)"
]

BGG_TEST_USERNAMES = ["portos", "tomvasel", "rahdo", "boardgamegeek"]

class MeepleMindUser(HttpUser):
    """Simulates a user browsing MeepleMind and requesting recommendations."""
    
    # Wait between 1 and 3 seconds between simulated requests
    wait_time = between(1.0, 3.0)

    @task(1)
    def check_health(self):
        """Simulate health check ping."""
        self.client.get("/health", name="GET /health")

    @task(2)
    def fetch_metadata(self):
        """Simulate loading catalog metrics & game names list."""
        self.client.get("/api/v1/metadata", name="GET /api/v1/metadata")

    @task(5)
    def recommend_manual_search(self):
        """Simulate user selecting 1-3 seed games for recommendations."""
        num_seeds = random.randint(1, 3)
        selected = random.sample(SAMPLE_LOCKED_GAMES, num_seeds)
        
        payload = {
            "selected_names": selected,
            "player_count_range": [2, 4],
            "playtime_option": "Any Duration",
            "complexity_range": [1.0, 5.0],
            "selected_cats": [],
            "selected_mechs": [],
            "selected_themes": [],
            "exclude_names": None,
            "use_profile_similarity": False,
            "top_n": 5
        }
        self.client.post("/api/v1/recommend", json=payload, name="POST /api/v1/recommend (Manual Search)")

    @task(3)
    def recommend_with_filters(self):
        """Simulate user applying range sliders (player count, playtime, complexity)."""
        num_seeds = random.randint(1, 2)
        selected = random.sample(SAMPLE_LOCKED_GAMES, num_seeds)
        playtime = random.choice(PLAYTIME_OPTIONS)
        min_p = random.randint(1, 3)
        max_p = random.randint(min_p, 6)
        
        payload = {
            "selected_names": selected,
            "player_count_range": [min_p, max_p],
            "playtime_option": playtime,
            "complexity_range": [2.0, 4.0],
            "selected_cats": [],
            "selected_mechs": [],
            "selected_themes": [],
            "exclude_names": None,
            "use_profile_similarity": False,
            "top_n": 5
        }
        self.client.post("/api/v1/recommend", json=payload, name="POST /api/v1/recommend (With Filters)")

    @task(2)
    def sync_bgg_collection(self):
        """Simulate BGG XML API collection sync lookup."""
        username = random.choice(BGG_TEST_USERNAMES)
        payload = {"username": username}
        self.client.post("/api/v1/bgg-collection", json=payload, name="POST /api/v1/bgg-collection")
