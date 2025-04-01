import pandas as pd
import requests
from difflib import get_close_matches

# Load dataset
try:
    emissions_df = pd.read_csv("C:/greenbite/datasets/Food_Product_Emissions.csv")
    emissions_df["Food product"] = emissions_df["Food product"].str.lower().str.strip()
    print("✅ Emissions dataset loaded successfully.")
except Exception as e:
    print(f"❌ Error loading emissions dataset: {e}")

def get_best_match(ingredient):
    """Find closest match for an ingredient in the dataset."""
    matches = get_close_matches(ingredient.lower(), emissions_df["Food product"].tolist(), n=1, cutoff=0.5)

    if matches:
        print(f"🔍 Best match for '{ingredient}': {matches[0]}")
        return matches[0]
    else:
        print(f"⚠ No close match found for '{ingredient}'")
        return None

def get_sustainability_score(ingredients):
    """Send emissions data to ML API and get sustainability scores for the entire dish."""
    print(f"🧐 Debug: Processing ingredients → {ingredients}")  # ✅ Debug ingredient list

    scores = []

    for ingredient in ingredients:
        best_match = get_best_match(ingredient)

        if not best_match:
            print(f"⚠ No match found for: {ingredient}, assigning 'N/A'")
            scores.append("N/A")
            continue

        row = emissions_df[emissions_df["Food product"] == best_match]
        
        if row.empty:
            print(f"⚠ Data missing for: {best_match}, assigning 'N/A'")
            scores.append("N/A")
            continue

        emissions_value = row["Total Global Average GHG Emissions per kg"].values[0]
        print(f"📊 Debug: Extracted emissions for '{ingredient}' → {emissions_value}")  # ✅ Debug emissions value

        # 🔥 Ensure emissions_value is a valid float
        try:
            emissions_value = float(emissions_value)
        except ValueError:
            print(f"❌ Invalid emissions value for '{ingredient}', assigning 'N/A'")
            scores.append("N/A")
            continue

        try:
            print(f"📤 Sending '{ingredient}' (Emissions: {emissions_value}) to ML API...")

            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json={"total_land_to_retail": emissions_value},
                headers={"Content-Type": "application/json"},
                timeout=5  # ✅ Prevents indefinite waits
            )
            response.raise_for_status()

            response_data = response.json()
            print(f"✅ API Response for '{ingredient}': {response_data}")  # ✅ Debug API response

            # 🔥 Ensure the response contains a valid sustainability score
            score = response_data.get("sustainability_score")
            if score is None or not isinstance(score, (int, float)):
                print(f"⚠ Invalid score received for '{ingredient}', assigning 'N/A'")
                scores.append("N/A")
            else:
                scores.append(score)

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error for '{ingredient}': {e}")
            scores.append("Error")

    print(f"🌱 Individual Sustainability Scores: {scores}")  # ✅ Debug individual scores

    # Aggregate the individual scores to get a single score for the entire dish
    valid_scores = [score for score in scores if isinstance(score, (int, float))]
    
    if valid_scores:
        dish_score = sum(valid_scores) / len(valid_scores)  # Average of the valid scores
        print(f"✅ Final Sustainability Score for the Dish: {dish_score:.2f}")
        return dish_score
    else:
        print("⚠ No valid sustainability scores, returning 'N/A'.")
        return "N/A"
