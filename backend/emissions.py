import pandas as pd
from thefuzz import process

def load_emissions_data(filepath):
    """ Load emissions dataset from CSV file. """
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"❌ Error loading emissions data: {str(e)}")
        return None

def clean_ingredient(ingredient):
    """ Standardize ingredient formatting. """
    return ingredient.replace("[", "").replace("]", "").replace('"', "").strip().lower()

def match_ingredients_with_emissions(ingredients, emissions_dataset):
    """ Match ingredients with emissions dataset using fuzzy matching. """
    if emissions_dataset is None or "Food product" not in emissions_dataset.columns:
        print("❌ Error: Emissions dataset missing or incorrect format.")
        return {}

    matched_ingredients = {}

    for ingredient in ingredients:
        cleaned_ingredient = clean_ingredient(ingredient)
        match = process.extractOne(cleaned_ingredient, emissions_dataset["Food product"].values)

        if match and match[1] >= 80:  # 80% confidence threshold
            matched_data = emissions_dataset.loc[emissions_dataset["Food product"] == match[0]].iloc[0]
            matched_ingredients[match[0]] = {
                "Land Use Change": matched_data["Land Use Change"],
                "Feed": matched_data["Feed"],
                "Farm": matched_data["Farm"],
                "Processing": matched_data["Processing"],
                "Transport": matched_data["Transport"],
                "Packaging": matched_data["Packaging"],
                "Retail": matched_data["Retail"],
                "Total Emissions": matched_data["Total Global Average GHG Emissions per kg"]
            }

    return matched_ingredients

def calculate_total_impact(matched_ingredients):
    """ Calculate total environmental impact for a recipe. """
    totals = {
        "Land Use Change": 0, "Feed": 0, "Farm": 0, "Processing": 0,
        "Transport": 0, "Packaging": 0, "Retail": 0, "Total Emissions": 0
    }

    if not matched_ingredients:
        return totals, 0  # Return valid response even if no matches found

    for data in matched_ingredients.values():
        for key in totals.keys():
            totals[key] += data[key]

    return totals, totals["Total Emissions"]
