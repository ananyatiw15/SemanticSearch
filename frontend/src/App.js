import React, { useState, useEffect } from "react";
import { FaSearch } from "react-icons/fa";
import { IoMdArrowForward } from "react-icons/io"; // Enter arrow icon
import "./css/base.css";
import "./css/demo2.css";
import "./App.css";
import "./js/swirl.js"; // Import live background animation

function App() {
  const [query, setQuery] = useState("");
  const [numPapers, setNumPapers] = useState(""); // Default is EMPTY now
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Ensure the live background animation starts
  useEffect(() => {
    setTimeout(() => {
      if (window.setup) {
        window.setup(); // Initialize swirl background
      }
    }, 500); // Small delay to ensure proper rendering
  }, []);

  // Handle search request (POST API call)
  const handleSearch = async () => {
    if (!query.trim() || !numPapers.trim()) {
      setError("Please enter a search term and the number of papers.");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]); // Clear old results before new request

    try {
      const response = await fetch("http://18.191.173.194:8080/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query, k: parseInt(numPapers) }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log("API Response:", data); // Debugging: Check API response format

      setResults(data.results || []);
    } catch (err) {
      setError("Failed to fetch results. Please try again.");
      setResults([]);
    }

    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* Live Background Canvas */}
      <div className="content--canvas"></div>

      {/* Project Title */}
      <div className="title-container">
        <h1 className="highlight-text">SemanticSearch</h1>
        <h2 className="subtitle">A Research Assistant</h2>
      </div>

      {/* Search Bar and Number Input */}
      <div className="input-container">
        {/* Search Input */}
        <div className="search-container animate-search">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search any paper or type any topic"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()} // Trigger search on Enter
          />
        </div>

        {/* Number of Papers Input */}
        <div className="num-papers-container">
          <input
            type="number"
            min="1"
            max="50"
            placeholder="Number of Papers"
            value={numPapers}
            onChange={(e) => setNumPapers(e.target.value)}
          />
          <button onClick={handleSearch}>
            <IoMdArrowForward /> {/* Enter Arrow Icon */}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && <p className="error">{error}</p>}

      {/* Results Container */}
      <div className="results-container">
        {loading ? (
          <p className="loading">Loading...</p>
        ) : (
          results.length > 0 ? (
            results.map((paper, index) => (
              <div key={index} className="result-item">
                <h2>{paper.title}</h2>
                {paper.abstract && <p><strong>Abstract:</strong> {paper.abstract}</p>}
                <p><strong>Authors:</strong> {paper.authors}</p>
              </div>
            ))
          ) : (
            !loading && <p className="no-results">No results found.</p>
          )
        )}
      </div>
    </div>
  );
}

export default App;
