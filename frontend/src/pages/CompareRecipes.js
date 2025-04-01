import React, { useState } from "react";
import axios from "axios";
import SustainabilityComparisonChart from "./components/SustainabilityComparisonChart";

const CompareRecipes = () => {
  const [recipe1, setRecipe1] = useState("");
  const [recipe2, setRecipe2] = useState("");
  const [comparison, setComparison] = useState(null);

  const compareRecipes = async () => {
    const response = await axios.post("http://localhost:5000/compare-recipes", {
      recipe1: recipe1.split(",").map((item) => item.trim()),
      recipe2: recipe2.split(",").map((item) => item.trim()),
    });
    setComparison(response.data);
  };

  return (
    <div>
      <h2>Compare Recipe Sustainability</h2>
      <input value={recipe1} onChange={(e) => setRecipe1(e.target.value)} placeholder="Recipe 1 (comma-separated)" />
      <input value={recipe2} onChange={(e) => setRecipe2(e.target.value)} placeholder="Recipe 2 (comma-separated)" />
      <button onClick={compareRecipes}>Compare</button>

      {comparison && (
        <div>
          <h3>More Sustainable: {comparison.more_sustainable}</h3>
          <SustainabilityComparisonChart data={[
            { name: "Recipe 1", score: comparison.recipe1.avg_score },
            { name: "Recipe 2", score: comparison.recipe2.avg_score },
          ]} />
        </div>
      )}
    </div>
  );
};

export default CompareRecipes;
