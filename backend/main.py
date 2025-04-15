from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
import os
from thefuzz import process
from ingredients import extract_ingredients, load_dataset
from emissions import load_emissions_data, match_ingredients_with_emissions, calculate_total_impact, calculate_emissions_equivalence, calculate_sustainability_score
from sustainability import get_sustainability_score
from sustainability_comparison import compare_sustainability
from google.cloud import storage
import tempfile

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://greenbite-ashy.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://greenbite-ashy.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}")

# Load datasets with error handling
try:
    # Get the absolute path to the datasets directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(os.path.dirname(current_dir), 'datasets')
    
    # Load datasets from local files with memory optimization
    recipes_path = os.path.join(datasets_dir, 'filtered_recipes_1m.csv.gz')
    emissions_path = os.path.join(datasets_dir, 'Food_Product_Emissions.csv')
    
    # Load only necessary columns from recipes dataset
    recipes_df = pd.read_csv(
        recipes_path,
        compression='gzip',
        usecols=['Title', 'Cleaned_Ingredients'],  # Only load columns we need
        nrows=100000  # Limit to first 100k rows for testing
    )
    
    # Load emissions dataset
    emissions_df = pd.read_csv(emissions_path)
    
    print("✅ Successfully loaded both datasets with memory optimization")
except Exception as e:
    print(f"❌ Dataset loading error: {str(e)}")
    raise

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
        if recipes_df is None:
            return jsonify({"error": "Recipes dataset not loaded"}), 500

        extracted_ingredients, matched_titles = extract_ingredients(query, recipes_df)
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
        if emissions_df is None:
            print("❌ Emissions dataset not loaded!")
            return jsonify({"error": "Emissions dataset not loaded"}), 500

        matched_ingredients = match_ingredients_with_emissions(ingredients, emissions_df)
        if not matched_ingredients:
            print("⚠ No matching ingredients found in emissions dataset!")
            return jsonify({"breakdown": {}, "total_emissions": 0}), 200  

        print(f"🔍 Matched Ingredients: {matched_ingredients}")

        # Calculate total impact
        total_impact, total_emissions = calculate_total_impact(matched_ingredients)
        print(f"📊 Total Impact: {total_impact}, Total Emissions: {total_emissions}")

        # Calculate emissions equivalence
        emissions_equivalence_data = calculate_emissions_equivalence(total_emissions)
        print(f"📊 Emissions Equivalence Data: {emissions_equivalence_data}")

        response = {
            "breakdown": {key: round(value, 3) for key, value in total_impact.items()},
            "total_emissions": round(total_emissions, 2),
            "emissions_equivalence": emissions_equivalence_data
        }

        print("📌 Computed Emissions Data:", response)
        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Emissions error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """Calculate sustainability metrics for a single dish."""
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
            return jsonify({
                "sustainability_score": 3.0,
                "total_emissions": 0,
                "emissions_equivalence": calculate_emissions_equivalence(0),
                "breakdown": {}
            }), 200

        print(f"✅ Ingredients received: {ingredients}")

        # Match ingredients with emissions data
        if emissions_df is None:
            return jsonify({"error": "Emissions dataset not loaded"}), 500

        matched_ingredients = match_ingredients_with_emissions(ingredients, emissions_df)
        if not matched_ingredients:
            print("⚠ No matching ingredients found in emissions dataset!")
            return jsonify({
                "sustainability_score": 3.0,
                "total_emissions": 0,
                "emissions_equivalence": calculate_emissions_equivalence(0),
                "breakdown": {}
            }), 200

        print(f"🔍 Matched Ingredients: {matched_ingredients}")

        # Calculate total impact
        total_impact, total_emissions = calculate_total_impact(matched_ingredients)
        print(f"📊 Total Impact: {total_impact}, Total Emissions: {total_emissions}")

        # Calculate emissions equivalence
        emissions_equivalence_data = calculate_emissions_equivalence(total_emissions)
        print(f"📊 Emissions Equivalence Data: {emissions_equivalence_data}")

        # Calculate sustainability score based on total emissions
        sustainability_score = calculate_sustainability_score(total_emissions)
        print(f"📈 Sustainability Score: {sustainability_score}")

        response = {
            "sustainability_score": sustainability_score,
            "total_emissions": round(total_emissions, 2),
            "emissions_equivalence": emissions_equivalence_data,
            "breakdown": {key: round(value, 3) for key, value in total_impact.items()}
        }

        print("📌 Final Response:", response)
        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Predict error: {str(e)}")
        return jsonify({"error": str(e)}), 500

from sustainability import get_sustainability_score  # Import your existing function

@app.route("/compare-dishes", methods=["POST"])
def compare_dishes():
    """ Compare two dishes based on their environmental impact. """
    try:
        data = request.get_json()
        print(f"🔥 Raw request data: {request.data}")  # Debug request data
        print(f"🔥 Parsed JSON: {data}")  # Debug parsed JSON

        if not data or "dish1" not in data or "dish2" not in data:
            print("❌ Invalid request format!")
            return jsonify({"error": "Invalid request format"}), 400

        # Extract dish names
        dish1_name = data["dish1"]
        dish2_name = data["dish2"]

        print(f"✅ Comparing dishes: {dish1_name} vs {dish2_name}")

        # Find dishes in dataset
        try:
            dish1 = recipes_df[recipes_df["Title"].str.lower() == dish1_name.lower()].iloc[0]
            dish2 = recipes_df[recipes_df["Title"].str.lower() == dish2_name.lower()].iloc[0]
        except IndexError:
            print("❌ One or both dishes not found in dataset!")
            return jsonify({"error": "One or both dishes not found"}), 404

        # Extract and clean ingredients
        dish1_ingredients = [ing.strip() for ing in dish1["Cleaned_Ingredients"].split(",")]
        dish2_ingredients = [ing.strip() for ing in dish2["Cleaned_Ingredients"].split(",")]

        print(f"🔍 Dish 1 ingredients: {dish1_ingredients}")
        print(f"🔍 Dish 2 ingredients: {dish2_ingredients}")

        # Match ingredients with emissions data
        dish1_matched = match_ingredients_with_emissions(dish1_ingredients, emissions_df)
        dish2_matched = match_ingredients_with_emissions(dish2_ingredients, emissions_df)

        print(f"📊 Dish 1 matched emissions: {dish1_matched}")
        print(f"📊 Dish 2 matched emissions: {dish2_matched}")

        # Calculate total emissions
        dish1_impact, dish1_total = calculate_total_impact(dish1_matched)
        dish2_impact, dish2_total = calculate_total_impact(dish2_matched)

        print(f"📈 Dish 1 total emissions: {dish1_total}")
        print(f"📈 Dish 2 total emissions: {dish2_total}")

        # Calculate sustainability scores
        dish1_score = get_sustainability_score(dish1_ingredients)
        dish2_score = get_sustainability_score(dish2_ingredients)
        
        # Cap scores at 5.0
        dish1_score = min(5.0, float(dish1_score)) if isinstance(dish1_score, (int, float)) else 3.0
        dish2_score = min(5.0, float(dish2_score)) if isinstance(dish2_score, (int, float)) else 3.0

        print(f"⭐ Dish 1 sustainability score: {dish1_score}")
        print(f"⭐ Dish 2 sustainability score: {dish2_score}")

        # Prepare detailed results
        result = {
            "dish1": {
                "title": dish1["Title"],
                "ingredients": dish1_ingredients,
                "ingredient_emissions": dish1_matched,
                "sustainability_score": dish1_score,
                "total_emissions": round(dish1_total, 2),
                "emissions_breakdown": {key: round(value, 3) for key, value in dish1_impact.items()},
                "emissions_equivalence": calculate_emissions_equivalence(dish1_total)
            },
            "dish2": {
                "title": dish2["Title"],
                "ingredients": dish2_ingredients,
                "ingredient_emissions": dish2_matched,
                "sustainability_score": dish2_score,
                "total_emissions": round(dish2_total, 2),
                "emissions_breakdown": {key: round(value, 3) for key, value in dish2_impact.items()},
                "emissions_equivalence": calculate_emissions_equivalence(dish2_total)
            },
            "comparison_result": {
                "more_eco_friendly": dish1["Title"] if dish1_score > dish2_score else dish2["Title"],
                "score_difference": round(abs(dish1_score - dish2_score), 2),
                "emissions_difference": round(abs(dish1_total - dish2_total), 2)
            }
        }

        print("📌 Final comparison result:", result)
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Error comparing dishes: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
