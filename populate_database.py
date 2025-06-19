import uuid
import random
from sqlalchemy import create_engine, text
from config import Config

RECIPES_DATA = [
    {
        'name': 'Classic Margherita Pizza',
        'instructions': '1. Prepare pizza dough and let rise\n2. Roll out dough on floured surface\n3. Spread tomato sauce evenly\n4. Add fresh mozzarella and basil\n5. Bake at 475°F for 12-15 minutes',
        'time': 45,
        'steps': 5,
        'complexity': 'Intermediate',
        'cuisine': 'Italian',
        'ingredients': ['pizza dough', 'tomato sauce', 'fresh mozzarella', 'fresh basil', 'olive oil'],
        'calories': 285,
        'fat': 12.0,
        'sugar': 4.0,
        'sodium': 580.0,
        'protein': 12.0,
        'sat_fat': 6.0,
        'carbs': 32.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Savory',
        'dietary': ['Vegetarian']
    },
    {
        'name': 'Spaghetti Carbonara',
        'instructions': '1. Cook spaghetti until al dente\n2. Fry pancetta until crispy\n3. Whisk eggs with parmesan\n4. Toss hot pasta with pancetta\n5. Add egg mixture off heat, stirring quickly\n6. Season with black pepper',
        'time': 25,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'Italian',
        'ingredients': ['spaghetti', 'pancetta', 'eggs', 'parmesan cheese', 'black pepper'],
        'calories': 520,
        'fat': 22.0,
        'sugar': 2.0,
        'sodium': 890.0,
        'protein': 28.0,
        'sat_fat': 8.0,
        'carbs': 58.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Savory',
        'dietary': []
    },
    
    {
        'name': 'Chicken Teriyaki Bowl',
        'instructions': '1. Marinate chicken in teriyaki sauce\n2. Cook rice according to package directions\n3. Grill chicken until cooked through\n4. Steam broccoli and carrots\n5. Serve over rice with vegetables\n6. Drizzle with extra teriyaki sauce',
        'time': 35,
        'steps': 6,
        'complexity': 'Beginner',
        'cuisine': 'Japanese',
        'ingredients': ['chicken breast', 'teriyaki sauce', 'jasmine rice', 'broccoli', 'carrots', 'sesame seeds'],
        'calories': 420,
        'fat': 8.0,
        'sugar': 12.0,
        'sodium': 950.0,
        'protein': 35.0,
        'sat_fat': 2.0,
        'carbs': 55.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Sweet and Savory',
        'dietary': ['Gluten-Free']
    },
    {
        'name': 'Vegetable Pad Thai',
        'instructions': '1. Soak rice noodles in warm water\n2. Prepare sauce with tamarind, fish sauce, and palm sugar\n3. Heat oil in wok, scramble eggs\n4. Add drained noodles and sauce\n5. Stir in vegetables and bean sprouts\n6. Garnish with peanuts, lime, and cilantro',
        'time': 30,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'Thai',
        'ingredients': ['rice noodles', 'eggs', 'bean sprouts', 'carrots', 'bell peppers', 'peanuts', 'lime', 'cilantro'],
        'calories': 380,
        'fat': 14.0,
        'sugar': 8.0,
        'sodium': 720.0,
        'protein': 12.0,
        'sat_fat': 3.0,
        'carbs': 58.0,
        'spice': 'Medium',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Sweet and Spicy',
        'dietary': ['Vegetarian', 'Gluten-Free']
    },
    {
        'name': 'Black Bean Quesadillas',
        'instructions': '1. Mash black beans with cumin and lime\n2. Spread bean mixture on tortillas\n3. Add cheese and fold tortillas\n4. Cook in pan until crispy and cheese melts\n5. Cut into wedges\n6. Serve with salsa and sour cream',
        'time': 20,
        'steps': 6,
        'complexity': 'Beginner',
        'cuisine': 'Mexican',
        'ingredients': ['flour tortillas', 'black beans', 'monterey jack cheese', 'cumin', 'lime', 'salsa'],
        'calories': 340,
        'fat': 15.0,
        'sugar': 3.0,
        'sodium': 680.0,
        'protein': 16.0,
        'sat_fat': 8.0,
        'carbs': 38.0,
        'spice': 'Medium',
        'temp': 'Hot',
        'meal': 'Lunch',
        'course': 'Main',
        'taste': 'Savory',
        'dietary': ['Vegetarian']
    },
    {
        'name': 'Fish Tacos with Mango Salsa',
        'instructions': '1. Season fish with chili powder and lime\n2. Grill fish until flaky\n3. Dice mango, red onion, and jalapeño for salsa\n4. Warm corn tortillas\n5. Assemble tacos with fish, salsa, and cabbage\n6. Serve with lime wedges',
        'time': 25,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'Mexican',
        'ingredients': ['white fish', 'corn tortillas', 'mango', 'red onion', 'jalapeño', 'cabbage', 'lime'],
        'calories': 280,
        'fat': 6.0,
        'sugar': 12.0,
        'sodium': 420.0,
        'protein': 25.0,
        'sat_fat': 1.0,
        'carbs': 35.0,
        'spice': 'Medium',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Fresh and Spicy',
        'dietary': ['Gluten-Free', 'Dairy-Free']
    },
    {
        'name': 'Chickpea Curry (Chana Masala)',
        'instructions': '1. Soak and cook chickpeas until tender\n2. Sauté onions, garlic, and ginger\n3. Add spices and cook until fragrant\n4. Add tomatoes and cook until soft\n5. Add chickpeas and simmer\n6. Garnish with cilantro and serve with rice',
        'time': 45,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'Indian',
        'ingredients': ['chickpeas', 'onions', 'garlic', 'ginger', 'tomatoes', 'garam masala', 'cumin', 'cilantro'],
        'calories': 320,
        'fat': 8.0,
        'sugar': 12.0,
        'sodium': 580.0,
        'protein': 15.0,
        'sat_fat': 1.0,
        'carbs': 52.0,
        'spice': 'Medium',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Spicy',
        'dietary': ['Vegetarian', 'Vegan', 'Gluten-Free']
    },
    {
        'name': 'Butter Chicken',
        'instructions': '1. Marinate chicken in yogurt and spices\n2. Cook chicken in tandoor or grill\n3. Sauté onions and aromatics\n4. Add tomato puree and cream\n5. Simmer with cooked chicken\n6. Finish with butter and serve with naan',
        'time': 60,
        'steps': 6,
        'complexity': 'Advanced',
        'cuisine': 'Indian',
        'ingredients': ['chicken', 'yogurt', 'tomatoes', 'cream', 'butter', 'garam masala', 'fenugreek leaves'],
        'calories': 480,
        'fat': 28.0,
        'sugar': 8.0,
        'sodium': 720.0,
        'protein': 32.0,
        'sat_fat': 15.0,
        'carbs': 18.0,
        'spice': 'Medium',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Rich and Creamy',
        'dietary': ['Gluten-Free']
    },
    {
        'name': 'Greek Salad',
        'instructions': '1. Chop tomatoes, cucumbers, and red onion\n2. Add olives and feta cheese\n3. Whisk olive oil with lemon juice and oregano\n4. Toss vegetables with dressing\n5. Season with salt and pepper\n6. Let marinate for 10 minutes before serving',
        'time': 15,
        'steps': 6,
        'complexity': 'Beginner',
        'cuisine': 'Greek',
        'ingredients': ['tomatoes', 'cucumbers', 'red onion', 'kalamata olives', 'feta cheese', 'olive oil', 'lemon', 'oregano'],
        'calories': 220,
        'fat': 18.0,
        'sugar': 8.0,
        'sodium': 680.0,
        'protein': 6.0,
        'sat_fat': 6.0,
        'carbs': 12.0,
        'spice': 'Mild',
        'temp': 'Cold',
        'meal': 'Lunch',
        'course': 'Salad',
        'taste': 'Fresh and Tangy',
        'dietary': ['Vegetarian', 'Gluten-Free']
    },
    {
        'name': 'Moroccan Tagine',
        'instructions': '1. Brown lamb in tagine or Dutch oven\n2. Add onions, garlic, and spices\n3. Add dried fruits and broth\n4. Cover and simmer for 1.5 hours\n5. Add vegetables in last 30 minutes\n6. Serve over couscous with almonds',
        'time': 120,
        'steps': 6,
        'complexity': 'Advanced',
        'cuisine': 'Moroccan',
        'ingredients': ['lamb', 'onions', 'dried apricots', 'almonds', 'cinnamon', 'ginger', 'saffron', 'couscous'],
        'calories': 520,
        'fat': 20.0,
        'sugar': 15.0,
        'sodium': 420.0,
        'protein': 35.0,
        'sat_fat': 6.0,
        'carbs': 45.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Sweet and Savory',
        'dietary': ['Dairy-Free']
    },
    {
        'name': 'BBQ Pulled Pork Sandwich',
        'instructions': '1. Rub pork shoulder with spice blend\n2. Slow cook for 6-8 hours until tender\n3. Shred meat with forks\n4. Mix with BBQ sauce\n5. Toast brioche buns\n6. Serve with coleslaw',
        'time': 480,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'American',
        'ingredients': ['pork shoulder', 'BBQ sauce', 'brioche buns', 'coleslaw mix', 'brown sugar', 'paprika'],
        'calories': 580,
        'fat': 22.0,
        'sugar': 18.0,
        'sodium': 980.0,
        'protein': 38.0,
        'sat_fat': 8.0,
        'carbs': 52.0,
        'spice': 'Medium',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Main',
        'taste': 'Smoky and Sweet',
        'dietary': []
    },
    {
        'name': 'Quinoa Buddha Bowl',
        'instructions': '1. Cook quinoa according to package directions\n2. Roast sweet potatoes and Brussels sprouts\n3. Massage kale with lemon juice\n4. Prepare tahini dressing\n5. Arrange all ingredients in bowl\n6. Top with avocado and pumpkin seeds',
        'time': 35,
        'steps': 6,
        'complexity': 'Beginner',
        'cuisine': 'American',
        'ingredients': ['quinoa', 'sweet potatoes', 'brussels sprouts', 'kale', 'avocado', 'tahini', 'pumpkin seeds'],
        'calories': 420,
        'fat': 18.0,
        'sugar': 12.0,
        'sodium': 320.0,
        'protein': 16.0,
        'sat_fat': 3.0,
        'carbs': 55.0,
        'spice': 'Mild',
        'temp': 'Warm',
        'meal': 'Lunch',
        'course': 'Main',
        'taste': 'Fresh and Nutty',
        'dietary': ['Vegetarian', 'Vegan', 'Gluten-Free']
    },
    {
        'name': 'Classic French Onion Soup',
        'instructions': '1. Caramelize onions slowly for 45 minutes\n2. Add wine and reduce\n3. Add beef broth and simmer\n4. Ladle into oven-safe bowls\n5. Top with bread and Gruyère cheese\n6. Broil until cheese is bubbly',
        'time': 75,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'French',
        'ingredients': ['yellow onions', 'beef broth', 'dry white wine', 'French bread', 'gruyère cheese', 'butter'],
        'calories': 380,
        'fat': 18.0,
        'sugar': 12.0,
        'sodium': 890.0,
        'protein': 18.0,
        'sat_fat': 11.0,
        'carbs': 32.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Soup',
        'taste': 'Rich and Savory',
        'dietary': ['Vegetarian']
    },
    {
        'name': 'Ratatouille',
        'instructions': '1. Slice all vegetables thinly\n2. Sauté onions and garlic\n3. Add tomatoes and herbs\n4. Layer vegetables in baking dish\n5. Drizzle with olive oil\n6. Bake until tender',
        'time': 60,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'French',
        'ingredients': ['eggplant', 'zucchini', 'bell peppers', 'tomatoes', 'onions', 'garlic', 'herbs de provence'],
        'calories': 160,
        'fat': 8.0,
        'sugar': 12.0,
        'sodium': 220.0,
        'protein': 4.0,
        'sat_fat': 1.0,
        'carbs': 22.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Dinner',
        'course': 'Side',
        'taste': 'Fresh and Herbal',
        'dietary': ['Vegetarian', 'Vegan', 'Gluten-Free']
    },
    {
        'name': 'Overnight Oats with Berries',
        'instructions': '1. Mix oats with milk and chia seeds\n2. Add maple syrup and vanilla\n3. Refrigerate overnight\n4. Top with fresh berries\n5. Add chopped nuts\n6. Serve chilled',
        'time': 10,
        'steps': 6,
        'complexity': 'Beginner',
        'cuisine': 'American',
        'ingredients': ['rolled oats', 'almond milk', 'chia seeds', 'maple syrup', 'vanilla', 'mixed berries', 'walnuts'],
        'calories': 320,
        'fat': 12.0,
        'sugar': 18.0,
        'sodium': 120.0,
        'protein': 10.0,
        'sat_fat': 2.0,
        'carbs': 45.0,
        'spice': 'None',
        'temp': 'Cold',
        'meal': 'Breakfast',
        'course': 'Main',
        'taste': 'Sweet',
        'dietary': ['Vegetarian', 'Vegan', 'Gluten-Free']
    },
    {
        'name': 'Avocado Toast with Poached Egg',
        'instructions': '1. Toast sourdough bread\n2. Mash avocado with lemon and salt\n3. Bring water to simmer for poaching\n4. Crack egg into water and poach\n5. Spread avocado on toast\n6. Top with poached egg and seasoning',
        'time': 15,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'American',
        'ingredients': ['sourdough bread', 'avocado', 'eggs', 'lemon', 'red pepper flakes', 'sea salt'],
        'calories': 380,
        'fat': 22.0,
        'sugar': 3.0,
        'sodium': 480.0,
        'protein': 16.0,
        'sat_fat': 4.0,
        'carbs': 32.0,
        'spice': 'Mild',
        'temp': 'Hot',
        'meal': 'Breakfast',
        'course': 'Main',
        'taste': 'Savory',
        'dietary': ['Vegetarian']
    },
    {
        'name': 'Chocolate Chip Cookies',
        'instructions': '1. Cream butter and sugars\n2. Add eggs and vanilla\n3. Mix in flour, baking soda, and salt\n4. Fold in chocolate chips\n5. Drop onto baking sheets\n6. Bake at 375°F for 9-11 minutes',
        'time': 30,
        'steps': 6,
        'complexity': 'Beginner',
        'cuisine': 'American',
        'ingredients': ['flour', 'butter', 'brown sugar', 'white sugar', 'eggs', 'vanilla', 'chocolate chips'],
        'calories': 180,
        'fat': 8.0,
        'sugar': 15.0,
        'sodium': 140.0,
        'protein': 2.0,
        'sat_fat': 5.0,
        'carbs': 26.0,
        'spice': 'None',
        'temp': 'Room temperature',
        'meal': 'Dessert',
        'course': 'Dessert',
        'taste': 'Sweet',
        'dietary': ['Vegetarian']
    },
    {
        'name': 'Vegan Chocolate Mousse',
        'instructions': '1. Melt dark chocolate carefully\n2. Whip aquafaba until peaks form\n3. Fold melted chocolate into aquafaba\n4. Add vanilla and sweetener\n5. Chill for 2 hours\n6. Serve with fresh berries',
        'time': 140,
        'steps': 6,
        'complexity': 'Intermediate',
        'cuisine': 'French',
        'ingredients': ['dark chocolate', 'aquafaba', 'vanilla', 'maple syrup', 'berries'],
        'calories': 220,
        'fat': 14.0,
        'sugar': 20.0,
        'sodium': 25.0,
        'protein': 4.0,
        'sat_fat': 8.0,
        'carbs': 28.0,
        'spice': 'None',
        'temp': 'Cold',
        'meal': 'Dessert',
        'course': 'Dessert',
        'taste': 'Rich and Sweet',
        'dietary': ['Vegan', 'Gluten-Free']
    }
]

def get_dietary_restriction_id(conn, restriction_name):
    """Get the ID for a dietary restriction"""
    result = conn.execute(text("""
        SELECT RestrictionID FROM DietaryRestrictions 
        WHERE RestrictionName = :name
    """), {'name': restriction_name}).fetchone()
    return result[0] if result else None

def create_enhanced_sample_data(engine):
    """Create comprehensive sample data with diverse recipes"""
    
    with engine.connect() as conn:
        print("Creating enhanced sample data...")
        
        users = [
            ('chef_maria', 'maria@example.com', 'Italian cooking enthusiast'),
            ('spice_master', 'spice@example.com', 'Loves Indian and Thai cuisine'),
            ('healthy_eats', 'healthy@example.com', 'Focus on nutritious meals'),
            ('comfort_cook', 'comfort@example.com', 'Traditional American recipes'),
            ('plant_based', 'vegan@example.com', 'Vegan recipe creator')
        ]
        
        user_ids = {}
        for username, email, bio in users:
            user_id = str(uuid.uuid4())
            user_ids[username] = user_id
            conn.execute(text("""
                INSERT INTO Users (UserID, Username, Email, Password) 
                VALUES (:id, :username, :email, :password)
                ON CONFLICT (Username) DO NOTHING
            """), {
                'id': user_id,
                'username': username,
                'email': email,
                'password': f'hashed_password_{username}'
            })
        
        for i, recipe_data in enumerate(RECIPES_DATA):
            nutr_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO NutritionalInfo (NutrID, Calories, TotalFat, Sugar, Sodium, Protein, SaturatedFat, Carbs)
                VALUES (:id, :calories, :fat, :sugar, :sodium, :protein, :sat_fat, :carbs)
            """), {
                'id': nutr_id,
                'calories': recipe_data['calories'],
                'fat': recipe_data['fat'],
                'sugar': recipe_data['sugar'],
                'sodium': recipe_data['sodium'],
                'protein': recipe_data['protein'],
                'sat_fat': recipe_data['sat_fat'],
                'carbs': recipe_data['carbs']
            })
            
            flavor_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO FlavorProfiles (FlavorID, SpiceLevel, ServingTemp, MealType, CourseType, Taste)
                VALUES (:id, :spice, :temp, :meal, :course, :taste)
            """), {
                'id': flavor_id,
                'spice': recipe_data['spice'],
                'temp': recipe_data['temp'],
                'meal': recipe_data['meal'],
                'course': recipe_data['course'],
                'taste': recipe_data['taste']
            })
            
            random_user = random.choice(list(user_ids.values()))

            recipe_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO Recipes (RecipeID, RecipeName, Instructions, Time, NumSteps, NumIngredients, 
                                   Complexity, CuisineType, UserID, NutrID, FlavorID, AverageRating, NumRatings)
                VALUES (:id, :name, :instructions, :time, :steps, :ingredients, :complexity, :cuisine,
                        :user_id, :nutr_id, :flavor_id, :rating, :num_ratings)
            """), {
                'id': recipe_id,
                'name': recipe_data['name'],
                'instructions': recipe_data['instructions'],
                'time': recipe_data['time'],
                'steps': recipe_data['steps'],
                'ingredients': len(recipe_data['ingredients']),
                'complexity': recipe_data['complexity'],
                'cuisine': recipe_data['cuisine'],
                'user_id': random_user,
                'nutr_id': nutr_id,
                'flavor_id': flavor_id,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'num_ratings': random.randint(5, 50)
            })
            
            for ingredient_name in recipe_data['ingredients']:
                existing = conn.execute(text("""
                    SELECT IngredientID FROM Ingredients WHERE IngredientName = :name
                """), {'name': ingredient_name}).fetchone()
                
                if existing:
                    ingredient_id = existing[0]
                else:
                    ingredient_id = str(uuid.uuid4())
                    conn.execute(text("""
                        INSERT INTO Ingredients (IngredientID, IngredientName)
                        VALUES (:id, :name)
                    """), {'id': ingredient_id, 'name': ingredient_name})
                
                conn.execute(text("""
                    INSERT INTO Contains (RecipeID, IngredientID)
                    VALUES (:recipe_id, :ingredient_id)
                """), {'recipe_id': recipe_id, 'ingredient_id': ingredient_id})
            
            for dietary_restriction in recipe_data['dietary']:
                restriction_id = get_dietary_restriction_id(conn, dietary_restriction)
                if restriction_id:
                    conn.execute(text("""
                        INSERT INTO CompatibleWith (RecipeID, RestrictionID)
                        VALUES (:recipe_id, :restriction_id)
                    """), {'recipe_id': recipe_id, 'restriction_id': restriction_id})
            
            for _ in range(random.randint(1, 3)):
                review_id = str(uuid.uuid4())
                reviewer_id = random.choice(list(user_ids.values()))
                rating = random.randint(3, 5)
                
                comments = [
                    "Delicious and easy to make!",
                    "Great recipe, will make again.",
                    "Perfect for a weeknight dinner.",
                    "Amazing flavors, highly recommend!",
                    "Simple ingredients but fantastic results.",
                    "This has become a family favorite.",
                    "Exactly what I was looking for!"
                ]
                
                conn.execute(text("""
                    INSERT INTO Reviews (ReviewID, Rating, Comment, UserID, RecipeID)
                    VALUES (:id, :rating, :comment, :user_id, :recipe_id)
                """), {
                    'id': review_id,
                    'rating': rating,
                    'comment': random.choice(comments),
                    'user_id': reviewer_id,
                    'recipe_id': recipe_id
                })
        
        for user_id in user_ids.values():
            recipes_result = conn.execute(text("""
                SELECT RecipeID FROM Recipes WHERE UserID != :user_id
                ORDER BY RANDOM() LIMIT :limit
            """), {'user_id': user_id, 'limit': random.randint(3, 7)}).fetchall()
            
            for recipe_row in recipes_result:
                conn.execute(text("""
                    INSERT INTO Saves (UserID, RecipeID)
                    VALUES (:user_id, :recipe_id)
                """), {'user_id': user_id, 'recipe_id': recipe_row[0]})
        
        conn.commit()
        print(f"Successfully created {len(RECIPES_DATA)} diverse recipes")
        print(f"Created {len(users)} additional users")
        print("Added sample reviews and saved recipes")

def main():
    """Main function to populate database with enhanced data"""    
    engine = create_engine(Config.DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful")
        
        create_enhanced_sample_data(engine)
        
        print("\nDatabase population completed successfully.")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        print("Check your database connection and ensure tables are created first.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        engine = create_engine(Config.DATABASE_URI)