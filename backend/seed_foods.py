import csv
import json
from pathlib import Path
from app.config import DATA_DIR
from app.database import SessionLocal
from app.models.nutrition import Food


def seed_food_catalogue():
    csv_file = Path(DATA_DIR) / "foods.csv"
    if not csv_file.exists():
        print(f"File not found: {csv_file}")
        return

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Food).count() > 0:
            print("Foods already present in database. Skipping seed.")
            return

        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                food = Food(
                    name=row["name"],
                    category=row["category"],
                    serving_description=row["serving_description"],
                    serving_grams=float(row["serving_grams"]),
                    calories=float(row["calories"]),
                    protein_g=float(row["protein_g"]),
                    carbs_g=float(row["carbs_g"]),
                    fat_g=float(row["fat_g"]),
                    fiber_g=float(row["fiber_g"]),
                    iron_mg=float(row["iron_mg"]),
                    calcium_mg=float(row["calcium_mg"]),
                    vitamin_d_mcg=float(row["vitamin_d_mcg"]),
                    vitamin_b12_mcg=float(row["vitamin_b12_mcg"]),
                    vitamin_c_mg=float(row["vitamin_c_mg"]),
                    is_vegetarian=row["is_vegetarian"].lower() == "true",
                    is_vegan=row["is_vegan"].lower() == "true",
                    is_gluten_free=row["is_gluten_free"].lower() == "true",
                    is_dairy_free=row["is_dairy_free"].lower() == "true",
                    suitable_meals=json.loads(row["suitable_meals"]),
                    tags=json.loads(row["tags"]),
                )
                db.add(food)
        db.commit()
        print("Successfully seeded food catalogue into database.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding foods: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_food_catalogue()