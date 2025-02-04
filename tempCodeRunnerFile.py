import pandas as pd
from thefuzz import process

def load_dataset(file_path):        #reading the indgredients dataset
    return pd.read_csv(file_path)

synonym_map = {         #providing a synonym map for the indgredient names
    # **Vegetables**
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

    # **Fruits**
    "mixed berries": ["berries", ["strawberries", "blueberries"]],
    "strawberries": "berries",
    "blueberries": "berries",
    "citrus fruit": ["orange", "lemon", "lime"],
    "grapefruit": "citrus fruit",
    "tamarind pulp": ["tamarind", "imli"],
    "watermelon": ["melon", "citrullus"],

    # **Dairy Products**
    "cheddar cheese": ["cheese", ["sharp cheddar"]],
    "mozzarella cheese": ["cheese", ["soft cheese"]],
    "parmesan cheese": ["cheese", ["hard cheese"]],
    "cream cheese": ["cheese", ["soft cheese"]],
    "buttermilk": ["milk", ["cultured milk"]],
    "paneer": ["cottage cheese", "Indian cheese"],
    "ghee": ["clarified butter", ["butter"]],
    "yogurt (milk, cultures)": ["yogurt", ["curd"]],

    # **Meats and Seafood**
    "chicken breast": ["chicken", ["poultry"]],
    "grilled chicken": ["chicken", ["poultry"]],
    "lamb/chicken": ["lamb", ["chicken"]],
    "salmon fillet": ["salmon", ["fish"]],
    "fish (salmon, tuna)": ["fish", [["salmon", "tuna"]]],
    "prawns": ["shrimp", ["shellfish"]],

    # **Grains and Flours**
    "pizza dough": ["flour", ["bread dough"]],
    "wheat flour": ["flour", ["all-purpose flour"]],
    "basmati rice": ["rice", [["long-grain rice"]]],
    
    # **Oils and Fats**
    "vegetable oil": ["oil", [["canola oil"]]],
    "olive oil": ["oil", [["extra virgin olive oil"]]],
    
    # **Sweeteners**
    "brown sugar": ["sugar", [["demerara sugar"]]],
    "honey syrup": ["honey"],

   # **Herbs and Spices**
   # Herbs
   'oregano': ['oregano leaves', 'wild marjoram'],
   'basil': ['sweet basil', 'holy basil', 'Thai basil', 'lemon basil'],
   'parsley': ['flat-leaf parsley', 'curly parsley'],
   'mint': ['peppermint', 'spearmint'],
   'thyme': ['common thyme', 'lemon thyme'],
   'rosemary': ['pine rosemary'],
   'dill': ['dill weed', 'dill herb'],
   'chives': ['green onion tops', 'scallion tops'],
   'tarragon': ['French tarragon'],
   'sage': ['common sage', 'garden sage'],
   'bay leaf': ['laurel leaf', 'Indian bay leaf'],
   'lemongrass': ['citronella grass'],
   'fenugreek': ['methi leaves'],
   
   # Spices
   'black pepper': ['peppercorns'],
   'cinnamon': ['cassia', 'true cinnamon', 'Ceylon cinnamon'],
   'clove': ['cloves'],
   'cardamom': ['green cardamom', 'black cardamom'],
   'nutmeg': ['mace (outer covering)'],
   'star anise': ['anise star'],
   'cumin': ['jeera'],
   'turmeric': ['haldi'],
   'paprika': ['sweet paprika', 'smoked paprika'],
   'chili powder': ['red chili powder', 'cayenne pepper powder'],
   'mustard seed': ['yellow mustard seed', 'black mustard seed'],

   # Blended Spices
   'garam masala': ['Indian spice mix'],
   'curry powder': ['spice blend for curries'],

   # Miscellaneous
   'ginger': ['fresh ginger root', 'ground ginger'],
   'saffron': ['kesar', 'zafran']
}

def normalize_input(dish_name,synonym_map):     #normalising the input values to lowercase for easier processing and finding their synonyms if applicable 
    words=dish_name.lower().split()
    normalized_words=[synonym_map.get(word,word) for word in words]
    return " ".join(normalized_words)

def extract_ingredients(dish_name,dataset,threshold=80):
    
    #if the exact name of the dish is present in the dataset
    if dish_name in dataset["title"].values:
        return dataset.loc[dataset["title"]==dish_name,"NER"].tolist()
    
    #using fuzzy logic 
    matches=process.extract(dish_name,dataset["title"].values,limit=1) #find the best match of the dish 
    best_match,score=matches[0] #extracts the dish name and the score 
    
    if score>=threshold:
        return dataset.loc[dataset["title"]==best_match,"NER"].tolist() #if score is gteater than the threshold value then return the list of the ingredients for the dish 
    
    return [] #if no match is found return an empty list 

def main():
    file_path="C:\\greenbite\\datasets\\filtered_recipes_1m.csv"
    dataset=load_dataset(file_path)
    
    user_input=input("Enter the name of your dish")
    
    normalized_input=normalize_input(user_input,synonym_map)
    
    ingredients=extract_ingredients(normalized_input,dataset)
    
    if ingredients:
        print(f"Ingredients for '{user_input}':{','.join(ingredients)}")
    else:
        print(f"Sorry! no ingredients found for '{user_input}.")
        
if __name__=="__main__":
    main()
        
        
    
    
    
    
    
    