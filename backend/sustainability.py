import pandas as pd
import requests
from difflib import get_close_matches
from emissions import match_ingredients_with_emissions, calculate_total_impact

# Load dataset
try:
    emissions_df = pd.read_csv("datasets/Food_Product_Emissions.csv")
    emissions_df["Food product"] = emissions_df["Food product"].str.lower().str.strip()
    print("✅ Emissions dataset loaded successfully.")
except Exception as e:
    print(f"❌ Error loading emissions dataset: {e}")
    emissions_df = None

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
    """Calculate sustainability score based on emissions data."""
    print(f"🧐 Debug: Processing ingredients → {ingredients}")  # ✅ Debug ingredient list

    try:
        # First, calculate the total emissions for the dish
        matched_ingredients = match_ingredients_with_emissions(ingredients, emissions_df)
        if not matched_ingredients:
            print("⚠ No matching ingredients found in emissions dataset!")
            return 3.0  # Default score if no matches found
            
        _, total_emissions = calculate_total_impact(matched_ingredients)
        
        print(f"📊 Debug: Total emissions for the dish → {total_emissions}")  # ✅ Debug total emissions
        
        # Calculate sustainability score based on total emissions
        # Lower total emissions = higher sustainability score
        # Scale the score to be between 1 and 5
        max_emissions = 10.0  # Assume max emissions is 10 kg CO2e
        min_emissions = 0.1   # Assume min emissions is 0.1 kg CO2e
        
        if total_emissions <= min_emissions:
            score = 5.0  # Maximum score for very low emissions
        elif total_emissions >= max_emissions:
            score = 1.0  # Minimum score for very high emissions
        else:
            # Linear scaling between min and max emissions
            score = 5.0 - ((total_emissions - min_emissions) / (max_emissions - min_emissions)) * 4.0
        
        # Ensure score is capped at 5.0 and never returns None
        score = min(5.0, float(score)) if isinstance(score, (int, float)) else 3.0
        print(f"✅ Final Sustainability Score for the Dish: {score:.2f}")
        return score
        
    except Exception as e:
        print(f"❌ Error calculating sustainability score: {str(e)}")
        return 3.0  # Default score if error occurs
