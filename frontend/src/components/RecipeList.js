import React from "react";
import { useNavigate } from "react-router-dom";
import "./../styles/RecipeList.css";

const RecipeList = ({ recipes = [] }) => {
  const navigate = useNavigate();

  if (!Array.isArray(recipes) || recipes.length === 0) {
    return <p className="error-message">No recipes found. Please try another search.</p>;
  }

  return (
    <div className="recipe-list">
      {recipes.map((recipe, index) => (
        <div key={index} className="recipe-card">
          <h3 className="recipe-title">{recipe.name}</h3>
          <p className="recipe-ingredients">
            Ingredients: {recipe.ingredients?.join(", ") || "No ingredients available"}
          </p>
          <button
            className="select-recipe-button"
            onClick={() => navigate("/emissions", { state: { ingredients: recipe.ingredients } })}
          >
            Select Recipe
          </button>
        </div>
      ))}
    </div>
  );
};

export default RecipeList;
