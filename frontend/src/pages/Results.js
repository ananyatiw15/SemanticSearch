import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FaFileAlt } from "react-icons/fa";
import fetchPapers from "../api";

function Results() {
  const navigate = useNavigate();
  const { state } = useLocation();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!state?.query) {
      navigate("/", { replace: true });
      return;
    }

    setResults([]); // Clear results when navigating
    const fetchResults = async () => {
      setLoading(true);
      try {
        const data = await fetchPapers(state.query, state.numPapers);
        setResults(data.results || []);
      } catch (error) {
        console.error("Error fetching data:", error);
        setResults([]);
      }
      setLoading(false);
    };

    fetchResults();
  }, [state, navigate]);

  return (
    <motion.div
      className="p-10 min-h-screen text-white bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#334155]
                 bg-opacity-80 backdrop-blur-lg"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <h2 className="text-4xl font-bold text-blue-400 mb-6">Results</h2>

      {loading ? (
        <motion.div
          className="flex items-center justify-center min-h-[60vh] bg-white/10 backdrop-blur-xl rounded-lg
                     shadow-2xl p-10 border border-white/10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="flex flex-col items-center">
            {/* Animated Loader */}
            <div className="relative w-16 h-16">
              <div className="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-75"></div>
              <div className="absolute inset-0 bg-purple-500 rounded-full animate-pulse"></div>
            </div>
            <p className="mt-4 text-xl text-gray-300">Fetching Papers...</p>
          </div>
        </motion.div>
      ) : results.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((paper, index) => (
            <motion.div
              key={index}
              className="p-6 backdrop-blur-xl bg-white/10 rounded-xl shadow-2xl border border-white/10
                         hover:scale-[1.02] transition duration-300 relative overflow-hidden"
              whileHover={{ scale: 1.05 }}
            >
              {/* Neon Border Glow */}
              <div
                className="absolute inset-0 bg-gradient-to-br from-blue-500/30 to-purple-600/20 opacity-30
                              rounded-xl pointer-events-none"
              ></div>

              {/* Paper Title */}
              <h3 className="text-xl font-semibold text-blue-300">
                {paper.title}
              </h3>

              {/* Paper Abstract or Placeholder */}
              <div className="mt-2 text-sm text-gray-300 leading-relaxed">
                <p className="font-semibold text-white mb-2">Abstract:</p>
                {paper.abstract ? (
                  <p className="text-gray-400">{paper.abstract}</p>
                ) : (
                  <div className="flex items-center text-gray-500">
                    <FaFileAlt className="mr-2 text-lg" />
                    <p>No abstract available for this paper.</p>
                  </div>
                )}
              </div>

              {/* Authors */}
              {paper.authors && (
                <p className="mt-2 text-sm text-gray-400">
                  <strong>Authors:</strong> {paper.authors}
                </p>
              )}

              {/* View Paper Button */}
              {paper.id || paper.paperid ? (
                <a
                  href={
                    paper.id ||
                    `https://www.semanticscholar.org/paper/${paper.paperid}`
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 inline-block px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500
                             text-white font-bold rounded-full hover:scale-105 transition shadow-lg"
                >
                  View Paper
                </a>
              ) : (
                <p className="mt-4 text-sm text-gray-400">
                  No direct link available
                </p>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <p className="text-center mt-10 text-red-400">No results found.</p>
      )}
    </motion.div>
  );
}

export default Results;
