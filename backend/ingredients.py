import pandas as pd
from thefuzz import process

# Synonym map for normalization
synonym_map = {
    "aubergine": "eggplant",
    "brinjal": "eggplant",
    "courgette": "zucchini",
    "capsicum": "bell pepper",
    "ladyfinger": "okra",
    "spring onion": "green onion",
    "beetroot": "beet",
    "cilantro": "coriander",
    "mixed vegetables": ["vegetables", "stir-fry vegetables"],
    "sweet corn": "corn",
    "yam": ["sweet potato", "taro"],
    "cauliflower": ["gobi", "flower cabbage"],
    "cabbage": ["red cabbage", "green cabbage"],
    "strawberries": "berries",
    "blueberries": "berries",
    "cheddar cheese": "cheese",
    "mozzarella cheese": "cheese",
    "parmesan cheese": "cheese",
    "paneer": ["cottage cheese", "Indian cheese"],
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
    normalized_words = [synonym_map.get(word, word) for word in words]
    return " ".join(normalized_words)

def extract_ingredients(dish_name, dataset, threshold=80):
    """
    Extract multiple recipe options and their ingredients using fuzzy matching.

    Args:
        dish_name (str): The name of the dish entered by the user.
        dataset (pd.DataFrame): Dataset containing recipes and their ingredients.
        threshold (int): Similarity score threshold for fuzzy matching.

    Returns:
        list: A list of recipe options with their ingredients.
        list: A list of matched recipe titles.
    """
    dish_name = normalize_input(dish_name)  # Apply synonym mapping before matching

    # Fuzzy match to find up to 5 best matches
    matches = process.extract(dish_name, dataset["title"].values, limit=5)
    best_matches = [match[0] for match in matches if match[1] >= threshold]

    all_ingredients = []
    matched_titles = []
    
    for best_match in best_matches:
        matched_rows = dataset.loc[dataset["title"] == best_match]
        
        for _, row in matched_rows.iterrows():
            ingredients = row["NER"].split(", ") if isinstance(row["NER"], str) else []
            if ingredients:
                all_ingredients.append(ingredients)
                matched_titles.append(best_match)

    return all_ingredients, matched_titles