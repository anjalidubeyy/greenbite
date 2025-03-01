import pandas as pd
from thefuzz import process

def load_emissions_data(file_path):
    """
    Load emissions data from a CSV file.
    """
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None

def match_ingredients_with_emissions(ingredients, emissions_dataset):
    """
    Match ingredients from the selected recipe with those in the emissions dataset.

    Args:
        ingredients (list): List of ingredients from the selected recipe.
        emissions_dataset (pd.DataFrame): Dataset containing emission information.

    Returns:
        dict: A dictionary mapping matched ingredients to their environmental impact data.
    """
    if emissions_dataset is None or "Food product" not in emissions_dataset.columns:
        print("Emissions dataset is incorrect or missing required columns.")
        return {}

    matched_ingredients = {}

    for ingredient in ingredients:
        match = process.extractOne(ingredient, emissions_dataset["Food product"].values)
        if match and match[1] >= 80:  # Threshold for fuzzy matching
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
    """
    Calculate total environmental impact based on all parameters.

    Args:
        matched_ingredients (dict): Dictionary of matched ingredients with their environmental data.

    Returns:
        dict: Total values for each parameter (e.g., Land Use Change, Feed).
        float: Total GHG emissions for the entire dish.
    """
    totals = {
        "Land Use Change": 0,
        "Feed": 0,
        "Farm": 0,
        "Processing": 0,
        "Transport": 0,
        "Packaging": 0,
        "Retail": 0,
        "Total Emissions": 0
    }
    
    for data in matched_ingredients.values():
        for key in totals.keys():
            totals[key] += data[key]
    
    return totals, totals["Total Emissions"]
