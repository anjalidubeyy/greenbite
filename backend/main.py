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
import requests
from io import BytesIO
import gzip

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://greenbite-ashy.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
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
    print("📁 Downloading datasets...")
    
    # Download recipes dataset
    recipes_url = "https://storage.googleapis.com/greenbite-datasets/filtered_recipes_1m.csv.gz"
    print(f"📁 Downloading recipes from: {recipes_url}")
    recipes_response = requests.get(recipes_url)
    recipes_response.raise_for_status()
    
    # Load recipes dataset with memory optimization
    recipes_df = pd.read_csv(
        BytesIO(recipes_response.content),
        compression='gzip',
        usecols=['title', 'NER'],
        dtype={'title': 'string', 'NER': 'string'}
    )
    
    # Rename columns to match our code
    recipes_df = recipes_df.rename(columns={
        'title': 'Title',
        'NER': 'Cleaned_Ingredients'
    })
    
    # Download emissions dataset
    emissions_url = "https://storage.googleapis.com/greenbite-datasets/Food_Product_Emissions.csv"
    print(f"📁 Downloading emissions from: {emissions_url}")
    emissions_response = requests.get(emissions_url)
    emissions_response.raise_for_status()
    
    # Load emissions dataset
    emissions_df = pd.read_csv(BytesIO(emissions_response.content))
    
    print("✅ Successfully loaded both datasets")
    print(f"📊 Recipes dataset columns: {recipes_df.columns.tolist()}")
    print(f"📊 Emissions dataset columns: {emissions_df.columns.tolist()}")
    print(f"📊 Total recipes loaded: {len(recipes_df)}")
    
except Exception as e:
    print(f"❌ Dataset loading error: {str(e)}")
    raise

# Global variables to store the datasets
RECIPES_DATASET = recipes_df
EMISSIONS_DATASET = emissions_df

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
            print("❌ Emissions dataset not loaded!")
            return jsonify({"error": "Emissions dataset not loaded"}), 500

        matched_ingredients = match_ingredients_with_emissions(ingredients, EMISSIONS_DATASET)
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
        if EMISSIONS_DATASET is None:
            return jsonify({"error": "Emissions dataset not loaded"}), 500

        matched_ingredients = match_ingredients_with_emissions(ingredients, EMISSIONS_DATASET)
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

        # Find dishes in dataset using fuzzy matching
        try:
            print(f"🔍 Searching for dish1: {dish1_name}")
            print(f"🔍 Searching for dish2: {dish2_name}")
            
            # Get all unique titles for fuzzy matching
            all_titles = RECIPES_DATASET['Title'].unique()
            
            # Find best matches using fuzzy matching
            dish1_matches = process.extract(dish1_name.lower(), [title.lower() for title in all_titles], limit=5)
            dish2_matches = process.extract(dish2_name.lower(), [title.lower() for title in all_titles], limit=5)
            
            print(f"📊 Dish1 fuzzy matches: {dish1_matches}")
            print(f"📊 Dish2 fuzzy matches: {dish2_matches}")
            
            # Get the best match for each dish
            dish1_best_match = dish1_matches[0][0] if dish1_matches else None
            dish2_best_match = dish2_matches[0][0] if dish2_matches else None
            
            if not dish1_best_match or not dish2_best_match:
                print("❌ Could not find good matches for one or both dishes!")
                return jsonify({"error": "Could not find good matches for one or both dishes"}), 404
            
            # Find the exact matches in the dataset
            dish1_matches = RECIPES_DATASET[RECIPES_DATASET["Title"].str.lower() == dish1_best_match]
            dish2_matches = RECIPES_DATASET[RECIPES_DATASET["Title"].str.lower() == dish2_best_match]
            
            print(f"📊 Dish1 exact matches found: {len(dish1_matches)}")
            print(f"📊 Dish2 exact matches found: {len(dish2_matches)}")
            
            if len(dish1_matches) == 0 or len(dish2_matches) == 0:
                print("❌ One or both dishes not found in dataset!")
                return jsonify({"error": "One or both dishes not found"}), 404
            
            dish1 = dish1_matches.iloc[0]
            dish2 = dish2_matches.iloc[0]
            
            print(f"✅ Found dish1: {dish1['Title']}")
            print(f"✅ Found dish2: {dish2['Title']}")
            
        except IndexError:
            print("❌ One or both dishes not found in dataset!")
            return jsonify({"error": "One or both dishes not found"}), 404

        # Extract and clean ingredients
        dish1_ingredients = [ing.strip() for ing in dish1["Cleaned_Ingredients"].split(",")]
        dish2_ingredients = [ing.strip() for ing in dish2["Cleaned_Ingredients"].split(",")]

        print(f"🔍 Dish 1 ingredients: {dish1_ingredients}")
        print(f"🔍 Dish 2 ingredients: {dish2_ingredients}")

        # Match ingredients with emissions data
        dish1_matched = match_ingredients_with_emissions(dish1_ingredients, EMISSIONS_DATASET)
        dish2_matched = match_ingredients_with_emissions(dish2_ingredients, EMISSIONS_DATASET)

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
