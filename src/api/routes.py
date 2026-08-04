from fastapi import APIRouter, HTTPException
from src.recommender.engine import load_data, recommend_games
from src.recommender.bgg_api import fetch_bgg_collection
from src.utils.ai_explainer import generate_game_explanation
from src.api.schemas import (
    HealthResponse,
    MetadataResponse,
    RecommendationRequest,
    RecommendationItem,
    BGGCollectionRequest,
    BGGCollectionResponse,
    ExplainRequest,
    ExplainResponse
)
from typing import List

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")

@router.get("/api/v1/metadata", response_model=MetadataResponse)
def get_metadata():
    """Retrieve catalog sizes, all categories, mechanics, themes, and game names list."""
    try:
        data = load_data()
        df = data['metadata']
        categories = data['categories']
        mechanics = sorted(data['mechanics'])
        themes = sorted(data['themes'])
        all_names = sorted(df['Name'].tolist())
        
        return MetadataResponse(
            total_games=len(df),
            total_mechanics=len(mechanics),
            total_themes=len(themes),
            categories=categories,
            mechanics=mechanics,
            themes=themes,
            all_names=all_names
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load metadata: {str(e)}")

@router.post("/api/v1/recommend", response_model=List[RecommendationItem])
def get_recommendations(req: RecommendationRequest):
    """Execute recommendation engine given user liked games, range filters, and exclusions."""
    try:
        player_range = tuple(req.player_count_range) if req.player_count_range else None
        complexity_range = tuple(req.complexity_range) if req.complexity_range else None
        
        results = recommend_games(
            selected_names=req.selected_names,
            player_count_range=player_range,
            playtime_option=req.playtime_option,
            complexity_range=complexity_range,
            selected_cats=req.selected_cats,
            selected_mechs=req.selected_mechs,
            selected_themes=req.selected_themes,
            exclude_names=req.exclude_names,
            use_profile_similarity=req.use_profile_similarity,
            top_n=req.top_n
        )
        return [RecommendationItem(**r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")

@router.post("/api/v1/bgg-collection", response_model=BGGCollectionResponse)
def get_bgg_collection(req: BGGCollectionRequest):
    """Fetch user collection from BGG XML API2 and match against local catalog."""
    try:
        data = load_data()
        all_names = data['metadata']['Name'].tolist()
        success, error_msg, matched = fetch_bgg_collection(req.username, all_names)
        
        return BGGCollectionResponse(
            success=success,
            error_msg=error_msg,
            matched_games=matched
        )
    except Exception as e:
        return BGGCollectionResponse(
            success=False,
            error_msg=f"Error connecting to BGG API: {str(e)}",
            matched_games=[]
        )

@router.post("/api/v1/explain", response_model=ExplainResponse)
def explain_game(req: ExplainRequest):
    """Generate LLM gameplay explanation using local Ollama model."""
    try:
        explanation = generate_game_explanation(req.rec, req.liked_games, model=req.model)
        return ExplainResponse(explanation=explanation)
    except Exception as e:
        return ExplainResponse(explanation=f"Error generating explanation: {str(e)}")
