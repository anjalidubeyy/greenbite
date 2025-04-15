from thefuzz import process
from sustainability import get_sustainability_score

# Clean ingredient (standardize formatting)
def clean_ingredient(ingredient):
    """Standardize ingredient formatting."""
    return ingredient.replace("[", "").replace("]", "").replace('"', "").strip().lower()

# Fuzzy matching of ingredients with emissions dataset
def match_ingredients_with_emissions(ingredients, emissions_dataset):
    """Match ingredients with emissions dataset using fuzzy matching."""
    if emissions_dataset is None:
        print("❌ Error: Emissions dataset not loaded.")
        return {}

    if "Food product" not in emissions_dataset.columns:
        print("❌ Error: Missing 'Food product' column in dataset.")
        return {}

    print("\n📌 Checking Emissions Data Types:")
    print(emissions_dataset.dtypes)  # Debug: Check data types

    matched_ingredients = {}

    for ingredient in ingredients:
        cleaned_ingredient = clean_ingredient(ingredient)
        match = process.extractOne(cleaned_ingredient, emissions_dataset["Food product"].values)

        if match and match[1] >= 80:  # 80% confidence threshold
            matched_data = emissions_dataset.loc[emissions_dataset["Food product"] == match[0]].iloc[0]

            # Debug: Print Matched Ingredient Data
            print(f"\n🔍 Matched '{ingredient}' to '{match[0]}'")
            print(matched_data.to_dict())  

            matched_ingredients[match[0]] = {
                key: float(matched_data.get(key, 0) or 0) for key in [
                    "Land Use Change", "Feed", "Farm", "Processing", "Transport", 
                    "Packaging", "Retail", "Total from Land to Retail", 
                    "Total Global Average GHG Emissions per kg"
                ]
            }
            
        else:
            print(f"❌ No match found for ingredient: {ingredient}")

    print("\n📌 Final Matched Ingredients Data:")
    print(matched_ingredients)  # Debug: Print final matched data

    return matched_ingredients

# Calculate total environmental impact for a recipe
def calculate_total_impact(matched_ingredients):
    """Calculate total environmental impact for a recipe."""
    totals = {
        "Land Use Change": 0, "Feed": 0, "Farm": 0, "Processing": 0,
        "Transport": 0, "Packaging": 0, "Retail": 0, 
        "Total from Land to Retail": 0,  
        "Total Global Average GHG Emissions per kg": 0,
        "Total Emissions": 0
    }

    if not matched_ingredients:
        print("⚠ No matched ingredients found, returning zero totals.")
        return totals, 0  

    for ingredient, data in matched_ingredients.items():
        print(f"\n🔹 Processing: {ingredient}")  
        for key in totals.keys():
            value = data.get(key, 0) or 0  
            try:
                float_value = float(value)  
                print(f"  ✅ {key}: {float_value} (Before sum)")
                totals[key] += float_value  
                print(f"  🔄 Running Total {key}: {totals[key]}")  

            except ValueError:
                print(f"❌ ERROR: '{key}' value is invalid: {value} (Type: {type(value)})")
                continue  

    totals["Total Emissions"] = sum([ 
        totals["Land Use Change"], totals["Feed"], totals["Farm"], totals["Processing"],
        totals["Transport"], totals["Packaging"], totals["Retail"], 
        totals["Total from Land to Retail"],  
        totals["Total Global Average GHG Emissions per kg"]
    ])

    print(f"\n✅ Final Total Emissions: {totals['Total Emissions']:.2f} kg CO₂e")
    
    return totals, totals["Total Emissions"]

# Compare sustainability scores of two dishes
def compare_sustainability(dish_1, dish_2, emissions_data):
    """Compare sustainability scores of two dishes based on their sustainability scores."""

    # Match ingredients for dish 1
    matched_ingredients_1 = match_ingredients_with_emissions(dish_1['ingredients'], emissions_data)
    total_impact_1, total_emissions_1 = calculate_total_impact(matched_ingredients_1)

    # Match ingredients for dish 2
    matched_ingredients_2 = match_ingredients_with_emissions(dish_2['ingredients'], emissions_data)
    total_impact_2, total_emissions_2 = calculate_total_impact(matched_ingredients_2)

    # Calculate sustainability score for dish 1
    sustainability_score_1 = get_sustainability_score(dish_1['ingredients'])  # Use the existing logic for this

    # Calculate sustainability score for dish 2
    sustainability_score_2 = get_sustainability_score(dish_2['ingredients'])  # Use the existing logic for this

    # Compare sustainability scores based on the calculated scores
    comparison_result = ""
    if sustainability_score_1 > sustainability_score_2:
        comparison_result = f"Dish 1 is more sustainable (Sustainability Score: {sustainability_score_1})."
    elif sustainability_score_1 < sustainability_score_2:
        comparison_result = f"Dish 2 is more sustainable (Sustainability Score: {sustainability_score_2})."
    else:
        comparison_result = f"Both dishes have the same sustainability score (Sustainability Score: {sustainability_score_1})."

    # Return the full response including the sustainability score for both dishes
    return {
        "dish_1": {
            "title": dish_1['title'],
            "total_emissions": total_emissions_1,
            "sustainability_score": sustainability_score_1  # Include sustainability score
        },
        "dish_2": {
            "title": dish_2['title'],
            "total_emissions": total_emissions_2,
            "sustainability_score": sustainability_score_2  # Include sustainability score
        },
        "comparison_result": comparison_result
    }
