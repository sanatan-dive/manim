import React, { useState } from 'react';
import './App.css';

// Main App component for the Manim Animation Generator
const App: React.FC = () => {
  // State to store the user's prompt for the Manim animation
  const [prompt, setPrompt] = useState<string>('');
  // State to manage the loading status during API calls
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // State to store the URL of the generated Manim video
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  // State to store any error messages
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles the submission of the user's prompt.
   * This function will make a fetch request to the conceptual backend.
   */
  const handleSubmit = async () => {
    // Clear previous errors and video URL
    setError(null);
    setVideoUrl(null);
    // Set loading state to true
    setIsLoading(true);

    try {
      // Make a POST request to your conceptual backend endpoint.
      // Replace 'http://127.0.0.1:5000/generate-manim' with your actual backend endpoint if deployed
      const response = await fetch('http://127.0.0.1:5000/generate-manim', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      // Check if the response from the backend is successful
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to generate Manim animation.');
      }

      // Parse the JSON response from the backend
      const data = await response.json();
      // Set the video URL received from the backend (this will be null/undefined as per current backend logic)
      setVideoUrl(data.videoUrl);

    } catch (err: any) {
      // Catch and display any errors during the fetch operation
      setError(err.message || 'An unexpected error occurred.');
      console.error('Error generating Manim animation:', err);
    } finally {
      // Set loading state back to false
      setIsLoading(false);
    }
  };

  /**
   * Clears the prompt input and any displayed video/errors.
   */
  const handleClear = () => {
    setPrompt('');
    setVideoUrl(null);
    setError(null);
    setIsLoading(false); // Ensure loading is off if cleared mid-process
  };

  return (
    <div className="min-h-screen bg-zinc-900 text-zinc-100 flex flex-col items-center justify-center p-4 font-inter">
      <div className="bg-zinc-800 p-8 rounded-xl shadow-lg w-full max-w-2xl border border-zinc-700">
        {/* Header with icon */}
        <div className="flex items-center justify-center mb-6">
          {/* Simple gear icon for "animation" or "engine" */}
          <svg className="w-10 h-10 text-zinc-400 mr-3" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
          </svg>
          <h1 className="text-4xl font-bold text-zinc-100">
            Manim Animation Studio
          </h1>
        </div>

        {/* Input area for the user prompt */}
        <div className="mb-6">
          <label htmlFor="prompt-input" className="block text-lg font-medium text-zinc-300 mb-2">
            Describe your mathematical animation:
          </label>
          <textarea
            id="prompt-input"
            className="w-full p-3 rounded-md bg-zinc-700 text-zinc-100 border border-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-500 resize-y min-h-[120px] shadow-sm"
            placeholder="e.g., Animate the unit circle showing sine and cosine values, or Explain the derivative of x squared."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={5}
          ></textarea>
        </div>

        {/* Action buttons */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={handleSubmit}
            disabled={isLoading || prompt.trim() === ''}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-md transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin h-5 w-5 mr-3 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Generating...
              </span>
            ) : (
              'Generate Manim Animation'
            )}
          </button>
          <button
            onClick={handleClear}
            className="px-6 py-3 bg-zinc-600 hover:bg-zinc-700 text-zinc-100 font-semibold rounded-md transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-zinc-500 shadow-md"
            disabled={isLoading}
          >
            Clear
          </button>
        </div>

        {/* Error message display */}
        {error && (
          <div className="mt-6 p-3 bg-red-800 text-red-100 rounded-md border border-red-600 shadow-sm">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Video display area (Note: Video URL is not returned by current backend) */}
        {videoUrl && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-center mb-4 text-zinc-200">
              Your Animation
            </h2>
            <div className="relative w-full pb-[56.25%] rounded-lg overflow-hidden border border-zinc-700 shadow-xl"> {/* 16:9 aspect ratio */}
              <video
                src={videoUrl}
                controls
                autoPlay
                className="absolute top-0 left-0 w-full h-full object-contain bg-black" // Added bg-black for video player
                onEnded={() => console.log('Video finished playing')}
                onError={(e) => {
                  console.error('Video load error:', e);
                  setError('Failed to load video. Please try again or check the backend.');
                }}
              >
                Your browser does not support the video tag.
              </video>
            </div>
            <p className="text-center text-zinc-400 text-sm mt-3">
              (Video URL is conceptual; the current backend previews directly on the server.)
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-zinc-500 text-sm">
        <p>&copy; 2025 Manim Animation Studio. Powered by Python & AI.</p>
        <p className="mt-1">For educational and explanatory mathematical videos.</p>
      </footer>
    </div>
  );
};

export default App;
