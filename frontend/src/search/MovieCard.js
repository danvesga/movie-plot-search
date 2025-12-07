import React, { useState, useRef, useLayoutEffect, useEffect } from 'react';

function MovieCard({ movie, onRecommend, lockedMovie , setLockedMovie }) {
  const [isLocked, setIsLocked] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);
  const containerRef = useRef(null);
  const tooltipRef = useRef(null);

  const toggleMovieLocked = () => {
    if (lockedMovie !== movie.id) {
      setLockedMovie(movie.id);
      setIsLocked(true);
    }
    else if (lockedMovie === movie.id) {
      setLockedMovie(null);
      setIsLocked(false);
    }
  }
  const getTMDBImageUrl = (posterPath, size = 'w342') => {
    if (!posterPath) return null;
    const baseUrl = 'https://image.tmdb.org/t/p/';
    return `${baseUrl}${size}${posterPath}`;
  };

  const posterUrl = getTMDBImageUrl(movie.poster_path);
  const placeholderUrl = 'https://via.placeholder.com/342x513/cccccc/666666?text=No+Poster';

  // Calculate whether the tooltip should flip to the left to avoid overflowing the viewport.
  useLayoutEffect(() => {
    const visible = (isHovered && lockedMovie === null) || (isLocked && lockedMovie === movie.id);
    if (!visible) return;
    const container = containerRef.current;
    const tooltip = tooltipRef.current;
    if (!container) return;
    const containerRect = container.getBoundingClientRect();
    const tooltipWidth = tooltip ? tooltip.offsetWidth : 320; // fallback width for w-80 (20rem ~ 320px)
    const margin = 8;
    setIsFlipped(containerRect.right + tooltipWidth + margin > window.innerWidth);
  }, [isHovered, isLocked, lockedMovie, movie.id]);

  useEffect(() => {
    const handleResize = () => {
      const visible = (isHovered && lockedMovie === null) || (isLocked && lockedMovie === movie.id);
      if (!visible) return;
      const container = containerRef.current;
      const tooltip = tooltipRef.current;
      if (!container) return;
      const tooltipWidth = tooltip ? tooltip.offsetWidth : 320;
      setIsFlipped(container.getBoundingClientRect().right + tooltipWidth + 8 > window.innerWidth);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isHovered, isLocked, lockedMovie, movie.id]);
  
  return (
    <div 
      ref={containerRef}
      className="relative group cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => toggleMovieLocked()}
    >
      {/* Movie Poster */}
      <div className="aspect-[2/3] overflow-hidden rounded-lg shadow-md transition-transform duration-200 group-hover:scale-105">
        <img 
          src={posterUrl || placeholderUrl}
          alt={`${movie.title} poster`}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.src = placeholderUrl;
          }}
        />
      </div>

      {/* Hover Details Box */}
      {((isHovered && lockedMovie === null) || (isLocked && lockedMovie === movie.id)) && (
        <div 
          ref={tooltipRef}
          className={`absolute top-0 w-80 bg-white border border-gray-300 rounded-lg shadow-xl p-4 z-50 pointer-events-none ${isFlipped ? 'right-full mr-2' : 'left-full ml-2'}`}
        >
          <h3 className="font-bold text-lg mb-2">{movie.title}</h3>
          <p className="text-sm text-gray-600 mb-2">
            <span className="font-semibold">Release:</span> {movie.release_date || 'N/A'}
          </p>
          <p className="text-sm text-gray-600 mb-2">
            <span className="font-semibold">Genres:</span> {movie.genres || 'N/A'}
          </p>
          
          <div className="mb-3">
            <p className="text-sm font-semibold mb-1">Confidence Score:</p>
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

          <p className={`text-sm text-gray-700 mb-3 ${isLocked ? '' : 'line-clamp-3'}`}>
            <span className="font-semibold">Overview:</span> {movie.overview || 'No overview available.'}
          </p>
          {!isLocked && <span className="text-blue-500 ml-1"> read more </span>}

        </div>
      )}
    </div>
  );
}

export default MovieCard;