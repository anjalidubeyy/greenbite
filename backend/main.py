from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
from ingredients import extract_ingredients, load_dataset
from emissions import load_emissions_data, match_ingredients_with_emissions, calculate_total_impact
from sustainability import get_sustainability_score  # Only use this for sustainability score

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

@app.before_request
def handle_preflight_requests():
    if request.method == "OPTIONS":
        response = jsonify({"message": "Preflight request handled"})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200

# Load datasets with error handling
try:
    RECIPES_DATASET = load_dataset("C:/greenbite/datasets/filtered_recipes_1m.csv.gz")
    EMISSIONS_DATASET = load_emissions_data("C:/greenbite/datasets/Food_Product_Emissions.csv")
    print("✅ Datasets loaded successfully!")
except Exception as e:
    print(f"❌ Dataset loading error: {e}")
    RECIPES_DATASET, EMISSIONS_DATASET = None, None  # Gracefully handle loading failures

@app.route("/search", methods=["POST"])
def search():
    """Extract ingredients from the query and find matching recipes."""
    try:
        print(f"🔥 Raw request data: {request.data}")  # Debug request data
        data = request.get_json(silent=True)
        print(f"🔥 Parsed JSON: {data}")  # Debug parsed JSON

        if not data or "query" not in data or not isinstance(data["query"], str):
            print("❌ Invalid request format received!")
            return jsonify({"error": "Invalid request format"}), 400

        query = data["query"].strip()
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        print(f"✅ Query received: {query}")

        # Extract ingredients using `ingredients.py`
        if RECIPES_DATASET is None:
            return jsonify({"error": "Recipes dataset not loaded"}), 500

        extracted_ingredients, matched_titles = extract_ingredients(query, RECIPES_DATASET)
        print(f"🔍 Extracted Ingredients: {extracted_ingredients}")
        print(f"📌 Matched Titles: {matched_titles}")

        if not extracted_ingredients:
            return jsonify({"error": "No ingredients recognized"}), 400

        # Clean the extracted ingredients
        cleaned_ingredients = []
        for ingredients in extracted_ingredients:
            # Remove unnecessary quotes, brackets, and any non-alphanumeric characters
            cleaned = re.sub(r'[^\w\s,]', '', str(ingredients))  # Clean unwanted characters
            cleaned = cleaned.replace('"', '').replace('[', '').replace(']', '')  # Clean extra quotes and brackets
            cleaned_ingredients.append([ingredient.strip() for ingredient in cleaned.split(',')])

        # Combine cleaned ingredients with matched titles
        response = [
            {"title": title, "ingredients": ingredients}
            for title, ingredients in zip(matched_titles, cleaned_ingredients)
        ]

        return jsonify({"recipes": response}), 200

    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/emissions", methods=["POST"])
def emissions():
    """Calculate emissions breakdown and total emissions for given ingredients."""
    try:
        print(f"🔥 Raw request data: {request.data}")  # Debug request data
        data = request.get_json(silent=True)
        print(f"🔥 Parsed JSON: {data}")  # Debug parsed JSON

        if not data or "ingredients" not in data or not isinstance(data["ingredients"], list):
            print("❌ Invalid request format!")
            return jsonify({"error": "Invalid request format"}), 400

        ingredients = [ing.strip() for ing in data["ingredients"] if isinstance(ing, str) and ing.strip()]

        if not ingredients:
            print("⚠ No valid ingredients found!")
            return jsonify({"breakdown": {}, "total_emissions": 0}), 200  

        print(f"✅ Ingredients received: {ingredients}")

        # Match ingredients with emissions data
        if EMISSIONS_DATASET is None:
            return jsonify({"error": "Emissions dataset not loaded"}), 500

        matched_ingredients = match_ingredients_with_emissions(ingredients, EMISSIONS_DATASET)
        if not matched_ingredients:
            print("⚠ No matching ingredients found in emissions dataset!")
            return jsonify({"breakdown": {}, "total_emissions": 0}), 200  

        print(f"🔍 Matched Ingredients: {matched_ingredients}")

        # Calculate emissions impact
        total_impact, total_emissions = calculate_total_impact(matched_ingredients)
        print(f"📊 Total Impact: {total_impact}, Total Emissions: {total_emissions}")

        response = {
            "breakdown": {key: round(value, 3) for key, value in total_impact.items()},
            "total_emissions": round(total_emissions, 2)
        }

        print("📌 Computed Emissions Data:", response)
        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Emissions error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """Predict sustainability score based on given ingredients."""
    try:
        print(f"🔥 Raw request data: {request.data}")  # Debug request data
        data = request.get_json(silent=True)
        print(f"🔥 Parsed JSON: {data}")  # Debug parsed JSON

        if not data or "ingredients" not in data or not isinstance(data["ingredients"], list):
            print("❌ Invalid request format!")
            return jsonify({"error": "Invalid request format"}), 400

        ingredients = [ing.strip() for ing in data["ingredients"] if isinstance(ing, str) and ing.strip()]

        if not ingredients:
            print("⚠ No valid ingredients found!")
            return jsonify({"sustainability_score": "N/A"}), 200  

        print(f"✅ Ingredients received: {ingredients}")

        # Get sustainability score from sustainability.py
        sustainability_score = get_sustainability_score(ingredients)  # Get sustainability score

        print(f"📈 Sustainability Score: {sustainability_score}")

        response = {
            "sustainability_score": sustainability_score
        }

        print("📌 Computed Sustainability Score:", response)
        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Predict error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
