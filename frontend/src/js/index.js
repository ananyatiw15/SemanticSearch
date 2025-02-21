import React, { useEffect } from "react";
import "./base.css";
import "./demo2.css";
import "./swirl.js"; // Import the live background animation script

function App() {
  useEffect(() => {
    if (window.setup) {
      window.setup(); // Ensure the background animation is initialized
    }
  }, []);

  return (
    <div className="app-container">
      <div className="content--canvas">
        {/* Live background animation will be injected here */}
      </div>
      <div className="content">
        <h1>Welcome to My React App</h1>
        <p>This is a website with a live animated background.</p>
      </div>
    </div>
  );
}

export default App;
