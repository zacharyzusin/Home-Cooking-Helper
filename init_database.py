import uuid
from sqlalchemy import create_engine, text
from config import Config

def create_tables(engine):
    """Create all database tables"""
    
    schema_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS Users (
        UserID VARCHAR(255) PRIMARY KEY,
        Username VARCHAR(100) UNIQUE NOT NULL,
        Email VARCHAR(255) UNIQUE NOT NULL,
        Password VARCHAR(255) NOT NULL,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Nutritional Information table
    CREATE TABLE IF NOT EXISTS NutritionalInfo (
        NutrID VARCHAR(255) PRIMARY KEY,
        Calories INTEGER,
        TotalFat DECIMAL(10,2),
        Sugar DECIMAL(10,2),
        Sodium DECIMAL(10,2),
        Protein DECIMAL(10,2),
        SaturatedFat DECIMAL(10,2),
        Carbs DECIMAL(10,2)
    );

    -- Flavor Profiles table
    CREATE TABLE IF NOT EXISTS FlavorProfiles (
        FlavorID VARCHAR(255) PRIMARY KEY,
        SpiceLevel VARCHAR(50),
        ServingTemp VARCHAR(50),
        MealType VARCHAR(50),
        CourseType VARCHAR(50),
        Taste VARCHAR(100)
    );

    -- Recipes table
    CREATE TABLE IF NOT EXISTS Recipes (
        RecipeID VARCHAR(255) PRIMARY KEY,
        RecipeName VARCHAR(255) NOT NULL,
        Instructions TEXT,
        Time INTEGER,
        NumSteps INTEGER,
        NumIngredients INTEGER,
        Complexity VARCHAR(50),
        CuisineType VARCHAR(100),
        UserID VARCHAR(255) REFERENCES Users(UserID),
        NutrID VARCHAR(255) REFERENCES NutritionalInfo(NutrID),
        FlavorID VARCHAR(255) REFERENCES FlavorProfiles(FlavorID),
        AverageRating DECIMAL(3,2) DEFAULT 0,
        NumRatings INTEGER DEFAULT 0,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Ingredients table
    CREATE TABLE IF NOT EXISTS Ingredients (
        IngredientID VARCHAR(255) PRIMARY KEY,
        IngredientName VARCHAR(255) NOT NULL
    );

    -- Contains table (Recipe-Ingredient relationship)
    CREATE TABLE IF NOT EXISTS Contains (
        RecipeID VARCHAR(255) REFERENCES Recipes(RecipeID),
        IngredientID VARCHAR(255) REFERENCES Ingredients(IngredientID),
        PRIMARY KEY (RecipeID, IngredientID)
    );

    -- Dietary Restrictions table
    CREATE TABLE IF NOT EXISTS DietaryRestrictions (
        RestrictionID VARCHAR(255) PRIMARY KEY,
        RestrictionName VARCHAR(100) UNIQUE NOT NULL
    );

    -- CompatibleWith table (Recipe-DietaryRestriction relationship)
    CREATE TABLE IF NOT EXISTS CompatibleWith (
        RecipeID VARCHAR(255) REFERENCES Recipes(RecipeID),
        RestrictionID VARCHAR(255) REFERENCES DietaryRestrictions(RestrictionID),
        PRIMARY KEY (RecipeID, RestrictionID)
    );

    -- Saves table (User-Recipe saved relationship)
    CREATE TABLE IF NOT EXISTS Saves (
        UserID VARCHAR(255) REFERENCES Users(UserID),
        RecipeID VARCHAR(255) REFERENCES Recipes(RecipeID),
        SavedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (UserID, RecipeID)
    );

    -- Reviews table
    CREATE TABLE IF NOT EXISTS Reviews (
        ReviewID VARCHAR(255) PRIMARY KEY,
        Rating INTEGER CHECK (Rating >= 1 AND Rating <= 5),
        Comment TEXT,
        UserID VARCHAR(255) REFERENCES Users(UserID),
        RecipeID VARCHAR(255) REFERENCES Recipes(RecipeID),
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with engine.connect() as conn:
        for statement in schema_sql.split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
        print("Database tables created successfully")

def populate_sample_data(engine):
    """Populate database with sample data"""
    
    with engine.connect() as conn:
        dietary_restrictions = [
            ('dr1', 'Vegetarian'),
            ('dr2', 'Vegan'),
            ('dr3', 'Gluten-Free'),
            ('dr4', 'Dairy-Free'),
            ('dr5', 'Nut-Free'),
            ('dr6', 'Low-Carb'),
            ('dr7', 'Keto'),
            ('dr8', 'Paleo'),
            ('dr9', 'Low-Sodium'),
            ('dr10', 'Sugar-Free')
        ]
        
        for restriction_id, restriction_name in dietary_restrictions:
            conn.execute(text("""
                INSERT INTO DietaryRestrictions (RestrictionID, RestrictionName) 
                VALUES (:id, :name) ON CONFLICT (RestrictionName) DO NOTHING
            """), {'id': restriction_id, 'name': restriction_name})
        
        user_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO Users (UserID, Username, Email, Password) 
            VALUES (:id, :username, :email, :password)
            ON CONFLICT (Username) DO NOTHING
        """), {
            'id': user_id,
            'username': 'demo_user',
            'email': 'demo@example.com',
            'password': 'password_here'
        })
        
        nutr_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO NutritionalInfo (NutrID, Calories, TotalFat, Sugar, Sodium, Protein, SaturatedFat, Carbs)
            VALUES (:id, :calories, :fat, :sugar, :sodium, :protein, :sat_fat, :carbs)
        """), {
            'id': nutr_id,
            'calories': 350,
            'fat': 12.5,
            'sugar': 8.0,
            'sodium': 450.0,
            'protein': 25.0,
            'sat_fat': 4.0,
            'carbs': 35.0
        })
        
        flavor_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO FlavorProfiles (FlavorID, SpiceLevel, ServingTemp, MealType, CourseType, Taste)
            VALUES (:id, :spice, :temp, :meal, :course, :taste)
        """), {
            'id': flavor_id,
            'spice': 'Medium',
            'temp': 'Hot',
            'meal': 'Dinner',
            'course': 'Main',
            'taste': 'Savory'
        })
        
        recipe_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO Recipes (RecipeID, RecipeName, Instructions, Time, NumSteps, NumIngredients, 
                               Complexity, CuisineType, UserID, NutrID, FlavorID, AverageRating, NumRatings)
            VALUES (:id, :name, :instructions, :time, :steps, :ingredients, :complexity, :cuisine,
                    :user_id, :nutr_id, :flavor_id, :rating, :num_ratings)
        """), {
            'id': recipe_id,
            'name': 'Sample Pasta Dish',
            'instructions': '1. Boil water\n2. Cook pasta\n3. Add sauce\n4. Serve hot',
            'time': 30,
            'steps': 4,
            'ingredients': 3,
            'complexity': 'Beginner',
            'cuisine': 'Italian',
            'user_id': user_id,
            'nutr_id': nutr_id,
            'flavor_id': flavor_id,
            'rating': 4.5,
            'num_ratings': 10
        })
        
        ingredients = ['pasta', 'tomato sauce', 'parmesan cheese']
        for ingredient_name in ingredients:
            ingredient_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO Ingredients (IngredientID, IngredientName)
                VALUES (:id, :name)
            """), {'id': ingredient_id, 'name': ingredient_name})
            
            conn.execute(text("""
                INSERT INTO Contains (RecipeID, IngredientID)
                VALUES (:recipe_id, :ingredient_id)
            """), {'recipe_id': recipe_id, 'ingredient_id': ingredient_id})
        
        conn.commit()
        print("Sample data inserted successfully")

def create_indexes(engine):
    """Create database indexes for better performance"""
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_recipes_user ON Recipes(UserID)",
        "CREATE INDEX IF NOT EXISTS idx_recipes_cuisine ON Recipes(CuisineType)",
        "CREATE INDEX IF NOT EXISTS idx_recipes_rating ON Recipes(AverageRating)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_recipe ON Reviews(RecipeID)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_user ON Reviews(UserID)",
        "CREATE INDEX IF NOT EXISTS idx_contains_recipe ON Contains(RecipeID)",
        "CREATE INDEX IF NOT EXISTS idx_contains_ingredient ON Contains(IngredientID)",
        "CREATE INDEX IF NOT EXISTS idx_compatible_recipe ON CompatibleWith(RecipeID)",
        "CREATE INDEX IF NOT EXISTS idx_saves_user ON Saves(UserID)"
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            conn.execute(text(index_sql))
        conn.commit()
        print("Database indexes created successfully")

def main():
    """Main initialization function"""
    print("Initializing Home Cooking Helper Database...")
    
    engine = create_engine(Config.DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful")
        
        create_tables(engine)    
        populate_sample_data(engine)    
        create_indexes(engine)
        print("\ Database initialization completed successfully.")
        print("You can now run your Flask application.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Check your database connection settings in config.py")
        return False
    
    return True

if __name__ == "__main__":
    main()