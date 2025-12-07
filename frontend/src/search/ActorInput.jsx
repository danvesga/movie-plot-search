import React, { useState } from 'react';

function ActorInput({ selectedActors, setSelectedActors }) {
  const [actorInput, setActorInput] = useState('');

  const handleAddActor = (e) => {
    e.preventDefault();
    const actor = actorInput.trim();
    if (actor && !selectedActors.includes(actor)) {
      setSelectedActors([...selectedActors, actor]);
      setActorInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddActor(e);
    }
  };

  const removeActor = (actorToRemove) => {
    setSelectedActors(selectedActors.filter(a => a !== actorToRemove));
  };

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium mb-2">
        Add Actors:
      </label>
      
      <div className="flex gap-2">
        <input
          type="text"
          value={actorInput}
          onChange={(e) => setActorInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type actor name and press Enter"
          className="flex-1 px-4 py-2 border rounded"
        />
        <button
          type="button"
          onClick={handleAddActor}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
           + 
        </button>
      </div>

      {selectedActors.length > 0 && (
        <div className="mt-3">
          <div className="flex flex-wrap gap-2">
            {selectedActors.map((actor, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-1 bg-purple-500 text-white rounded-full text-sm"
              >
                <span>{actor}</span>
                <button
                  type="button"
                  onClick={() => removeActor(actor)}
                  className="hover:bg-purple-600 rounded-full w-5 h-5 flex items-center justify-center"
                  aria-label={`Remove ${actor}`}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setSelectedActors([])}
            className="mt-2 text-sm text-red-500 hover:text-red-700"
          >
            Clear all actors
          </button>
        </div>
      )}
    </div>
  );
}

export default ActorInput;