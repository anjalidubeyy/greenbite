import pandas as pd
from thefuzz import process

def load_emissions_data(filepath):
    """ Load emissions dataset from CSV file safely. """
    try:
        emissions_data = pd.read_csv(filepath)
        
        # Ensure required columns exist
        required_columns = {
            "Food product", "Land Use Change", "Feed", "Farm", 
            "Processing", "Transport", "Packaging", "Retail", 
            "Total from Land to Retail", "Total Global Average GHG Emissions per kg"
        }
        
        if not required_columns.issubset(emissions_data.columns):
            print(f"❌ Error: Missing required columns in emissions data.")
            return None
        
        for col in emissions_data.columns:
            if col not in ["Food product"]:
                emissions_data[col] = pd.to_numeric(emissions_data[col], errors="coerce").fillna(0)

        print(f"✅ Emissions data loaded successfully from: {filepath}")
        return emissions_data

    except Exception as e:
        print(f"❌ Error loading emissions data: {str(e)}")
        return None

def clean_ingredient(ingredient):
    """ Standardize ingredient formatting. """
    return ingredient.replace("[", "").replace("]", "").replace('"', "").strip().lower()

def match_ingredients_with_emissions(ingredients, emissions_dataset):
    """ Match ingredients with emissions dataset using fuzzy matching. """
    if emissions_dataset is None:
        print("❌ Error: Emissions dataset not loaded.")
        return {}

    if "Food product" not in emissions_dataset.columns:
        print("❌ Error: Missing 'Food product' column in dataset.")
        return {}

    print("\n📌 Checking Emissions Data Types:")
    print(emissions_dataset.dtypes)  # ✅ Debug: Check data types

    matched_ingredients = {}

    for ingredient in ingredients:
        cleaned_ingredient = clean_ingredient(ingredient)
        match = process.extractOne(cleaned_ingredient, emissions_dataset["Food product"].values)

        if match and match[1] >= 80:  # 80% confidence threshold
            matched_data = emissions_dataset.loc[emissions_dataset["Food product"] == match[0]].iloc[0]

            # ✅ Debug: Print Matched Ingredient Data
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
    print(matched_ingredients)  # ✅ Debug: Print final matched data

    return matched_ingredients

def calculate_total_impact(matched_ingredients):
    """ Calculate total environmental impact for a recipe. """
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
