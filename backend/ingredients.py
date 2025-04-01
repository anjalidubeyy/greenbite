import pandas as pd
from thefuzz import process
import re

# Synonym map for normalization
synonym_map = {
    "aubergine": "eggplant", "brinjal": "eggplant",
    "courgette": "zucchini", "capsicum": "bell pepper",
    "ladyfinger": "okra", "spring onion": "green onion",
    "beetroot": "beet", "cilantro": "coriander",
    "mixed vegetables": ["vegetables", "stir-fry vegetables"],
    "sweet corn": "corn", "yam": ["sweet potato", "taro"],
    "cauliflower": ["gobi", "flower cabbage"],
    "cabbage": ["red cabbage", "green cabbage"],
    "cheddar cheese": "cheese", "mozzarella cheese": "cheese",
    "parmesan cheese": "cheese", "paneer": ["cottage cheese", "Indian cheese"],
    "ghee": ["clarified butter", "butter"],
    "yogurt (milk, cultures)": ["yogurt", "curd"],
    "chicken breast": ["chicken", "poultry"],
    "salmon fillet": ["salmon", "fish"],
    "prawns": ["shrimp", "shellfish"],
    "wheat flour": ["flour", "all-purpose flour"],
    "olive oil": ["oil", "extra virgin olive oil"],
    "black pepper": ["peppercorns"],
    "cinnamon": ["cassia", "Ceylon cinnamon"],
    "turmeric": ["haldi"],
    "chili powder": ["red chili powder", "cayenne pepper powder"],
    "garam masala": ["Indian spice mix"],
}

def load_dataset(file_path):
    """Load a dataset from a CSV file."""
    return pd.read_csv(file_path)

def normalize_input(dish_name):
    """Normalize input dish name using synonyms."""
    words = dish_name.lower().split()
    normalized_words = []

    # Normalize each word based on synonym map
    for word in words:
        normalized_word = word
        # Check if word has a synonym in the map and replace it
        for key, values in synonym_map.items():
            if word in [key] + (values if isinstance(values, list) else [values]):
                normalized_word = key
                break
        normalized_words.append(normalized_word)

    return " ".join(normalized_words)

def extract_ingredients(dish_name, dataset, threshold=80):
    """Extract multiple recipe options and their ingredients using fuzzy matching."""
    dish_name = normalize_input(dish_name)

    # Fuzzy matching
    matches = process.extract(dish_name, dataset["title"].values, limit=5)
    best_matches = [match[0] for match in matches if match[1] >= threshold]

    all_ingredients = []
    matched_titles = []

    for best_match in best_matches:
        matched_rows = dataset.loc[dataset["title"] == best_match]

        for _, row in matched_rows.iterrows():
            ingredients = row["NER"]  # Assuming NER column contains the ingredients
            if isinstance(ingredients, str) and ingredients:
                # Clean ingredients
                ingredients = re.sub(r'[^\w\s,]', '', ingredients)  # Remove special characters
                cleaned_ingredients = [ingredient.strip().lower() for ingredient in ingredients.split(',')]

                all_ingredients.append(cleaned_ingredients)
                matched_titles.append(best_match)

    return all_ingredients, matched_titles
