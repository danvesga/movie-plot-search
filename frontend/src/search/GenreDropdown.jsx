import React from 'react';

const GENRES = [
  'Animation', 'Action', 'Adventure', 'Comedy', 'Crime', 
  'Drama', 'Family', 'Fantasy', 'History', 'Horror', 
  'Music', 'Mystery', 'Romance', 'Science Fiction', 
  'Thriller', 'War', 'Western'
];

function GenreDropdown({ selectedGenres, setSelectedGenres }) {
  const handleGenreSelect = (e) => {
    const genre = e.target.value;
    if (genre && !selectedGenres.includes(genre)) {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const removeGenre = (genreToRemove) => {
    setSelectedGenres(selectedGenres.filter(g => g !== genreToRemove));
  };

  const availableGenres = GENRES.filter(g => !selectedGenres.includes(g));

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium mb-2">
        Add Genres:
      </label>
      
      <select
        onChange={handleGenreSelect}
        value=""
        className="px-4 py-2 border rounded bg-white cursor-pointer"
      >
        <option value="" disabled>
          Select a genre...
        </option>
        {availableGenres.map(genre => (
          <option key={genre} value={genre}>
            {genre}
          </option>
        ))}
      </select>

      {selectedGenres.length > 0 && (
        <div className="mt-3">
          <div className="flex flex-wrap gap-2">
            {selectedGenres.map(genre => (
              <div
                key={genre}
                className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-full text-sm"
              >
                <span>{genre}</span>
                <button
                  type="button"
                  onClick={() => removeGenre(genre)}
                  className="hover:bg-blue-600 rounded-full w-5 h-5 flex items-center justify-center"
                  aria-label={`Remove ${genre}`}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setSelectedGenres([])}
            className="mt-2 text-sm text-red-500 hover:text-red-700"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
}

export default GenreDropdown;