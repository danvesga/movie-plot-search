const API_BASE_URL = 'http://localhost:8000';

export const searchMovies = async (query, topK = 10, genres = [], actors = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        top_k: topK,
        genres: genres,
        actors: actors
      })
    });

    if (!response.ok) {
      throw new Error('Search failed');
    }

    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('Error searching movies:', error);
    throw error;
  }
};

export const getRecommendations = async (movieId, topK = 10, genres = [], actors = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        movie_id: movieId,
        top_k: topK,
        genres: genres,
        actors: actors
      })
    });

    if (!response.ok) {
      throw new Error('Recommendation failed');
    }

    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};