from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"

class MetadataResponse(BaseModel):
    total_games: int
    total_mechanics: int
    total_themes: int
    categories: List[str]
    mechanics: List[str]
    themes: List[str]
    all_names: List[str]

class RecommendationRequest(BaseModel):
    selected_names: List[str] = Field(default_factory=list)
    player_count_range: Optional[Tuple[int, int]] = None
    playtime_option: Optional[str] = None
    complexity_range: Optional[Tuple[float, float]] = None
    selected_cats: Optional[List[str]] = None
    selected_mechs: Optional[List[str]] = None
    selected_themes: Optional[List[str]] = None
    exclude_names: Optional[List[str]] = None
    use_profile_similarity: bool = False
    top_n: int = 5

class RecommendationItem(BaseModel):
    BGGId: int
    Name: str
    Description: str
    YearPublished: int
    GameWeight: float
    AvgRating: float
    BayesAvgRating: float
    MinPlayers: int
    MaxPlayers: int
    ComAgeRec: float
    LanguageEase: float
    BestPlayers: str
    TotalEngagement: int
    MaxPlaytime: float
    MinPlaytime: float
    ImagePath: str
    Categories: List[str]
    Mechanics: List[str]
    Themes: List[str]
    Similarity: float
    Score: float
    SharedCategories: List[str]
    SharedMechanics: List[str]
    SharedThemes: List[str]

class BGGCollectionRequest(BaseModel):
    username: str

class BGGCollectionResponse(BaseModel):
    success: bool
    error_msg: str = ""
    matched_games: List[str] = Field(default_factory=list)

class ExplainRequest(BaseModel):
    rec: dict
    liked_games: List[str] = Field(default_factory=list)
    model: str = "phi3"

class ExplainResponse(BaseModel):
    explanation: str
