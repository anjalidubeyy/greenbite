import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./../styles/Home.css"; // Adjust this if needed

function SearchBar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      // Redirect to results page with query as a URL param
      navigate(`/results?query=${encodeURIComponent(query)}`);
    } catch (error) {
      console.error("Search error:", error);
    }
  };

  return (
    <div className="search-container">
      <input
        type="text"
        placeholder="Enter a dish..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Analyze My Dish</button>
    </div>
  );
}

export default SearchBar;
