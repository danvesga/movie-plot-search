import React, { useState } from 'react';
import { searchMovies, getRecommendations } from './api';
import GenreDropdown from './GenreDropdown';
import '../App.css'

function MovieSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [error, setError] = useState('');

  const getTMDBImageUrl = (posterPath, size = 'w185') => {
    if (!posterPath) return null;
    const baseUrl = 'https://image.tmdb.org/t/p/';
    // Available sizes: w92, w154, w185, w342, w500, w780, original
    return `${baseUrl}${size}${posterPath}`;
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    try {
      const movies = await searchMovies(query, 10, selectedGenres);
      setResults(movies);
      
      if (movies.length === 0) {
        setError('No movies found matching your search and filters. Try adjusting your filters or search query.');
      }
    } catch (error) {
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async (movieId) => {
    setLoading(true);
    setError('');
    try {
      const recommendations = await getRecommendations(movieId, 10, selectedGenres);
      setResults(recommendations);
      
      if (recommendations.length === 0) {
        setError('No recommendations found for this movie with the current filters.');
      }
    } catch (error) {
      setError('Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <h1 className="text-3xl font-bold mb-6">Movie Search</h1>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="plot-input">
          <label className="block text-sm font-medium mb-2">
            Describe the movie plot:
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., A heist movie set in space with a twist ending..."
            className="w-1/2 px-4 py-2 border rounded resize-y min-h-[100px]"
            rows={4}
          />
        </div>

        <div className="plot-input">
          <label className="block text-sm font-medium mb-2">
            Filter by Genre (optional):
          </label>
          <GenreDropdown 
            selectedGenres={selectedGenres} 
            setSelectedGenres={setSelectedGenres} 
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {results.map((movie) => (
          <div key={movie.id} className="border rounded p-4 shadow p-8">
            {movie.poster_path && (
              <img 
                src={getTMDBImageUrl(movie.poster_path)} 
                alt={`${movie.title} poster`}
                className="w-full h-64 object-cover rounded mb-3"
                onError={(e) => {
                  e.target.style.display = 'none'; // Hide if image fails to load
                }}
              />
            )}
            
            <h3 className="font-bold text-lg mb-2">{movie.title}</h3>
            <p className="text-sm text-gray-600 mb-2">{movie.release_date}</p>
            <p className="text-sm mb-3 line-clamp-3">{movie.overview}</p>
            <p className="text-xs text-gray-500 mb-2">Genres: {movie.genres}</p>
            <div className="mb-3">
              <p className="text-xs text-gray-500 mb-1">Confidence Score: </p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${movie.score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold">{(movie.score * 100).toFixed(1)}%</span>
              </div>
            </div>
            {/* <button
              onClick={() => handleRecommend(movie.id)}
              className="px-4 py-2 bg-green-500 text-white rounded text-sm hover:bg-green-600"
            >
              Similar Movies
            </button> */}
          </div>
        ))}
      </div>
    </div>
  );
}

export default MovieSearch;