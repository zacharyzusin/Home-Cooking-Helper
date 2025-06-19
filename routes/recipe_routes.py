from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from models import RecipeModel, SaveModel, ReviewModel, UserModel
from utils import login_required, validate_recipe_data, prepare_recipe_data_for_creation, format_recipe_instructions
from config import Config

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipe/<recipe_id>')
def show_recipe(recipe_id):
    """Display individual recipe page"""
    saved = False
    
    if 'UserID' in session:
        try:
            saved = SaveModel.is_recipe_saved(session['UserID'], recipe_id)
        except:
            pass
    
    recipe = RecipeModel.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)
    
    recipe_dict = recipe._asdict()
    
    instructions_list = format_recipe_instructions(recipe_dict['instructions'])
    
    ingredients_list = RecipeModel.get_recipe_ingredients(recipe_id)
    dietary_restrictions = RecipeModel.get_recipe_dietary_restrictions(recipe_id)
    author = RecipeModel.get_recipe_author(recipe_id)
    nutrition = RecipeModel.get_recipe_nutrition(recipe_id)
    flavor_profile = RecipeModel.get_recipe_flavor_profile(recipe_id)
    
    return render_template("recipe_info.html", 
                         saved=saved,
                         drs=dietary_restrictions,
                         flavors=flavor_profile,
                         nutrients=nutrition,
                         user=author,
                         recipe=recipe_dict,
                         instructions=instructions_list,
                         ingredients=ingredients_list)

@recipe_bp.route('/save-recipe', methods=['POST'])
@login_required
def save_recipe():
    """Save a recipe to user's collection"""
    recipe_id = request.form.get('recipe_id')
    if recipe_id:
        try:
            SaveModel.save_recipe(session['UserID'], recipe_id)
        except Exception as e:
            print(f"Error saving recipe: {e}")
    
    return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))

@recipe_bp.route('/unsave', methods=['POST'])
@login_required
def unsave_recipe_from_account():
    """Remove recipe from user's saved collection (from account page)"""
    recipe_id = request.form.get('recipe_id')
    
    if recipe_id:
        try:
            SaveModel.unsave_recipe(session['UserID'], recipe_id)
        except Exception as e:
            print(f"Error unsaving recipe: {e}")
    
    return redirect(url_for('user.account_settings'))

@recipe_bp.route('/unsave2', methods=['POST'])
@login_required
def unsave_recipe_from_recipe_page():
    """Remove recipe from user's saved collection (from recipe page)"""
    recipe_id = request.form.get('recipe_id')
    
    if recipe_id:
        try:
            SaveModel.unsave_recipe(session['UserID'], recipe_id)
        except Exception as e:
            print(f"Error unsaving recipe: {e}")
    
    return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))

@recipe_bp.route('/create-recipe')
@login_required
def create_recipe_page():
    """Recipe creation page"""
    return render_template('recipe_creation.html')

@recipe_bp.route('/recipe-creation', methods=['POST'])
@login_required
def create_recipe():
    """Handle recipe creation form submission"""
    is_valid, errors = validate_recipe_data(request.form)
    if not is_valid:
        return render_template('recipe_creation.html', 
                             error='; '.join(errors))
    
    try:
        recipe_data = prepare_recipe_data_for_creation(request.form, session['UserID'])
        
        user = UserModel.get_user_by_id(session['UserID'])
        if not user:
            raise ValueError("User does not exist")
        
        recipe_id = RecipeModel.create_recipe(recipe_data)
        
        return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))
        
    except ValueError as ve:
        return render_template('recipe_creation.html', error=str(ve))
    except Exception as e:
        print(f'Error creating recipe: {e}')
        return render_template('recipe_creation.html', 
                             error='Recipe creation failed. Please try again.')

@recipe_bp.route('/recipe/<recipe_id>/review')
@login_required
def review_page(recipe_id):
    """Review creation page"""
    recipe = RecipeModel.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)
    
    recipe_dict = recipe._asdict()
    return render_template('review_creation.html', recipe=recipe_dict)

@recipe_bp.route('/review/<recipe_id>', methods=['POST'])
@login_required
def create_review(recipe_id):
    """Handle review creation"""
    try:
        print("Form data received:", dict(request.form))
        print("All form keys:", list(request.form.keys()))
        print("Rating value:", repr(request.form.get('rating')))
        
        rating = request.form.get('rating')
        if not rating:
            raise ValueError("Rating is required")
            
        rating = int(rating)
        comments = request.form.get('comments', '')
        user_id = session['UserID']
        
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        review_data = {
            'rating': rating,
            'comments': comments,
            'user_id': user_id,
            'recipe_id': recipe_id
        }
        
        ReviewModel.create_review(review_data)
        
        return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))
        
    except ValueError as ve:
        recipe = RecipeModel.get_recipe_by_id(recipe_id)
        if recipe:
            recipe_dict = recipe._asdict()
        else:
            recipe_dict = {'recipeid': recipe_id, 'recipename': 'Unknown Recipe'}
            
        return render_template('review_creation.html', 
                             recipe=recipe_dict,
                             error=str(ve))
    except Exception as e:
        print(f'Error creating review: {e}')
        recipe = RecipeModel.get_recipe_by_id(recipe_id)
        if recipe:
            recipe_dict = recipe._asdict()
        else:
            recipe_dict = {'recipeid': recipe_id, 'recipename': 'Unknown Recipe'}
            
        return render_template('review_creation.html', 
                             recipe=recipe_dict,
                             error='Review creation failed. Please try again.')