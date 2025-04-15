import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/Results.css";

const Results = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchQuery = searchParams.get("query") || "";

    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!searchQuery) return;

        const fetchRecipes = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/search`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query: searchQuery }), 
                });

                if (!response.ok) throw new Error(`API Error: ${response.status}`);

                const data = await response.json();
                console.log("✅ Recipe API Response:", data);

                if (!data || !Array.isArray(data.recipes)) {
                    throw new Error("Invalid data format received.");
                }

                setRecipes(data.recipes);
            } catch (err) {
                console.error("❌ Recipe API Error:", err);
                setError(err.message);
                setRecipes([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRecipes();
    }, [searchQuery]);

    const handleSelectRecipe = async (recipe) => {
        setLoading(true);
        setError(null);

        try {
            let selectedIngredients = [];

            // 🛠️ Ensure ingredients are in list format
            if (Array.isArray(recipe.ingredients)) {
                selectedIngredients = recipe.ingredients.map(ing =>
                    ing.trim().replace(/[\[\]"]/g, "")
                ).filter(Boolean);
            } else {
                try {
                    const parsedIngredients = JSON.parse(recipe.ingredients);
                    if (Array.isArray(parsedIngredients)) {
                        selectedIngredients = parsedIngredients.map(ing =>
                            ing.replace(/^"|"$/g, '').trim()
                        );
                    } else {
                        throw new Error("Parsed ingredients are not in an array format.");
                    }
                } catch (err) {
                    console.error("❌ Error parsing ingredients:", err, recipe.ingredients);
                    setError("Failed to parse ingredients.");
                    return;
                }
            }

            if (selectedIngredients.length === 0) {
                setError("No valid ingredients found.");
                return;
            }

            console.log("🔹 Cleaned Ingredients:", selectedIngredients);

            // 🚀 Fetch emissions data
            const response = await fetch(`${process.env.REACT_APP_API_URL}/emissions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ingredients: selectedIngredients }),
            });

            if (!response.ok) throw new Error(`API Error: ${response.status}`);

            const data = await response.json();
            console.log("✅ Emissions API Response:", data);

            // ✅ Ensure emissions data is valid
            if (!data || !data.breakdown) {
                throw new Error("Invalid emissions data received.");
            }

            // ⚠ Check if emissions data is missing for some ingredients
            const missingData = Object.keys(data.breakdown).filter(ingredient => data.breakdown[ingredient] === 0);
            if (missingData.length > 0) {
                console.warn(`⚠ No emissions data for: ${missingData.join(", ")}`);
                setError(`No emissions data for: ${missingData.join(", ")}`);
            }

            // 🔀 Navigate to Emissions page with data
            console.log("Recipe name being passed:", recipe.name || searchQuery || "Emissions Report"); // Debug recipe name
            navigate("/emissions", {
                state: {
                    recipeName: recipe.name || searchQuery || "Emissions Report",
                    searchQuery: searchQuery, // Pass the search query
                    emissionsData: data, // ✅ Pass complete emissions data
                    selectedIngredients, // ✅ Pass selected ingredients for debugging
                },
            });

        } catch (err) {
            console.error("❌ Emissions API Error:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
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
                            <h3>{recipe.name || `Recipe ${index + 1}`}</h3>
                            <p><strong>Ingredients:</strong> {Array.isArray(recipe.ingredients) ? recipe.ingredients.join(", ") : "No ingredients listed"}</p>
                            <button className="select-btn" onClick={() => handleSelectRecipe(recipe)}>Select Recipe</button>
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
