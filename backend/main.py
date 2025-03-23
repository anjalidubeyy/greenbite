from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from ingredients import extract_ingredients, load_dataset
from emissions import load_emissions_data, match_ingredients_with_emissions, calculate_total_impact

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load datasets once
RECIPES_DATASET = load_dataset("C:\\greenbite\\datasets\\filtered_recipes_1m.csv.gz")
EMISSIONS_DATASET = load_emissions_data("C:\\greenbite\\datasets\\Food_Product_Emissions.csv")

@app.route("/search", methods=["POST"])  
def search():
    try:
        dish_name = request.json.get("dish")

        if not dish_name:
            return jsonify({"error": "No dish name provided"}), 400

        print(f"🔍 Searching for: {dish_name}")  

        matched_recipes, matched_titles = extract_ingredients(dish_name, RECIPES_DATASET)

        if not matched_recipes or not any(matched_recipes):
            return jsonify({"recipes": []}), 200  

        formatted_recipes = [
            {
                "title": matched_titles[i] if i < len(matched_titles) else "Untitled Recipe",
                "ingredients": matched_recipes[i] if isinstance(matched_recipes[i], list) else []
            }
            for i in range(min(5, len(matched_recipes)))
        ]

        return jsonify({"recipes": formatted_recipes}), 200  

    except Exception as e:
        print(f"❌ Search error: {str(e)}")  
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@app.route("/emissions", methods=["POST"])
def emissions():
    try:
        data = request.get_json()
        print(f"🔥 Received request data: {data}")  

        ingredients = data.get("ingredients")

        if not ingredients or not isinstance(ingredients, list):
            return jsonify({"error": "No valid ingredients provided"}), 400

        print(f"✅ Ingredients received: {ingredients}")

        matched_ingredients = match_ingredients_with_emissions(ingredients, EMISSIONS_DATASET)

        if not matched_ingredients:
            return jsonify({"breakdown": {}, "total_emissions": 0}), 200  

        total_impact, total_emissions = calculate_total_impact(matched_ingredients)

        response = {
            "breakdown": {key: round(value, 3) for key, value in total_impact.items()},
            "total_emissions": round(total_emissions, 2)
        }

        print("📌 Computed Emissions Data:", response)  

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Emissions error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
