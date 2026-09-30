"""
services/recommendation_service.py
Milestone 3: Knowledge Matrix, Strict Filter Logic, and Meal Planning.
"""
from typing import List, Dict, Any, Optional
import random

# 1. Deficiency to Key Nutrients Mapping
DEFICIENCY_TO_NUTRIENT_MAP: Dict[str, List[str]] = {
    "iron_deficiency_anemia": ["iron", "vitamin_c"],
    "vitamin_d_deficiency": ["vitamin_d", "calcium"],
    "vitamin_b12_deficiency": ["vitamin_b12", "folate"],
    "calcium_deficiency": ["calcium", "magnesium", "vitamin_d"],
    "protein_energy_malnutrition": ["protein", "zinc"],
    "general_fatigue": ["iron", "magnesium", "vitamin_b12"]
}

# 2. Food Database with Nutrient Tags, Diet Categories, and Allergens
FOOD_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "food_1",
        "name": "Spinach & Lentil Dal",
        "meal_slot": "lunch",
        "rich_in": ["iron", "folate", "protein"],
        "diet_type": ["vegan", "vegetarian"],
        "allergens": [],
        "calories": 280,
        "recipe_instructions": "Simmer yellow lentils with chopped spinach, cumin, turmeric, and garlic for 20 mins."
    },
    {
        "id": "food_2",
        "name": "Fortified Oatmeal with Chia & Almonds",
        "meal_slot": "breakfast",
        "rich_in": ["iron", "magnesium", "calcium"],
        "diet_type": ["vegan", "vegetarian"],
        "allergens": ["nuts"],
        "calories": 350,
        "recipe_instructions": "Cook oats in fortified soy/almond milk. Top with chia seeds, sliced almonds, and berries."
    },
    {
        "id": "food_3",
        "name": "Grilled Salmon with Steamed Broccoli",
        "meal_slot": "dinner",
        "rich_in": ["vitamin_d", "vitamin_b12", "protein"],
        "diet_type": ["non_vegetarian", "pescatarian"],
        "allergens": ["fish"],
        "calories": 480,
        "recipe_instructions": "Pan-sear salmon fillet with lemon and olive oil for 8 mins. Serve with steamed broccoli."
    },
    {
        "id": "food_4",
        "name": "Greek Yogurt Parfait with Pumpkin Seeds",
        "meal_slot": "snack",
        "rich_in": ["calcium", "protein", "zinc", "vitamin_b12"],
        "diet_type": ["vegetarian"],
        "allergens": ["dairy"],
        "calories": 210,
        "recipe_instructions": "Layer unsweetened Greek yogurt with roasted pumpkin seeds and honey."
    },
    {
        "id": "food_5",
        "name": "Tofu Scramble with Bell Peppers",
        "meal_slot": "breakfast",
        "rich_in": ["protein", "iron", "calcium", "vitamin_c"],
        "diet_type": ["vegan", "vegetarian"],
        "allergens": ["soy"],
        "calories": 290,
        "recipe_instructions": "Crumble firm tofu in skillet with turmeric, nutritional yeast, and diced bell peppers."
    },
    {
        "id": "food_6",
        "name": "Chickpea & Quinoa Mediterranean Bowl",
        "meal_slot": "lunch",
        "rich_in": ["protein", "iron", "magnesium", "folate"],
        "diet_type": ["vegan", "vegetarian"],
        "allergens": [],
        "calories": 420,
        "recipe_instructions": "Toss cooked quinoa, boiled chickpeas, cucumber, olive oil, and lemon juice."
    },
    {
        "id": "food_7",
        "name": "Roasted Paneer & Vegetable Skewers",
        "meal_slot": "dinner",
        "rich_in": ["calcium", "protein", "vitamin_d"],
        "diet_type": ["vegetarian"],
        "allergens": ["dairy"],
        "calories": 360,
        "recipe_instructions": "Marinate paneer cubes and veggies in yogurt spices. Bake at 200°C for 15 mins."
    },
    {
        "id": "food_8",
        "name": "Hard Boiled Eggs with Orange Slices",
        "meal_slot": "breakfast",
        "rich_in": ["vitamin_b12", "protein", "vitamin_d", "vitamin_c"],
        "diet_type": ["non_vegetarian", "eggetarian"],
        "allergens": ["egg"],
        "calories": 220,
        "recipe_instructions": "Boil 2 eggs for 9 mins. Serve with freshly sliced oranges for iron-boosting Vitamin C."
    },
    {
        "id": "food_9",
        "name": "Roasted Edamame / Spiced Roasted Chickpeas",
        "meal_slot": "snack",
        "rich_in": ["iron", "magnesium", "protein"],
        "diet_type": ["vegan", "vegetarian"],
        "allergens": ["soy"],
        "calories": 180,
        "recipe_instructions": "Air-fry cooked edamame or chickpeas with paprika and sea salt."
    },
    {
        "id": "food_10",
        "name": "Fortified Mushroom & Spinach Risotto",
        "meal_slot": "dinner",
        "rich_in": ["vitamin_d", "iron"],
        "diet_type": ["vegan", "vegetarian"],
        "allergens": [],
        "calories": 410,
        "recipe_instructions": "Sauté UV-treated mushrooms with garlic, arborio rice, and vegetable broth until creamy."
    }
]


class RecommendationEngine:
    @staticmethod
    def filter_food_pool(
        diet_preference: str,
        allergies: List[str],
        food_catalog: List[Dict[str, Any]] = FOOD_CATALOG
    ) -> List[Dict[str, Any]]:
        """Filters catalog against dietary restrictions and medical allergies."""
        safe_foods = []
        user_allergies = set(a.lower().strip() for a in allergies)

        for food in food_catalog:
            # 1. Dietary Check
            if diet_preference != "flexible" and diet_preference not in food["diet_type"]:
                continue
            
            # 2. Allergy Check (Disallow any food containing user's allergens)
            food_allergens = set(a.lower().strip() for a in food["allergens"])
            if user_allergies.intersection(food_allergens):
                continue

            safe_foods.append(food)
        return safe_foods

    @classmethod
    def get_ranked_foods(
        cls,
        detected_deficiencies: List[str],
        diet_preference: str,
        allergies: List[str]
    ) -> List[Dict[str, Any]]:
        """Scores and prioritizes foods addressing detected deficiency risks."""
        safe_pool = cls.filter_food_pool(diet_preference, allergies)
        
        # Determine target nutrients
        target_nutrients = set()
        for def_key in detected_deficiencies:
            for nut in DEFICIENCY_TO_NUTRIENT_MAP.get(def_key, []):
                target_nutrients.add(nut)

        def score_food(item: Dict[str, Any]) -> int:
            return sum(2 for nut in item["rich_in"] if nut in target_nutrients)

        # Sort descending by relevance score
        return sorted(safe_pool, key=score_food, reverse=True)

    @classmethod
    def generate_7_day_meal_plan(
        cls,
        detected_deficiencies: List[str],
        diet_preference: str,
        allergies: List[str]
    ) -> Dict[str, Any]:
        """Generates a 7-day plan (Breakfast, Lunch, Snack, Dinner) without back-to-back repeats."""
        candidate_foods = cls.get_ranked_foods(detected_deficiencies, diet_preference, allergies)
        
        slots = ["breakfast", "lunch", "snack", "dinner"]
        plan: Dict[str, Dict[str, Any]] = {}
        last_assigned: Dict[str, Optional[str]] = {s: None for s in slots}

        for day_num in range(1, 8):
            day_key = f"Day_{day_num}"
            plan[day_key] = {}

            for slot in slots:
                slot_candidates = [f for f in candidate_foods if f["meal_slot"] == slot]
                
                if not slot_candidates:
                    plan[day_key][slot] = {
                        "name": "Custom Balanced Plate",
                        "calories": 300,
                        "recipe_instructions": "Select foods consistent with dietary profile."
                    }
                    continue

                # Repetition constraint: avoid repeating previous day's exact meal if alternatives exist
                filtered = [f for f in slot_candidates if f["id"] != last_assigned[slot]]
                chosen = random.choice(filtered if filtered else slot_candidates)
                
                plan[day_key][slot] = chosen
                last_assigned[slot] = chosen["id"]

        return {
            "risk_estimate_notice": "AI Risk Estimate: Clinical decision support prototype. Not certified medical advice.",
            "detected_deficiencies": detected_deficiencies,
            "dietary_profile": {"preference": diet_preference, "allergies": allergies},
            "meal_plan": plan
        } 