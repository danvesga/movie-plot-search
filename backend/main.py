from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Movie Search API")

# Add CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model and Pinecone on startup
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Connecting to Pinecone...")
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('movie-plots')

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    genres: Optional[List[str]] = None
    actors: Optional[List[str]] = None

class Movie(BaseModel):
    id: str
    title: str
    overview: str
    genres: str
    release_date: str
    popularity: float
    poster_path: str
    production_companies: str
    credits: str
    score: float

class SearchResponse(BaseModel):
    results: List[Movie]
    query: str

class RecommendRequest(BaseModel):
    movie_id: str
    top_k: Optional[int] = 10
    genres: Optional[List[str]] = None
    actors: Optional[List[str]] = None

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Movie Search API is running"}

@app.post("/search", response_model=SearchResponse)
def search_movies(request: SearchRequest):
    """
    Search for movies based on plot description with optional genre and actor filtering.
    Actors are weighted more heavily in the ranking.
    """
    try:
        query_embedding = model.encode(request.query).tolist()
        
        # Get more results if filtering is needed
        needs_filtering = (request.genres and len(request.genres) > 0) or (request.actors and len(request.actors) > 0)
        fetch_count = request.top_k * 10 if needs_filtering else request.top_k
        
        # Query Pinecone WITHOUT any filter
        results = index.query(
            vector=query_embedding,
            top_k=min(fetch_count, 100),  # Cap at 100
            include_metadata=True
        )
        
        # Filter and score by genre and actors
        movies = []
        for match in results['matches']:
            movie_genres = match['metadata'].get('genres', '').lower()
            movie_credits = match['metadata'].get('credits', '').lower()
            
            # Genre filtering (hard filter - must match if specified)
            if request.genres and len(request.genres) > 0:
                genre_match = False
                for genre in request.genres:
                    if genre.lower() in movie_genres:
                        genre_match = True
                        break
                
                if not genre_match:
                    continue
            
            # Actor matching and boosting
            actor_boost = 0.0
            if request.actors and len(request.actors) > 0:
                actor_matches = 0
                for actor in request.actors:
                    if actor.lower() in movie_credits:
                        actor_matches += 1
                
                # Calculate boost: each matching actor adds significant boost
                # With multiple actors, boost increases exponentially
                if actor_matches > 0:
                    actor_boost = 0.15 * actor_matches  # 15% boost per matching actor
                else:
                    # If actors specified but none match, skip this movie
                    continue
            
            # Apply actor boost to the similarity score
            boosted_score = min(match['score'] + actor_boost, 1.0)  # Cap at 1.0
            
            movies.append({
                'movie': Movie(
                    id=match['id'],
                    title=match['metadata'].get('title', ''),
                    overview=match['metadata'].get('overview', ''),
                    genres=match['metadata'].get('genres', ''),
                    release_date=match['metadata'].get('release_date', ''),
                    popularity=match['metadata'].get('popularity', 0),
                    poster_path=match['metadata'].get('poster_path', ''),
                    production_companies=match['metadata'].get('production_companies', ''),
                    credits=match['metadata'].get('credits', ''),
                    score=boosted_score
                ),
                'boosted_score': boosted_score
            })
        
        # Sort by boosted score (highest first)
        movies.sort(key=lambda x: x['boosted_score'], reverse=True)
        
        # Extract just the Movie objects and limit to top_k
        final_movies = [item['movie'] for item in movies[:request.top_k]]
        
        return SearchResponse(results=final_movies, query=request.query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend", response_model=SearchResponse)
def recommend_movies(request: RecommendRequest):
    """
    Get movie recommendations based on a specific movie with optional genre and actor filtering.
    """
    try:
        # Fetch the movie's vector from Pinecone
        movie_data = index.fetch(ids=[request.movie_id])
        
        if not movie_data['vectors'] or request.movie_id not in movie_data['vectors']:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Get the movie's embedding
        movie_vector = movie_data['vectors'][request.movie_id]['values']
        
        # Get more results if filtering
        needs_filtering = (request.genres and len(request.genres) > 0) or (request.actors and len(request.actors) > 0)
        fetch_count = (request.top_k + 1) * 5 if needs_filtering else request.top_k + 1
        
        # Query for similar movies
        results = index.query(
            vector=movie_vector,
            top_k=min(fetch_count, 100),
            include_metadata=True
        )
        
        # Format results (exclude the original movie and apply filters)
        movies = []
        for match in results['matches']:
            # Skip the original movie
            if match['id'] == request.movie_id:
                continue
            
            movie_genres = match['metadata'].get('genres', '').lower()
            movie_credits = match['metadata'].get('credits', '').lower()
            
            # Genre filtering
            if request.genres and len(request.genres) > 0:
                genre_match = False
                for genre in request.genres:
                    if genre.lower() in movie_genres:
                        genre_match = True
                        break
                
                if not genre_match:
                    continue
            
            # Actor filtering
            if request.actors and len(request.actors) > 0:
                actor_match = False
                for actor in request.actors:
                    if actor.lower() in movie_credits:
                        actor_match = True
                        break
                
                if not actor_match:
                    continue
            
            movies.append(Movie(
                id=match['id'],
                title=match['metadata'].get('title', ''),
                overview=match['metadata'].get('overview', ''),
                genres=match['metadata'].get('genres', ''),
                release_date=match['metadata'].get('release_date', ''),
                popularity=match['metadata'].get('popularity', 0),
                poster_path=match['metadata'].get('poster_path', ''),
                production_companies=match['metadata'].get('production_companies', ''),
                credits=match['metadata'].get('credits', ''),
                score=match['score']
            ))
            
            if len(movies) >= request.top_k:
                break
        
        original_title = movie_data['vectors'][request.movie_id]['metadata'].get('title', 'Unknown')
        return SearchResponse(
            results=movies, 
            query=f"Similar to: {original_title}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "model": "all-MiniLM-L6-v2", "index": "movie-plots"}

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)