import os
import requests
import json
from django.conf import settings
from groq import Groq

# Hardcoded accurate nutrition database for common ingredients (per 100g)
NUTRITION_DB = {
    # Vegetables
    "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9, "fiber": 1.2, "sodium": 5, "sugar": 2.6, "cholesterol": 0, "saturated_fat": 0},
    "onion": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9.3, "fiber": 1.7, "sodium": 4, "sugar": 4.2, "cholesterol": 0, "saturated_fat": 0},
    "potato": {"calories": 77, "protein": 2.0, "fat": 0.1, "carbs": 17.5, "fiber": 2.2, "sodium": 6, "sugar": 0.8, "cholesterol": 0, "saturated_fat": 0},
    "capsicum": {"calories": 31, "protein": 1.0, "fat": 0.3, "carbs": 6.0, "fiber": 2.1, "sodium": 4, "sugar": 2.4, "cholesterol": 0, "saturated_fat": 0},
    "carrot": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 9.6, "fiber": 2.8, "sodium": 69, "sugar": 4.7, "cholesterol": 0, "saturated_fat": 0},
    "spinach": {"calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6, "fiber": 2.2, "sodium": 79, "sugar": 0.4, "cholesterol": 0, "saturated_fat": 0},
    "peas": {"calories": 81, "protein": 5.4, "fat": 0.4, "carbs": 14.5, "fiber": 5.1, "sodium": 5, "sugar": 5.7, "cholesterol": 0, "saturated_fat": 0},
    "ginger": {"calories": 80, "protein": 1.8, "fat": 0.8, "carbs": 18.0, "fiber": 2.0, "sodium": 13, "sugar": 1.7, "cholesterol": 0, "saturated_fat": 0},
    "garlic": {"calories": 149, "protein": 6.4, "fat": 0.5, "carbs": 33.1, "fiber": 2.1, "sodium": 17, "sugar": 1.0, "cholesterol": 0, "saturated_fat": 0},
    "green chilli": {"calories": 40, "protein": 2.0, "fat": 0.2, "carbs": 9.5, "fiber": 1.5, "sodium": 7, "sugar": 5.0, "cholesterol": 0, "saturated_fat": 0},
    "cauliflower": {"calories": 25, "protein": 1.9, "fat": 0.3, "carbs": 5.0, "fiber": 2.0, "sodium": 30, "sugar": 1.9, "cholesterol": 0, "saturated_fat": 0},
    "brinjal": {"calories": 25, "protein": 1.0, "fat": 0.2, "carbs": 5.9, "fiber": 3.0, "sodium": 2, "sugar": 3.5, "cholesterol": 0, "saturated_fat": 0},
    "cucumber": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6, "fiber": 0.5, "sodium": 2, "sugar": 1.7, "cholesterol": 0, "saturated_fat": 0},
    "beetroot": {"calories": 43, "protein": 1.6, "fat": 0.2, "carbs": 10.0, "fiber": 2.8, "sodium": 78, "sugar": 6.8, "cholesterol": 0, "saturated_fat": 0},
    "corn": {"calories": 86, "protein": 3.3, "fat": 1.4, "carbs": 19.0, "fiber": 2.7, "sodium": 15, "sugar": 6.3, "cholesterol": 0, "saturated_fat": 0},
    "mushroom": {"calories": 22, "protein": 3.1, "fat": 0.3, "carbs": 3.3, "fiber": 1.0, "sodium": 5, "sugar": 1.9, "cholesterol": 0, "saturated_fat": 0},

    # Proteins
    "egg": {"calories": 155, "protein": 13.0, "fat": 11.0, "carbs": 1.1, "fiber": 0, "sodium": 124, "sugar": 1.1, "cholesterol": 373, "saturated_fat": 3.3},
    "chicken": {"calories": 165, "protein": 31.0, "fat": 3.6, "carbs": 0, "fiber": 0, "sodium": 74, "sugar": 0, "cholesterol": 85, "saturated_fat": 1.0},
    "mutton": {"calories": 294, "protein": 25.6, "fat": 21.0, "carbs": 0, "fiber": 0, "sodium": 72, "sugar": 0, "cholesterol": 97, "saturated_fat": 9.2},
    "fish": {"calories": 136, "protein": 20.0, "fat": 6.0, "carbs": 0, "fiber": 0, "sodium": 54, "sugar": 0, "cholesterol": 50, "saturated_fat": 1.5},
    "paneer": {"calories": 265, "protein": 18.3, "fat": 20.8, "carbs": 1.2, "fiber": 0, "sodium": 28, "sugar": 1.2, "cholesterol": 60, "saturated_fat": 13.5},
    "tofu": {"calories": 76, "protein": 8.0, "fat": 4.8, "carbs": 1.9, "fiber": 0.3, "sodium": 7, "sugar": 0.6, "cholesterol": 0, "saturated_fat": 0.7},

    # Dairy
    "milk": {"calories": 61, "protein": 3.2, "fat": 3.3, "carbs": 4.8, "fiber": 0, "sodium": 44, "sugar": 5.1, "cholesterol": 10, "saturated_fat": 1.9},
    "curd": {"calories": 98, "protein": 3.5, "fat": 4.3, "carbs": 3.4, "fiber": 0, "sodium": 46, "sugar": 4.7, "cholesterol": 13, "saturated_fat": 2.7},
    "butter": {"calories": 717, "protein": 0.9, "fat": 81.1, "carbs": 0.1, "fiber": 0, "sodium": 643, "sugar": 0.1, "cholesterol": 215, "saturated_fat": 51.4},
    "ghee": {"calories": 900, "protein": 0, "fat": 99.9, "carbs": 0, "fiber": 0, "sodium": 2, "sugar": 0, "cholesterol": 256, "saturated_fat": 60.0},
    "cream": {"calories": 340, "protein": 2.1, "fat": 36.0, "carbs": 2.9, "fiber": 0, "sodium": 38, "sugar": 2.9, "cholesterol": 110, "saturated_fat": 21.0},

    # Grains
    "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28.2, "fiber": 0.4, "sodium": 1, "sugar": 0.1, "cholesterol": 0, "saturated_fat": 0},
    "wheat flour": {"calories": 340, "protein": 13.0, "fat": 2.5, "carbs": 72.0, "fiber": 10.7, "sodium": 2, "sugar": 0.4, "cholesterol": 0, "saturated_fat": 0.4},
    "dal": {"calories": 116, "protein": 9.0, "fat": 0.4, "carbs": 20.6, "fiber": 8.0, "sodium": 2, "sugar": 0.9, "cholesterol": 0, "saturated_fat": 0},
    "chickpeas": {"calories": 164, "protein": 8.9, "fat": 2.6, "carbs": 27.4, "fiber": 7.6, "sodium": 24, "sugar": 4.8, "cholesterol": 0, "saturated_fat": 0.3},
    "oats": {"calories": 389, "protein": 17.0, "fat": 7.0, "carbs": 66.0, "fiber": 10.6, "sodium": 2, "sugar": 0.9, "cholesterol": 0, "saturated_fat": 1.2},
    "bread": {"calories": 265, "protein": 9.0, "fat": 3.2, "carbs": 49.0, "fiber": 2.7, "sodium": 491, "sugar": 5.0, "cholesterol": 0, "saturated_fat": 0.7},

    # Oils & Condiments
    "oil": {"calories": 884, "protein": 0, "fat": 100.0, "carbs": 0, "fiber": 0, "sodium": 0, "sugar": 0, "cholesterol": 0, "saturated_fat": 14.0},
    "olive oil": {"calories": 884, "protein": 0, "fat": 100.0, "carbs": 0, "fiber": 0, "sodium": 0, "sugar": 0, "cholesterol": 0, "saturated_fat": 14.0},
    "coconut oil": {"calories": 862, "protein": 0, "fat": 100.0, "carbs": 0, "fiber": 0, "sodium": 0, "sugar": 0, "cholesterol": 0, "saturated_fat": 87.0},
    "salt": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "sodium": 38758, "sugar": 0, "cholesterol": 0, "saturated_fat": 0},
    "sugar": {"calories": 387, "protein": 0, "fat": 0, "carbs": 100.0, "fiber": 0, "sodium": 1, "sugar": 100.0, "cholesterol": 0, "saturated_fat": 0},
    "honey": {"calories": 304, "protein": 0.3, "fat": 0, "carbs": 82.4, "fiber": 0.2, "sodium": 4, "sugar": 82.1, "cholesterol": 0, "saturated_fat": 0},

    # Spices (per 1 tsp = ~3g, show 0 for spices)
    "turmeric": {"calories": 9, "protein": 0.3, "fat": 0.1, "carbs": 1.4, "fiber": 0.5, "sodium": 1, "sugar": 0.1, "cholesterol": 0, "saturated_fat": 0},
    "cumin": {"calories": 8, "protein": 0.4, "fat": 0.5, "carbs": 0.9, "fiber": 0.2, "sodium": 3, "sugar": 0, "cholesterol": 0, "saturated_fat": 0},
    "coriander": {"calories": 5, "protein": 0.4, "fat": 0.3, "carbs": 0.6, "fiber": 0.7, "sodium": 2, "sugar": 0, "cholesterol": 0, "saturated_fat": 0},
    "chilli powder": {"calories": 8, "protein": 0.4, "fat": 0.4, "carbs": 1.4, "fiber": 0.7, "sodium": 1, "sugar": 0, "cholesterol": 0, "saturated_fat": 0},
    "garam masala": {"calories": 8, "protein": 0.3, "fat": 0.4, "carbs": 1.2, "fiber": 0.5, "sodium": 2, "sugar": 0, "cholesterol": 0, "saturated_fat": 0},
}

def convert_to_grams(ingredient_name, quantity_str):
    quantity_str = str(quantity_str).lower().strip()
    ingredient_name = str(ingredient_name).lower().strip()
    
    # Direct gram mentions
    if 'g' in quantity_str or 'gram' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) if num_str else 100.0
        except ValueError:
            pass
            
    if 'kg' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 1000 if num_str else 1000.0
        except ValueError:
            pass
    
    # Spoons
    if 'tbsp' in quantity_str or 'tablespoon' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 15 if num_str else 15.0
        except ValueError:
            pass
            
    if 'tsp' in quantity_str or 'teaspoon' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 5 if num_str else 5.0
        except ValueError:
            pass

    # Cups
    if 'cup' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 200 if num_str else 200.0
        except ValueError:
            pass

    # Eggs specifically
    if 'egg' in ingredient_name:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 50 if num_str else 50.0
        except ValueError:
            pass

    # Medium/Large/Small sizes
    if 'medium' in quantity_str:
        size_map = {
            'onion': 110, 'tomato': 100, 'potato': 150,
            'carrot': 80, 'capsicum': 120, 'lemon': 60
        }
        for key, grams in size_map.items():
            if key in ingredient_name:
                return float(grams)
        return 100.0

    if 'large' in quantity_str:
        return 150.0
    if 'small' in quantity_str:
        return 70.0

    # Pinch/dash (spices)
    if 'pinch' in quantity_str or 'dash' in quantity_str or 'to taste' in quantity_str:
        return 3.0

    # Slices
    if 'slice' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 30 if num_str else 30.0
        except ValueError:
            pass

    # Cloves
    if 'clove' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 3.0 if num_str else 3.0
        except ValueError:
            pass

    # Pieces / inch
    if 'inch' in quantity_str or 'piece' in quantity_str:
        num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
        try:
            return float(num_str) * 5.0 if num_str else 5.0
        except ValueError:
            pass

    # Specific small items when no unit is given (just a number)
    num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
    if num_str:
        try:
            qty_num = float(num_str)
            if 'chilli' in ingredient_name or 'chili' in ingredient_name:
                return qty_num * 3.0
            if 'garlic' in ingredient_name:
                return qty_num * 3.0
            if 'ginger' in ingredient_name:
                return qty_num * 5.0
            if 'lemon' in ingredient_name or 'lime' in ingredient_name:
                return qty_num * 50.0
        except ValueError:
            pass

    # If all parsing fails, try to just grab any number
    num_str = ''.join(c for c in quantity_str if c.isdigit() or c == '.')
    try:
        if num_str:
            return float(num_str) * 100.0  # assume 100g chunks if just a number
    except ValueError:
        pass

    # Default
    return 100.0


def calculate_nutrition(ingredient_name, quantity_str):
    grams = convert_to_grams(ingredient_name, quantity_str)
    
    # Find ingredient in database
    ing_lower = str(ingredient_name).lower().strip()
    nutrition_per_100g = None
    
    # Exact or substring match in DB keys
    for key in NUTRITION_DB:
        if key in ing_lower or ing_lower in key:
            nutrition_per_100g = NUTRITION_DB[key]
            break
            
    # Also check if it matches in the quantity string (e.g. quantity is "1 tomato")
    if not nutrition_per_100g:
        q_lower = str(quantity_str).lower().strip()
        for key in NUTRITION_DB:
            if key in q_lower:
                nutrition_per_100g = NUTRITION_DB[key]
                break
    
    if not nutrition_per_100g:
        # Unknown ingredient - return zeros
        return {
            "calories": 0.0, "protein": 0.0, "fat": 0.0,
            "carbs": 0.0, "fiber": 0.0, "sodium": 0.0,
            "sugar": 0.0, "cholesterol": 0.0, "saturated_fat": 0.0,
            "grams": grams, "found": False
        }
    
    multiplier = grams / 100.0
    return {
        "calories": round(nutrition_per_100g.get("calories", 0) * multiplier, 1),
        "protein": round(nutrition_per_100g.get("protein", 0) * multiplier, 1),
        "fat": round(nutrition_per_100g.get("fat", 0) * multiplier, 1),
        "carbs": round(nutrition_per_100g.get("carbs", 0) * multiplier, 1),
        "fiber": round(nutrition_per_100g.get("fiber", 0) * multiplier, 1),
        "sodium": round(nutrition_per_100g.get("sodium", 0) * multiplier, 1),
        "sugar": round(nutrition_per_100g.get("sugar", 0) * multiplier, 1),
        "cholesterol": round(nutrition_per_100g.get("cholesterol", 0) * multiplier, 1),
        "saturated_fat": round(nutrition_per_100g.get("saturated_fat", 0) * multiplier, 1),
        "grams": round(grams, 1),
        "found": True
    }
