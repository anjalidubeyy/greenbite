import pandas as pd
from ingredients import extract_ingredients, load_dataset
from emissions import load_emissions_data, match_ingredients_with_emissions, calculate_total_impact

def main():
    """
    Main function to handle user input, extract ingredients, and calculate emissions.
    """
    try:
        # Load datasets
        recipes_dataset = load_dataset("C:\\greenbite\\datasets\\filtered_recipes_1m.csv.gz")  
        emissions_dataset = load_emissions_data("C:\\greenbite\\datasets\\Food_Product_Emissions.csv")  

    except FileNotFoundError as e:
        print(f"Error: {e}. Ensure the CSV files exist in the correct directory.")
        return

    # Get user input for dish name
    dish_name = input("Enter the name of your dish: ").strip().lower()

    # Extract matching recipes and ingredients
    matched_recipes, matched_titles = extract_ingredients(dish_name, recipes_dataset)

    if not matched_recipes:
        print(f"No recipes found for '{dish_name}'. Please try another dish.")
        return

    # Display only top 5 matched recipes
    print(f"\nMatched Recipes for '{dish_name}': (Top 5 Results)")
    for i, recipe in enumerate(matched_recipes[:5], start=1):
        print(f"Recipe {i}: {recipe}")

    # Ask user to select a recipe
    try:
        choice = int(input("\nSelect a recipe (enter the number): "))
        if choice < 1 or choice > min(5, len(matched_recipes)):
            print("Invalid selection. Exiting.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    # Get the selected recipe's ingredients
    selected_recipe = matched_recipes[choice - 1]
    selected_title = matched_titles[choice - 1]
    ingredients = selected_recipe.split(" - Ingredients: ")[1].strip().strip("[]").replace('"', '').split(", ")

    # Match ingredients with emissions data
    matched_ingredients = match_ingredients_with_emissions(ingredients, emissions_dataset)

    if not matched_ingredients:
        print("No environmental impact data found for the ingredients in this recipe.")
        return

    # Calculate total environmental impact
    total_impact, total_emissions = calculate_total_impact(matched_ingredients)

    # Display results
    print(f"\nEnvironmental Impact for '{selected_title}':")
    for key, value in total_impact.items():
        print(f"- {key}: {value:.2f} kg CO₂")

    print(f"\n🌍 Total Emissions for '{selected_title}': {total_emissions:.2f} kg CO₂")

if __name__ == "__main__":
    main()
