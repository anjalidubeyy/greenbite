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
        
        # Convert all columns except "Food product" to numeric
        for col in emissions_data.columns:
            if col != "Food product":
                emissions_data[col] = pd.to_numeric(emissions_data[col], errors="coerce")
                # Replace NaN values with 0
                emissions_data[col] = emissions_data[col].fillna(0)

        print(f"✅ Emissions data loaded successfully from: {filepath}")
        print(f"📊 Sample data: {emissions_data.head()}")
        return emissions_data

    except Exception as e:
        print(f"❌ Error loading emissions data: {str(e)}")
        return None

def clean_ingredient(ingredient):
    """ Standardize ingredient formatting. """
    # Remove brackets, quotes, and extra spaces
    cleaned = ingredient.replace("[", "").replace("]", "").replace('"', "").strip().lower()
    
    # Remove common suffixes and prefixes
    cleaned = cleaned.replace("whls", "").replace("adjust", "").replace("mix", "")
    
    # Remove extra spaces
    cleaned = " ".join(cleaned.split())
    
    return cleaned

def match_ingredients_with_emissions(ingredients, emissions_dataset):
    """ Match ingredients with emissions dataset using fuzzy matching. """
    if emissions_dataset is None:
        print("❌ Error: Emissions dataset not loaded.")
        return {}

    if "Food product" not in emissions_dataset.columns:
        print("❌ Error: Missing 'Food product' column in dataset.")
        return {}

    matched_ingredients = {}
    food_products = emissions_dataset["Food product"].str.lower().values

    # Expanded ingredient mappings with exact matches
    ingredient_mappings = {
        # Meats
        "hamburger": "beef (beef herd)",
        "beef": "beef (beef herd)",
        "ground beef": "beef (beef herd)",
        "steak": "beef (beef herd)",
        "chicken": "poultry meat",
        "poultry": "poultry meat",
        "pork": "pig meat",
        "bacon": "pig meat",
        "lamb": "lamb & mutton",
        "mutton": "lamb & mutton",
        
        # Dairy
        "cheese": "cheese",
        "cheddar": "cheese",
        "mozzarella": "cheese",
        "parmesan": "cheese",
        "milk": "milk",
        "cream": "milk",
        "yogurt": "milk",
        
        # Vegetables
        "onion": "onions & leeks",
        "leek": "onions & leeks",
        "tomato": "tomatoes",
        "tomato sauce": "tomatoes",
        "ketchup": "tomatoes",
        "potato": "potatoes",
        "carrot": "root vegetables",
        "beet": "root vegetables",
        "peas": "peas",
        "beans": "other pulses",
        "lentils": "other pulses",
        
        # Grains
        "rice": "rice",
        "wheat": "wheat & rye",
        "rye": "wheat & rye",
        "oats": "oatmeal",
        "rolled oats": "oatmeal",
        "barley": "barley",
        "corn": "maize",
        "maize": "maize",
        
        # Fruits
        "apple": "apples",
        "banana": "bananas",
        "orange": "citrus fruit",
        "lemon": "citrus fruit",
        "grape": "berries & grapes",
        "berry": "berries & grapes",
        
        # Other
        "egg": "eggs",
        "eggs": "eggs",
        "egg whites": "eggs",
        "egg whites whls": "eggs",
        "water": "water",
        "chili": "other vegetables",
        "chili powder": "other vegetables",
        "tabasco": "other vegetables",
        "tabasco sauce": "other vegetables",
        "onion soup": "onions & leeks",
        "onion soup mix": "onions & leeks",
        "onion soup mix adjust": "onions & leeks",
        "sugar": "beet sugar",
        "brown sugar": "beet sugar",
        "white sugar": "beet sugar",
        "coffee": "coffee",
        "chocolate": "dark chocolate",
        "cocoa": "dark chocolate"
    }

    for ingredient in ingredients:
        cleaned_ingredient = clean_ingredient(ingredient).lower()
        
        # Try mapping first
        mapped_ingredient = ingredient_mappings.get(cleaned_ingredient, cleaned_ingredient)
        
        # Try exact match first
        exact_match = None
        for product in food_products:
            if mapped_ingredient == product:
                exact_match = product
                break

        if not exact_match:
            # Try partial match
            for product in food_products:
                if mapped_ingredient in product or product in mapped_ingredient:
                    exact_match = product
                    break

        if not exact_match:
            # Try fuzzy matching with lower threshold (70%)
            match = process.extractOne(mapped_ingredient, food_products)
            if match and match[1] >= 70:
                exact_match = match[0]

        if exact_match:
            # Find the original case version of the match
            original_match = emissions_dataset.loc[emissions_dataset["Food product"].str.lower() == exact_match, "Food product"].iloc[0]
            matched_data = emissions_dataset.loc[emissions_dataset["Food product"] == original_match].iloc[0]
            
            # Store the matched ingredient with its emissions data
            matched_ingredients[ingredient] = {
                "Land Use Change": float(matched_data.get("Land Use Change", 0) or 0),
                "Feed": float(matched_data.get("Feed", 0) or 0),
                "Farm": float(matched_data.get("Farm", 0) or 0),
                "Processing": float(matched_data.get("Processing", 0) or 0),
                "Transport": float(matched_data.get("Transport", 0) or 0),
                "Packaging": float(matched_data.get("Packaging", 0) or 0),
                "Retail": float(matched_data.get("Retail", 0) or 0),
                "Total from Land to Retail": float(matched_data.get("Total from Land to Retail", 0) or 0),
                "Total Global Average GHG Emissions per kg": float(matched_data.get("Total Global Average GHG Emissions per kg", 0) or 0)
            }
            
            print(f"✅ Matched '{ingredient}' to '{original_match}' with emissions: {matched_ingredients[ingredient]['Total Global Average GHG Emissions per kg']}")
        else:
            print(f"❌ No match found for ingredient: {ingredient}")
            # Add default values for unmatched ingredients
            matched_ingredients[ingredient] = {
                "Land Use Change": 0,
                "Feed": 0,
                "Farm": 0,
                "Processing": 0,
                "Transport": 0,
                "Packaging": 0,
                "Retail": 0,
                "Total from Land to Retail": 0,
                "Total Global Average GHG Emissions per kg": 0
            }

    return matched_ingredients

def calculate_total_impact(matched_ingredients):
    """ Calculate total emissions impact from matched ingredients. """
    if not matched_ingredients:
        return {}, 0.0

    totals = {
        "Land Use Change": 0.0,
        "Feed": 0.0,
        "Farm": 0.0,
        "Processing": 0.0,
        "Transport": 0.0,
        "Packaging": 0.0,
        "Retail": 0.0,
        "Total from Land to Retail": 0.0
    }

    # Sum up emissions for each category
    for ingredient_data in matched_ingredients.values():
        for category in totals:
            try:
                value = float(ingredient_data.get(category, 0) or 0)
                totals[category] += value
            except (ValueError, TypeError):
                print(f"⚠ Warning: Invalid value for {category} in ingredient data")
                continue

    # Calculate total emissions using the correct column
    total_emissions = totals["Total from Land to Retail"]
    
    print(f"📊 Total emissions calculated: {total_emissions}")
    return totals, total_emissions

def calculate_emissions_equivalence(total_emissions):
    """
    Calculate real-life equivalence for the total emissions value.
    
    Conversion rates:
    1 kg CO₂e ≈ 
    • 4.5 km driven by a car  
    • 122 smartphone charges  
    • 20 plastic bags  
    • 10 hours of LED bulb usage
    """
    if not isinstance(total_emissions, (int, float)) or total_emissions <= 0:
        return {
            "car_distance": 0,
            "smartphone_charges": 0,
            "plastic_bags": 0,
            "led_bulb_hours": 0
        }
    
    # Calculate equivalences using the correct conversion rates
    car_distance = total_emissions * 4.5  # km
    smartphone_charges = total_emissions * 122
    plastic_bags = total_emissions * 20
    led_bulb_hours = total_emissions * 10
    
    return {
        "car_distance": round(car_distance, 1),
        "smartphone_charges": round(smartphone_charges, 0),
        "plastic_bags": round(plastic_bags, 0),
        "led_bulb_hours": round(led_bulb_hours, 0)
    }

def calculate_sustainability_score(total_emissions):
    """ Calculate sustainability score based on total emissions. """
    if total_emissions is None or total_emissions == 0:
        return 5.0  # Perfect score for no emissions
    
    # Convert to float and handle any potential string values
    try:
        total_emissions = float(total_emissions)
    except (ValueError, TypeError):
        print(f"⚠️ Warning: Invalid total_emissions value: {total_emissions}")
        return 3.0  # Default to middle score if invalid
    
    print(f"📊 Calculating score for emissions: {total_emissions} kg CO2")
    
    # Define emission ranges and corresponding scores
    # Lower emissions = higher score
    if total_emissions <= 1.0:
        score = 5.0  # Very low emissions (mostly plant-based)
    elif total_emissions <= 3.0:
        score = 4.5  # Low emissions (vegetarian)
    elif total_emissions <= 6.0:
        score = 4.0  # Moderate-low emissions (some dairy/eggs)
    elif total_emissions <= 10.0:
        score = 3.5  # Moderate emissions (poultry/fish)
    elif total_emissions <= 15.0:
        score = 3.0  # Moderate-high emissions (pork)
    elif total_emissions <= 25.0:
        score = 2.5  # High emissions (beef/lamb)
    elif total_emissions <= 40.0:
        score = 2.0  # Very high emissions (multiple high-emission ingredients)
    else:
        score = 1.0  # Extremely high emissions (multiple servings of high-emission ingredients)
    
    print(f"⭐ Calculated sustainability score: {score}")
    return score
