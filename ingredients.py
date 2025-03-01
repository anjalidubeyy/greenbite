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
    "cheddar cheese": ["cheese", ["sharp cheddar"]],
    "mozzarella cheese": ["cheese", ["soft cheese"]],
    "parmesan cheese": ["cheese", ["hard cheese"]],
    "cream cheese": ["cheese", ["soft cheese"]],
    "buttermilk": ["milk", ["cultured milk"]],
    "paneer": ["cottage cheese", "Indian cheese"],
    "ghee": ["clarified butter", ["butter"]],
    "yogurt (milk, cultures)": ["yogurt", ["curd"]],
    "pizza dough": ["flour", ["bread dough"]],
    "wheat flour": ["flour", ["all-purpose flour"]],
    "basmati rice": ["rice", [["long-grain rice"]]],
    "vegetable oil": ["oil", [["canola oil"]]],
    "olive oil": ["oil", [["extra virgin olive oil"]]],
    "brown sugar": ["sugar", [["demerara sugar"]]],
    "honey syrup": ["honey"],
}

def load_dataset(file_path):
    """
    Load a dataset from a CSV file.
    """
    return pd.read_csv(file_path)

def normalize_input(dish_name):
    """
    Normalize the input dish name by converting it to lowercase and replacing synonyms.
    """
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
    # Fuzzy match to find up to 5 best matches
    matches = process.extract(dish_name, dataset["title"].values, limit=5)
    best_matches = [match[0] for match in matches if match[1] >= threshold]

    all_ingredients = []
    matched_titles = []
    
    for best_match in best_matches:
        matched_rows = dataset.loc[dataset["title"] == best_match]
        
        for _, row in matched_rows.iterrows():
            ingredients = row["NER"].split(", ")
            ingredient_entry = f"{best_match} - Ingredients: {', '.join(ingredients)}"
            all_ingredients.append(ingredient_entry)
            matched_titles.append(best_match)
    
    return all_ingredients, matched_titles
