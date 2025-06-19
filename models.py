from sqlalchemy import text
from flask import g
from database import get_db_connection
import uuid

class UserModel:
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        query = text("SELECT * FROM Users WHERE userid = :userid")
        return g.conn.execute(query, {'userid': user_id}).fetchone()
    
    @staticmethod
    def get_user_by_credentials(username_or_email, password):
        """Authenticate user"""
        query = text("""
            SELECT * FROM Users 
            WHERE (Username = :username_or_email OR Email = :username_or_email) 
            AND Password = :password
        """)
        params = {'username_or_email': username_or_email, 'password': password}
        
        with get_db_connection() as conn:
            return conn.execute(query, params).fetchone()
    
    @staticmethod
    def check_user_exists(username, email):
        """Check if username or email already exists"""
        query = text("SELECT COUNT(*) FROM Users WHERE username = :username OR email = :email")
        with get_db_connection() as conn:
            result = conn.execute(query, {'username': username, 'email': email}).fetchone()
            return result[0] > 0
    
    @staticmethod
    def create_user(username, email, password):
        """Create a new user"""
        query = text("INSERT INTO Users (UserID, Username, Email, Password) VALUES (:userid, :username, :email, :password)")
        userid = str(uuid.uuid1())
        params = {'userid': userid, 'username': username, 'email': email, 'password': password}
        
        with get_db_connection() as conn:
            conn.execute(query, params)
            conn.commit()
        return userid

class RecipeModel:
    @staticmethod
    def get_recipe_by_id(recipe_id):
        """Get recipe by ID"""
        query = text("SELECT * FROM Recipes WHERE RecipeID = :recipe_id")
        return g.conn.execute(query, {"recipe_id": recipe_id}).fetchone()
    
    @staticmethod
    def get_recipe_ingredients(recipe_id):
        """Get ingredients for a recipe"""
        query = text("""
            SELECT Ingredients.IngredientName FROM Ingredients 
            JOIN Contains ON Ingredients.IngredientID = Contains.IngredientID 
            WHERE Contains.RecipeID = :recipe_id
        """)
        ingredients = g.conn.execute(query, {'recipe_id': recipe_id}).fetchall()
        return [ingredient[0] for ingredient in ingredients]
    
    @staticmethod
    def get_recipe_dietary_restrictions(recipe_id):
        """Get dietary restrictions for a recipe"""
        query = text("""
            SELECT DietaryRestrictions.RestrictionName FROM DietaryRestrictions 
            JOIN CompatibleWith ON DietaryRestrictions.RestrictionID = CompatibleWith.RestrictionID 
            WHERE CompatibleWith.RecipeID = :recipe_id
        """)
        drs = g.conn.execute(query, {'recipe_id': recipe_id}).fetchall()
        return [dr[0] for dr in drs]
    
    @staticmethod
    def get_recipe_author(recipe_id):
        """Get recipe author username"""
        query = text("""
            SELECT U.Username FROM Users U, Recipes R
            WHERE R.RecipeID = :recipe_id AND U.UserID = R.UserID
        """)
        user = g.conn.execute(query, {'recipe_id': recipe_id}).fetchone()
        return user[0].strip("'").title() if user else "Unknown"
    
    @staticmethod
    def get_recipe_nutrition(recipe_id):
        """Get nutritional information for a recipe"""
        query = text("""
            SELECT N.* FROM NutritionalInfo N, Recipes R
            WHERE R.RecipeID = :recipe_id AND N.NutrID = R.NutrID
        """)
        nutr = g.conn.execute(query, {'recipe_id': recipe_id}).fetchone()
        if nutr:
            nutr_dict = nutr._asdict()
            nutr_dict.pop('nutrid', None)
            return nutr_dict
        return {}
    
    @staticmethod
    def get_recipe_flavor_profile(recipe_id):
        """Get flavor profile for a recipe"""
        query = text("""
            SELECT F.* FROM FlavorProfiles F, Recipes R
            WHERE R.RecipeID = :recipe_id AND F.FlavorID = R.FlavorID
        """)
        flav = g.conn.execute(query, {'recipe_id': recipe_id}).fetchone()
        if flav:
            flav_dict = flav._asdict()
            flav_dict.pop('flavorid', None)
            return flav_dict
        return {}
    
    @staticmethod
    def create_recipe(recipe_data):
        """Create a new recipe with all related data"""
        recipe_id = str(uuid.uuid1())
        nutr_id = str(uuid.uuid1())
        flavor_id = str(uuid.uuid1())
        
        with get_db_connection() as conn:
            nutr_query = text("""
                INSERT INTO NutritionalInfo (NutrID, calories, totalfat, sugar, sodium, protein, saturatedfat, carbs)
                VALUES (:nutrID, :calories, :totalfat, :sugar, :sodium, :protein, :saturatedfat, :carbs)
            """)
            conn.execute(nutr_query, {
                'nutrID': nutr_id,
                'calories': recipe_data.get('calories'),
                'totalfat': recipe_data.get('totalfat'),
                'sugar': recipe_data.get('sugar'),
                'sodium': recipe_data.get('sodium'),
                'protein': recipe_data.get('protein'),
                'saturatedfat': recipe_data.get('saturatedfat'),
                'carbs': recipe_data.get('carbs')
            })
            
            flav_query = text("""
                INSERT INTO FlavorProfiles (FlavorID, spicelevel, servingtemp, mealtype, coursetype, taste)
                VALUES (:flavID, :spicelevel, :servingtemp, :mealtype, :coursetype, :taste)
            """)
            conn.execute(flav_query, {
                'flavID': flavor_id,
                'spicelevel': recipe_data.get('spicelevel'),
                'servingtemp': recipe_data.get('servingtemp'),
                'mealtype': recipe_data.get('mealtype'),
                'coursetype': recipe_data.get('coursetype'),
                'taste': recipe_data.get('taste')
            })
            
            recipe_query = text("""
                INSERT INTO Recipes (RecipeID, RecipeName, Instructions, Time, NumSteps, NumIngredients, 
                                   Complexity, CuisineType, UserID, NutrID, FlavorID, AverageRating, NumRatings)
                VALUES (:recipe_id, :recipe_name, :instructions, :time, :num_steps, :num_ingredients, 
                        :complexity, :cuisine_type, :user_id, :nutr_id, :flavor_id, :rating, :num_ratings)
            """)
            conn.execute(recipe_query, {
                'recipe_id': recipe_id,
                'recipe_name': recipe_data['recipe_name'],
                'instructions': recipe_data['instructions'],
                'time': recipe_data['time'],
                'num_steps': recipe_data['num_steps'],
                'num_ingredients': recipe_data['num_ingredients'],
                'complexity': recipe_data['complexity'],
                'cuisine_type': recipe_data['cuisine_type'],
                'user_id': recipe_data['user_id'],
                'nutr_id': nutr_id,
                'flavor_id': flavor_id,
                'rating': 0,
                'num_ratings': 0
            })
            
            for ingredient in recipe_data['ingredients']:
                ingredient_id = str(uuid.uuid1())
                
                ingredient_query = text("""
                    INSERT INTO Ingredients (IngredientID, IngredientName)
                    VALUES (:ingredient_id, :ingredient_name)
                """)
                conn.execute(ingredient_query, {
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient.strip().lower()
                })
                
                contains_query = text("""
                    INSERT INTO Contains (RecipeID, IngredientID)
                    VALUES (:recipe_id, :ingredient_id)
                """)
                conn.execute(contains_query, {
                    'recipe_id': recipe_id,
                    'ingredient_id': ingredient_id
                })
            
            for restriction_id in recipe_data.get('restrictions', []):
                restriction_query = text("""
                    INSERT INTO CompatibleWith (RecipeID, RestrictionID)
                    VALUES (:recipe_id, :restriction_id)
                """)
                conn.execute(restriction_query, {
                    'recipe_id': recipe_id,
                    'restriction_id': restriction_id
                })
            
            conn.commit()
        
        return recipe_id
    
    @staticmethod
    def search_recipes(filters):
        """Search recipes with various filters"""
        query = "SELECT R.* FROM Recipes R"
        
        if filters.get('ingredients') or filters.get('dietary_restrictions'):
            query += " LEFT JOIN Contains C ON R.RecipeID = C.RecipeID"
            query += " LEFT JOIN Ingredients I ON C.IngredientID = I.IngredientID"
            query += " LEFT JOIN CompatibleWith CW ON R.RecipeID = CW.RecipeID"
            query += " LEFT JOIN DietaryRestrictions DR ON CW.RestrictionID = DR.RestrictionID"
        
        query += " WHERE 1=1"
        params = {}
        
        if filters.get('ingredients'):
            ingredients = [ing.strip().lower() for ing in filters['ingredients']]
            ingredient_placeholders = ', '.join([f':ingredient{i}' for i in range(len(ingredients))])
            query += f" AND I.IngredientName IN ({ingredient_placeholders})"
            for i, ingredient in enumerate(ingredients):
                params[f'ingredient{i}'] = ingredient
        
        if filters.get('average_rating'):
            query += " AND R.AverageRating >= :averageRating"
            params['averageRating'] = filters['average_rating']
        
        if filters.get('cuisine_type'):
            query += " AND R.CuisineType = :cuisineType"
            params['cuisineType'] = filters['cuisine_type']
        
        if filters.get('complexity'):
            query += " AND R.Complexity = :complexity"
            params['complexity'] = filters['complexity']
        
        if filters.get('time'):
            query += " AND R.Time < :time"
            params['time'] = filters['time']
        
        if filters.get('dietary_restrictions'):
            dietary_restrictions = filters['dietary_restrictions']
            dietary_placeholders = ', '.join([f':restriction{i}' for i in range(len(dietary_restrictions))])
            query += f" AND DR.RestrictionName IN ({dietary_placeholders})"
            for i, restriction in enumerate(dietary_restrictions):
                params[f'restriction{i}'] = restriction.strip()
        
        query += " GROUP BY R.RecipeID"
        
        having_clauses = []
        if filters.get('ingredients'):
            having_clauses.append("COUNT(DISTINCT I.IngredientName) >= :numIngredients")
            params['numIngredients'] = len(filters['ingredients'])
        
        if filters.get('dietary_restrictions'):
            having_clauses.append("COUNT(DISTINCT DR.RestrictionName) >= :numRestrictions")
            params['numRestrictions'] = len(filters['dietary_restrictions'])
        
        if having_clauses:
            query += " HAVING " + " AND ".join(having_clauses)
        
        query += " LIMIT :limit"
        params['limit'] = filters.get('limit', 20)
        
        with get_db_connection() as conn:
            result = conn.execute(text(query), params)
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]

class SaveModel:
    @staticmethod
    def is_recipe_saved(user_id, recipe_id):
        """Check if recipe is saved by user"""
        query = text("SELECT * FROM Saves WHERE UserID = :userid AND RecipeID = :recipeid")
        params = {'userid': user_id, 'recipeid': recipe_id}
        with get_db_connection() as conn:
            return conn.execute(query, params).fetchone() is not None
    
    @staticmethod
    def save_recipe(user_id, recipe_id):
        """Save a recipe"""
        query = text("INSERT INTO Saves (UserID, RecipeID) VALUES (:user_id, :recipe_id)")
        params = {'user_id': user_id, 'recipe_id': recipe_id}
        with get_db_connection() as conn:
            conn.execute(query, params)
            conn.commit()
    
    @staticmethod
    def unsave_recipe(user_id, recipe_id):
        """Unsave a recipe"""
        query = text("DELETE FROM Saves WHERE RecipeID = :recipe_id AND UserID = :userid")
        params = {'userid': user_id, 'recipe_id': recipe_id}
        g.conn.execute(query, params)
        g.conn.commit()
    
    @staticmethod
    def get_saved_recipes(user_id):
        """Get all saved recipes for a user"""
        query = text("""
            SELECT * FROM Recipes 
            JOIN Saves ON Recipes.RecipeID = Saves.RecipeID 
            WHERE Saves.UserID = :userid
        """)
        return g.conn.execute(query, {'userid': user_id}).fetchall()

class ReviewModel:
    @staticmethod
    def create_review(review_data):
        """Create a new review and update recipe rating"""
        review_id = str(uuid.uuid1())
        
        recipe_query = text("SELECT * FROM Recipes WHERE RecipeID = :recipe_id")
        recipe = g.conn.execute(recipe_query, {'recipe_id': review_data['recipe_id']}).fetchone()
        
        if not recipe:
            raise ValueError("Recipe not found")
        
        recipe_dict = recipe._asdict()
        num_ratings = recipe_dict.get('numratings', 0)
        current_rating = recipe_dict.get('averagerating', 0)
        new_rating = review_data['rating']
        
        if num_ratings > 0:
            average_rating = (num_ratings * current_rating + new_rating) / (num_ratings + 1)
        else:
            average_rating = new_rating
        
        review_query = text("""
            INSERT INTO Reviews (ReviewID, Rating, Comment, UserID, RecipeID)
            VALUES (:review_id, :rating, :comments, :user_id, :recipe_id)
        """)
        review_params = {
            'review_id': review_id,
            'rating': new_rating,
            'comments': review_data['comments'],
            'user_id': review_data['user_id'],
            'recipe_id': review_data['recipe_id']
        }
        
        with get_db_connection() as conn:
            conn.execute(review_query, review_params)
            
            update_query = text("""
                UPDATE Recipes
                SET AverageRating = :average_rating, NumRatings = :num_ratings
                WHERE RecipeID = :recipe_id
            """)
            conn.execute(update_query, {
                'recipe_id': review_data['recipe_id'],
                'average_rating': average_rating,
                'num_ratings': num_ratings + 1
            })
            
            conn.commit()
        
        return review_id
    
    @staticmethod
    def get_recent_reviews(limit=20):
        """Get recent reviews for social feed"""
        query = text("SELECT * FROM Reviews LIMIT :limit")
        with get_db_connection() as conn:
            return conn.execute(query, {'limit': limit}).fetchall()
    
    @staticmethod
    def get_recipe_name(recipe_id):
        """Get recipe name by ID"""
        query = text("SELECT R.RecipeName FROM Recipes R WHERE R.RecipeID = :recipeid")
        with get_db_connection() as conn:
            result = conn.execute(query, {'recipeid': recipe_id}).fetchone()
            return result[0] if result else "Unknown Recipe"
    
    @staticmethod
    def get_username(user_id):
        """Get username by user ID"""
        query = text("SELECT U.Username FROM Users U WHERE U.UserID = :userid")
        with get_db_connection() as conn:
            result = conn.execute(query, {'userid': user_id}).fetchone()
            return result[0] if result else "Unknown User"

class DietaryRestrictionModel:
    @staticmethod
    def get_all_restrictions():
        """Get all dietary restrictions"""
        query = text("SELECT R.RestrictionName FROM DietaryRestrictions R")
        restrictions = g.conn.execute(query).fetchall()
        restrictions_list = [res[0] for res in restrictions]
        if restrictions_list:
            restrictions_list.pop()
        return restrictions_list