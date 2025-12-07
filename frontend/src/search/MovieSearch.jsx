import React, { useState } from 'react';
import { searchMovies, getRecommendations } from './api';
import GenreDropdown from './GenreDropdown';
import ActorInput from './ActorInput';
import MovieCard from './MovieCard';
import '../App.css'

function MovieSearch() {
  console.log('MovieSearch component loaded');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [selectedActors, setSelectedActors] = useState([]);
  const [error, setError] = useState('');
  const [lockedMovieId, setLockedMovieId] = useState(null);
  
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    try {
      const movies = await searchMovies(query, 10, selectedGenres, selectedActors);
      setResults(movies);
      
      if (movies.length === 0) {
        setError('No movies found matching your search and filters. Try adjusting your filters or search query.');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async (movieId) => {
    setLoading(true);
    setError('');
    try {
      const recommendations = await getRecommendations(movieId, 10, selectedGenres, selectedActors);
      setResults(recommendations);
      
      if (recommendations.length === 0) {
        setError('No recommendations found for this movie with the current filters.');
      }
    } catch (error) {
      console.error('Recommend error:', error);
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
        <div className="flex flex-row justify-center items-center gap-16 mt-4">
          <div className="plot-input">
            <ActorInput 
              selectedActors={selectedActors} 
              setSelectedActors={setSelectedActors} 
            />
          </div>
          <div className="plot-input">
            <GenreDropdown 
              selectedGenres={selectedGenres} 
              setSelectedGenres={setSelectedGenres} 
            />
          </div>
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

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {results.map((movie) => (
          <MovieCard 
            key={movie.id} 
            movie={movie} 
            onRecommend={handleRecommend}
            lockedMovie={lockedMovieId}
            setLockedMovie={setLockedMovieId}
          />
        ))}
      </div>
    </div>
  );
}

export default MovieSearch;