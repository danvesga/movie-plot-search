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

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Movie Search API is running"}

@app.post("/search", response_model=SearchResponse)
def search_movies(request: SearchRequest):
    """
    Search for movies based on plot description.
    """
    try:
        # Generate embedding for the search query
        query_embedding = model.encode(request.query).tolist()
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=request.top_k,
            include_metadata=True
        )
        
        # Format results
        movies = []
        for match in results['matches']:
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
        
        return SearchResponse(results=movies, query=request.query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend", response_model=SearchResponse)
def recommend_movies(request: RecommendRequest):
    """
    Get movie recommendations based on a specific movie.
    """
    try:
        # Fetch the movie's vector from Pinecone
        movie_data = index.fetch(ids=[request.movie_id])
        
        if not movie_data['vectors']:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Get the movie's embedding
        movie_vector = movie_data['vectors'][request.movie_id]['values']
        
        # Query for similar movies
        results = index.query(
            vector=movie_vector,
            top_k=request.top_k + 1,  # +1 because the movie itself will be in results
            include_metadata=True
        )
        
        # Format results (exclude the original movie)
        movies = []
        for match in results['matches']:
            if match['id'] != request.movie_id:  # Skip the original movie
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
        
        return SearchResponse(
            results=movies[:request.top_k], 
            query=f"Similar to: {movie_data['vectors'][request.movie_id]['metadata'].get('title', '')}"
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