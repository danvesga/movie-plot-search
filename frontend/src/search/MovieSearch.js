import React, { useState } from 'react';
import { searchMovies, getRecommendations } from './api';

export default function MovieSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const movies = await searchMovies(query);
      setResults(movies);
    } catch (error) {
      alert('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async (movieId) => {
    setLoading(true);
    try {
      const recommendations = await getRecommendations(movieId);
      setResults(recommendations);
    } catch (error) {
      alert('Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Movie Search</h1>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe a movie plot..."
            className="flex-1 px-4 py-2 border rounded"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {results.map((movie) => (
          <div key={movie.id} className="border rounded p-4 shadow">
            <h3 className="font-bold text-lg mb-2">{movie.title}</h3>
            <p className="text-sm text-gray-600 mb-2">{movie.release_date}</p>
            <p className="text-sm mb-3">{movie.overview}</p>
            <p className="text-xs text-gray-500 mb-2">Genres: {movie.genres}</p>
            <div className="mb-3">
              <p className="text-xs text-gray-500 mb-1">Confidence Score:</p>
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
            <button
              onClick={() => handleRecommend(movie.id)}
              className="px-4 py-2 bg-green-500 text-white rounded text-sm hover:bg-green-600"
            >
              Similar Movies
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}