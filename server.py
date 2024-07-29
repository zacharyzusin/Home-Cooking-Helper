import os
import uuid
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, jsonify, redirect, url_for, send_from_directory, Response, abort, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = str(uuid.uuid1())

DATABASEURI = "postgresql://apm2208:337364@34.74.171.121/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
    rest_query = text("SELECT R.RestrictionName FROM DietaryRestrictions R")
    rest = g.conn.execute(rest_query).fetchall()
    rest = [res[0] for res in rest]
    rest.pop()
    cuisine_types = ['American', 'Chinese', 'Cuban', 'Greek', 'Indian', 'Italian', 'Japanese', 'Korean', 'Mexican', 'Thai', 'Vietnamese']
    return render_template('index.html', cuisine_types = cuisine_types, dietary_restrictions = rest)

@app.route('/account-settings')
def account_settings():
    try:
        user_query = text("SELECT * FROM Users WHERE Users.userid = :userid")
        user_id = session['UserID']
        params = {'userid': user_id}
        usr = g.conn.execute(user_query, params).fetchone()
        
        sr_query = text("SELECT * FROM Recipes JOIN Saves ON Recipes.RecipeID = Saves.RecipeID WHERE Saves.UserID = :userid;")
        saved_recs = g.conn.execute(sr_query, params).fetchall()
        return render_template('account_settings.html', user = usr, recipes = saved_recs)
    except:
        return redirect('/login')

@app.route('/unsave', methods=['POST'])
def unsave():
    recipe_id = request.form.get('recipe_id')
    rem_query = text("DELETE FROM Saves WHERE RecipeID = :recipe_id AND UserID = :userid;")
    userid = session['UserID']
    params = {'userid': userid, 'recipe_id':recipe_id}
    g.conn.execute(rem_query, params)
    g.conn.commit()
    return redirect('/account-settings')

@app.route('/review/<recipe_id>', methods=['POST'])
def review(recipe_id):
    try:
        session['UserID']
        recipe_query = text("SELECT * FROM Recipes WHERE RecipeID = :recipe_id")
        recipe = g.conn.execute(recipe_query, {"recipe_id": recipe_id}).fetchone()
        if recipe is None:
            abort(404)
        recipe_dict = recipe._asdict()
        return render_template('review_creation.html', recipe = recipe_dict)
    except:
        return redirect('/login')

@app.route('/create-review', methods=['POST'])
def reviewed():
    rating = int(request.form.get('rating'))
    user_id = session['UserID']
    recipe_id = request.form.get('recipe_id')
    comments = request.form.get('comments')
    review_id = str(uuid.uuid1())

    num_query = text("""
        SELECT * FROM Recipes R
        WHERE R.RecipeID = :recipe_id
        """)
    num_params = {'recipe_id':recipe_id}
    recipe = g.conn.execute(num_query, num_params).fetchone()
    recipe_dict = recipe._asdict()
    num_rating = recipe_dict['numratings']
    average_rating = rating

    if num_rating > 1:
        current_rating = recipe_dict['averagerating']
        average_rating = (num_rating*current_rating+rating)/(num_rating+1)

    review_query = text("""
        INSERT INTO Reviews (ReviewID, Rating, Comment, UserID, RecipeID)
        VALUES (:review_id, :rating, :comments, :user_id, :recipe_id)
    """)
    review_params = {
        'review_id': review_id,
        'rating': rating,
        'comments': comments,
        'user_id': user_id,
        'recipe_id': recipe_id
    }
    with engine.connect() as conn:
        conn.execute(review_query, review_params)
        conn.commit()

    update_rating_query = text("""
        UPDATE Recipes
        SET AverageRating = :average_rating
        WHERE RecipeID = :recipe_id;
    """)
    with engine.connect() as conn:
        conn.execute(update_rating_query, {'recipe_id': recipe_id, 'average_rating': average_rating})
        conn.commit()

    return redirect(f'/recipe/{recipe_id}')

@app.route('/social')
def social():
    review_query = text("""
        SELECT * FROM reviews LIMIT 20;
    """)
    with engine.connect() as conn:
        reviews = conn.execute(review_query).fetchall()
    
    ratings_list = [review[1] for review in reviews]
    comments_list = [review[2] for review in reviews]
    recipes_list = [review[3] for review in reviews]
    user_list = [review[4] for review in reviews]

    rec_name_query = text("""
        SELECT R.recipename FROM Recipes R WHERE R.recipeid=:recipeid;
    """)
    recipe_names = []
    for i in recipes_list:
        with engine.connect() as conn:
            recipe_names.append(conn.execute(rec_name_query, {'recipeid': i}).fetchone()[0])
    print(len(recipe_names))
    username_query = text("""
        SELECT U.username FROM Users U WHERE U.userid=:userid;
    """)
    usernames = []
    for i in user_list:
        with engine.connect() as conn:
            usernames.append(conn.execute(username_query, {'userid': i}).fetchone()[0])

    reviews = [
        {'rating': rating, 'comment': comment, 'recipename': recipe_name, 'username': username, 'recipeid': recipeid}
        for rating, comment, recipe_name, username, recipeid in zip(ratings_list, comments_list, recipe_names, usernames, recipes_list)
    ]
    print(len(reviews))
    return render_template('social.html', reviews=reviews)

@app.route('/unsave2', methods=['POST'])
def unsave2():
    recipe_id = request.form.get('recipe_id')
    rem_query = text("DELETE FROM Saves WHERE RecipeID = :recipe_id AND UserID = :userid;")
    userid = session['UserID']
    params = {'userid': userid, 'recipe_id':recipe_id}
    g.conn.execute(rem_query, params)
    g.conn.commit()
    return redirect(f'/recipe/{recipe_id}')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/saved-recipes')
def saved_recipes():
    return render_template('saved_recipes.html')

@app.route('/account-creation')
def ac():
    return render_template('account_creation.html')

@app.route('/recipe/<recipe_id>')
def show_recipe(recipe_id):
    saved = False
    try:
        is_saved_q = text("""
        SELECT * FROM Saves 
        WHERE UserID = :userid AND RecipeID = :recipeid
        """)
        params = {'userid': session['UserID'], 'recipeid': recipe_id}
        with engine.connect() as conn:
            result = conn.execute(is_saved_q, params).fetchone()
        if result is not None:
            saved = True
    except:
        pass

    recipe_query = text("SELECT * FROM Recipes WHERE RecipeID = :recipe_id")
    recipe = g.conn.execute(recipe_query, {"recipe_id": recipe_id}).fetchone()
    if recipe is None:
        abort(404)
    
    recipe_dict = recipe._asdict()

    instructions_list = recipe_dict['instructions'].strip('[]').split(', ')


    ingredients_query = text("""
        SELECT Ingredients.IngredientName FROM Ingredients 
        JOIN Contains ON Ingredients.IngredientID = Contains.IngredientID 
        WHERE Contains.RecipeID = :recipe_id
      """)
    ingredients = g.conn.execute(ingredients_query, {'recipe_id': recipe_id}).fetchall()
    ingredients_list = [ingredient[0] for ingredient in ingredients]


    dr_query = text("""
        SELECT DietaryRestrictions.restrictionname FROM DietaryRestrictions 
        JOIN CompatibleWith ON DietaryRestrictions.restrictionid = CompatibleWith.restrictionid 
        WHERE CompatibleWith.RecipeID = :recipe_id
      """)
    drs = g.conn.execute(dr_query, {'recipe_id': recipe_id}).fetchall()
    dr_list = [dr[0] for dr in drs]

    user_query = text("""
        SELECT U.Username FROM Users U, Recipes R
        WHERE R.RecipeID = :recipe_id AND U.UserID = R.UserID
      """)
    user = g.conn.execute(user_query, {'recipe_id': recipe_id}).fetchone()
    user = user[0].strip("'").title()

    nutr_query = text("""
        SELECT N.* FROM NutritionalInfo N, Recipes R
        WHERE R.RecipeID = :recipe_id AND N.NutrID = R.NutrID
      """)
    nutr = g.conn.execute(nutr_query, {'recipe_id': recipe_id}).fetchone()._asdict()
    nutr.pop('nutrid')

    flav_query = text("""
        SELECT F.* FROM FlavorProfiles F, Recipes R
        WHERE R.RecipeID = :recipe_id AND F.FlavorID = R.FlavorID
      """)
    flav = g.conn.execute(flav_query, {'recipe_id': recipe_id}).fetchone()._asdict()
    flav.pop('flavorid')
    return render_template("recipe_info.html", saved = saved, drs = dr_list, flavors = flav, nutrients = nutr, user=user, recipe=recipe_dict, instructions=instructions_list, ingredients=ingredients_list)

@app.route('/search/', methods=['GET'])
def search():
    rest_query = text("SELECT R.RestrictionName FROM DietaryRestrictions R")
    rest = g.conn.execute(rest_query).fetchall()
    rest = [res[0] for res in rest]
    rest.pop()

    cuisine_types = ['American', 'Chinese', 'Cuban', 'Greek', 'Indian', 'Italian', 'Japanese', 'Korean', 'Mexican', 'Thai', 'Vietnamese']
    
    ingredients = request.args.get('ingredients', '').split(',')
    averageRating = request.args.get('averageRating')
    cuisineType = request.args.get('cuisineType')
    complexity = request.args.get('complexity')
    time = request.args.get('time')
    dietaryRestrictions = request.args.getlist('dietaryRestrictions')
    ingredients = [ingredient.lower() for ingredient in ingredients]
    # query = """
    # SELECT R.* FROM Recipes R
    # LEFT JOIN Contains C ON R.RecipeID = C.RecipeID
    # LEFT JOIN Ingredients I ON C.IngredientID = I.IngredientID
    # LEFT JOIN CompatibleWith CW ON R.RecipeID = CW.RecipeID
    # LEFT JOIN DietaryRestrictions DR ON CW.RestrictionID = DR.RestrictionID
    # WHERE 1=1
    # """

    # conditions = []

    # if ingredients:
    #     ingredient_subquery = """
    #     :num_ingredients <= (
    #         SELECT COUNT(DISTINCT I2.IngredientName)
    #         FROM Contains C2
    #         JOIN Ingredients I2 ON C2.IngredientID = I2.IngredientID
    #         WHERE C2.RecipeID = R.RecipeID AND I2.IngredientName IN :ingredients
    #     )
    #     """
    #     conditions.append(ingredient_subquery)

    # if averageRating:
    #     conditions.append("R.AverageRating = :averageRating")
    # if cuisineType:
    #     conditions.append("R.CuisineType = :cuisineType")
    # if complexity:
    #     conditions.append("R.Complexity = :complexity")
    # if time:
    #     conditions.append("R.Time <= :time")
    # if dietaryRestrictions:
    #     conditions.append("DR.RestrictionName IN (:dietaryRestrictions)")

    # if conditions:
    #     query += ' AND ' + ' AND '.join(conditions)

    # query += ' GROUP BY R.RecipeID LIMIT 20'

    # params = {
    #     'ingredients': tuple(ingredients), 
    #     'num_ingredients': len(ingredients),
    #     'averageRating': averageRating,
    #     'cuisineType': cuisineType,
    #     'complexity': complexity,
    #     'time': time,
    #     'dietaryRestrictions': tuple(dietaryRestrictions)
    # }

    query = "SELECT R.* FROM Recipes R"

    if ingredients or dietaryRestrictions:
        query += " LEFT JOIN Contains C ON R.RecipeID = C.RecipeID"
        query += " LEFT JOIN Ingredients I ON C.IngredientID = I.IngredientID"
        query += " LEFT JOIN CompatibleWith CW ON R.RecipeID = CW.RecipeID"
        query += " LEFT JOIN DietaryRestrictions DR ON CW.RestrictionID = DR.RestrictionID"

    query += " WHERE 1=1" 

    params = {}

    if ingredients:
        ingredient_placeholders = ', '.join([f':ingredient{i}' for i in range(len(ingredients))])
        query += f" AND I.IngredientName IN ({ingredient_placeholders})"
        for i, ingredient in enumerate(ingredients):
            params[f'ingredient{i}'] = ingredient.strip()

    if averageRating:
        query += " AND R.AverageRating >= :averageRating"
        params['averageRating'] = averageRating

    if cuisineType:
        query += " AND R.CuisineType = :cuisineType"
        params['cuisineType'] = cuisineType

    if complexity:
        query += " AND R.Complexity = :complexity"
        params['complexity'] = complexity

    if time:
        query += " AND R.Time < :time"
        params['time'] = time

    if dietaryRestrictions:
        dietary_placeholders = ', '.join([f':restriction{i}' for i in range(len(dietaryRestrictions))])
        query += f" AND DR.RestrictionName IN ({dietary_placeholders})"
        for i, restriction in enumerate(dietaryRestrictions):
            params[f'restriction{i}'] = restriction.strip()

    query += " GROUP BY R.RecipeID"
    
    if ingredients:
        query += " HAVING COUNT(DISTINCT I.IngredientName) >= :numIngredients"
        params['numIngredients'] = len(ingredients)

    if dietaryRestrictions:
        query += " AND COUNT(DISTINCT DR.RestrictionName) >= :numRestrictions"
        params['numRestrictions'] = len(dietaryRestrictions)

    query += '  LIMIT 20'

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        columns = result.keys()
        recipes_list = [dict(zip(columns, row)) for row in result]
    return render_template('index.html', recipes=recipes_list, cuisine_types = cuisine_types, dietary_restrictions = rest)

@app.route('/create-account', methods=['POST'])
def create_account():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    print(password)
    if len(password) < 8:
        print("Password error")
        return render_template('account_creation.html', error='Password must be at least 8 characters')
    
    test_email_query = text("""
        SELECT COUNT(*) FROM users 
        WHERE username = :username OR email = :email
    """)
    with engine.connect() as conn:
        params = {'username': username, 'email': email}
        result = conn.execute(test_email_query, params).fetchone()
        in_use = result[0] > 0

        if in_use:
            return render_template('account_creation.html', error='Username or email already in use.')
        
    query = text("INSERT INTO users (UserID, Username, Email, Password) VALUES (:userid, :username, :email, :password)")
    userid = str(uuid.uuid1())
    params = {'userid': userid, 'username': username, 'email': email, 'password': password}
    try:
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        print('Account created successfully')
        return redirect(url_for('login'))
    except Exception as e:
        print(f'Error creating account: {e}')
        return render_template('account_creation.html', error='Account creation failed. Please try again.')
    
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logged-in', methods=['POST'])
def logged_in():
    username_or_email = request.form.get('usernameOrEmail')
    password = request.form.get('password')

    query = text("""
        SELECT * FROM Users WHERE (Username = :usernameOrEmail OR Email = :usernameOrEmail) AND Password = :password
    """)
    params = {'usernameOrEmail': username_or_email, 'password': password}

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params).fetchone()
        if result:
            print('Login successful')
            session['UserID'] = result[0]
            return redirect('/')
        else:
            print('Login failed: Invalid credentials')
            return render_template('login.html', error='Invalid credentials. Please try again.')
    except Exception as e:
        print(f'Error during login: {e}')
        return render_template('login.html', error='An error occurred. Please try again.')

@app.route('/create-recipe')
def creation_page():
    try:
        session['UserID']
        return render_template('recipe_creation.html')
    except:
        return redirect('/login')

@app.route('/recipe-creation', methods=['POST'])
def create_recipe():
    recipe_id = str(uuid.uuid1())
    recipe_name = request.form.get('recipeName').lower()
    ingredients = request.form.get('ingredients').split(',')
    for i in range(0, len(ingredients)):
        ingredients[i] = ingredients[i].lower()
    instructions = request.form.get('instructions')
    time = request.form.get('time')
    num_steps = request.form.get('numSteps')
    num_ingredients = request.form.get('numIngredients')
    complexity = request.form.get('complexity')
    cuisine_type = request.form.get('cuisineType')
    user_id = session['UserID']
    calories = request.form.get('calories')
    totalfat = request.form.get('totalfat')
    sugar = request.form.get('sugar')
    sodium = request.form.get('sodium')
    protein = request.form.get('protein')
    saturatedfat = request.form.get('saturatedfat')
    carbs = request.form.get('carbs')
    nutrID = str(uuid.uuid1())
    restrictions = request.args.getlist('restrictions')
    flavID = str(uuid.uuid1())
    spicelevel = request.args.get('spicelevel')
    servingtemp = request.args.get('servingtemp')
    mealtype = request.args.get('mealtype')
    coursetype = request.args.get('coursetype')
    taste = request.args.get('taste')

    try:
        if int(time) < 0 or int(num_steps) <= 0 or int(num_ingredients) <= 0:
            raise ValueError("Invalid values for time, num_steps, or num_ingredients")

        complexity_values = ('Beginner', 'Aspiring Chef', 'Master Chef')
        if complexity not in complexity_values:
            raise ValueError("Invalid value for complexity")

        user_check_query = text("SELECT COUNT(*) FROM Users WHERE UserID = :user_id")
        user_check_params = {'user_id': user_id}
        with engine.connect() as conn:
            user_exists = conn.execute(user_check_query, user_check_params).scalar()
            if not user_exists:
                raise ValueError("User does not exist")

        nutr_query = text("""
            INSERT INTO NutritionalInfo (NutrID, calories, totalfat, sugar, sodium, protein, saturatedfat, carbs)
            VALUES (:nutrID, :calories, :totalfat, :sugar, :sodium, :protein, :saturatedfat, :carbs)
        """)
        nutr_params = {'nutrID': nutrID, 
                       'calories':calories, 
                       'totalfat': totalfat, 
                       'sugar': sugar, 
                       'sodium': sodium, 
                       'protein': protein, 
                       'saturatedfat': saturatedfat, 
                       'carbs': carbs}
        
        flav_query = text("""
            INSERT INTO FlavorProfiles (FlavorID, spicelevel, servingtemp, mealtype, coursetype, taste)
            VALUES (:flavID, :spicelevel, :servingtemp, :mealtype, :coursetype, :taste)
        """)
        flav_params = {'flavID': flavID,
                        'spicelevel': spicelevel, 
                       'servingtemp':servingtemp, 
                       'mealtype': mealtype, 
                       'coursetype': coursetype, 
                       'taste': taste}
        
        with engine.connect() as conn:
            conn.execute(nutr_query, nutr_params)
            conn.execute(flav_query, flav_params)
            conn.commit()

        query = text("""
            INSERT INTO Recipes (RecipeID, RecipeName, Instructions, Time, NumSteps, NumIngredients, Complexity, CuisineType, UserID, NutrID, FlavorID, AverageRating)
            VALUES (:recipe_id, :recipe_name, :instructions, :time, :num_steps, :num_ingredients, :complexity, :cuisine_type, :user_id, :nutr_id, :flavor_id, :rating)
        """)
        params = {
            'recipe_id': recipe_id,
            'recipe_name': recipe_name,
            'instructions': instructions,
            'time': time,
            'num_steps': num_steps,
            'num_ingredients': num_ingredients,
            'complexity': complexity,
            'cuisine_type': cuisine_type,
            'user_id': user_id,
            'nutr_id': nutrID,
            'flavor_id': flavID,
            'rating': 0
        }

        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        for id in restrictions:
            restr_query = text("""
                INSERT INTO CompatibleWith (RecipeID, RestrictionID)
                VALUES (:recipe_id, :restriction_id)
            """)
            r_params = {'recipe_id': recipe_id, 'restriction_id': id}
            
            with engine.connect() as conn:
                conn.execute(restr_query, r_params)
                conn.commit()

        ingredient_query = text("""
                INSERT INTO Ingredients (IngredientID, IngredientName)
                VALUES (:ingredient_id, :ingredient_name)
            """)
        contains_query = text("""
                INSERT INTO Contains (RecipeID, IngredientID)
                VALUES (:recipe_id, :ingredient_id)
            """)
        for ingredient in ingredients:
            ingred_id = str(uuid.uuid1())
            ingred_params = {'ingredient_id': ingred_id, 'ingredient_name': ingredient}
            contains_params = {'recipe_id': recipe_id, 'ingredient_id': ingred_id}
            with engine.connect() as conn:
                conn.execute(ingredient_query, ingred_params)
                conn.execute(contains_query, contains_params)
                conn.commit()


        print('Recipe created successfully')
        return redirect('/')
    except ValueError as ve:
        print(f'Error creating recipe: {ve}')
        return render_template('recipe_creation.html', error=str(ve))
    except Exception as e:
        print(f'Error creating recipe: {e}')
        return render_template('recipe_creation.html', error='Recipe creation failed. Please try again.')

@app.route('/save-recipe', methods=['POST'])
def save_recipe():
    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        save_query = text("INSERT INTO Saves (UserID, RecipeID) VALUES (:user_id, :recipe_id)")
        save_params = {'user_id': session['UserID'], 'recipe_id': recipe_id}
        with engine.connect() as conn:
            save_query = text("INSERT INTO Saves (UserID, RecipeID) VALUES (:user_id, :recipe_id)")
            save_params = {'user_id': session['UserID'], 'recipe_id': recipe_id}
            conn.execute(save_query, save_params)
            conn.commit()
        return redirect(url_for('show_recipe', recipe_id=recipe_id))


if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
      HOST, PORT = host, port
      print("running on %s:%d" % (HOST, PORT))
      app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
