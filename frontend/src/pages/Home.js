import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaSearch } from "react-icons/fa";
import { motion } from "framer-motion";

function Home() {
  const [query, setQuery] = useState("");
  const [numPapers, setNumPapers] = useState("");
  const navigate = useNavigate();

  const handleSearch = () => {
    if (!query.trim()) return;
    navigate("/results", { state: { query, numPapers: numPapers || 5 } });
  };

  return (
    <motion.div
      className="relative flex flex-col items-center justify-center h-screen text-white"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <h1
        className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-teal-400
                     bg-clip-text text-transparent drop-shadow-lg"
      >
        Semantic Search
      </h1>
      <p className="text-lg mt-2 text-gray-400 opacity-80">
        Find research papers instantly
      </p>

      {/* Search Section */}
      <div className="relative flex flex-col sm:flex-row gap-4 mt-6 z-10">
        {/* Search Input */}
        <div
          className="flex items-center bg-white/10 backdrop-blur-xl bg-gradient-to-br
                        from-white/5 to-white/15 px-5 py-3 rounded-full border border-white/10
                        w-80 sm:w-96 shadow-lg"
        >
          <FaSearch className="text-gray-400 mr-2" />
          <input
            type="text"
            placeholder="Search topics..."
            className="bg-transparent text-white placeholder-gray-400 outline-none w-full caret-green-400"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()} // ENTER triggers search
          />
        </div>

        {/* Number of Papers Input */}
        <input
          type="number"
          min="1"
          max="50"
          placeholder="Papers"
          className="bg-white/10 backdrop-blur-xl bg-gradient-to-br from-white/5 to-white/15 px-4 py-3
                     rounded-full border border-white/10 text-white text-center outline-none
                     w-24 shadow-lg appearance-none no-spinner"
          value={numPapers}
          onChange={(e) => setNumPapers(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()} // ENTER triggers search
        />

        {/* Search Button */}
        <button
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-br from-blue-400 to-purple-400
                     text-black font-semibold rounded-full hover:scale-105 transition-all shadow-lg"
          onClick={handleSearch}
        >
          <FaSearch className="text-black text-lg" /> {/* Cute icon */}
          <span>Search</span>
        </button>
      </div>
    </motion.div>
  );
}

export default Home;
