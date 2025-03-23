import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/Results.css";

const Results = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const searchParams = new URLSearchParams(location.search);
    const searchQuery = searchParams.get("query") || "";

    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!searchQuery) return;

        const fetchRecipes = async () => {
            try {
                setLoading(true);
                setError(null);

                const response = await fetch("http://localhost:5000/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ dish: searchQuery }),
                });

                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }

                const data = await response.json();

                if (!data || !Array.isArray(data.recipes)) {
                    throw new Error("Invalid data format received.");
                }

                setRecipes(data.recipes);
            } catch (err) {
                setError(err.message);
                setRecipes([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRecipes();
    }, [searchQuery]);

    const handleSelectRecipe = (recipe) => {
        const selectedIngredients = recipe.ingredients
            ?.map(ing => ing.replace(/["[\]]/g, "").trim())
            .filter(Boolean) || [];

        if (selectedIngredients.length === 0) {
            setError("No valid ingredients found.");
            return;
        }

        navigate("/emissions", { state: { ingredients: selectedIngredients } });
    };

    return (
        <div className="results-container">
            <h1>Results for: {searchQuery}</h1>

            {loading ? (
                <p className="loading">Loading recipes...</p>
            ) : error ? (
                <p className="error-message">⚠ {error}</p>
            ) : recipes.length > 0 ? (
                <div className="recipe-list">
                    {recipes.map((recipe, index) => (
                        <div key={index} className="recipe-card">
                            <h3>Recipe {index + 1}</h3>
                            <p>
                                <strong>Ingredients:</strong>{" "}
                                {recipe.ingredients?.join(", ") || "No ingredients available"}
                            </p>
                            <button className="select-btn" onClick={() => handleSelectRecipe(recipe)}>
                                Select Recipe
                            </button>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="no-results">🚫 No recipes found.</p>
            )}
        </div>
    );
};

export default Results;
