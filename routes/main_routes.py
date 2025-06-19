from flask import Blueprint, render_template, request, redirect, url_for
from models import DietaryRestrictionModel, RecipeModel, ReviewModel
from config import Config
from utils import build_search_filters

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with search functionality"""
    dietary_restrictions = DietaryRestrictionModel.get_all_restrictions()
    return render_template('index.html', 
                         cuisine_types=Config.CUISINE_TYPES, 
                         dietary_restrictions=dietary_restrictions)

@main_bp.route('/search')
def search():
    """Search recipes with filters"""
    dietary_restrictions = DietaryRestrictionModel.get_all_restrictions()  
    filters = build_search_filters(request.args)    
    recipes_list = RecipeModel.search_recipes(filters)
    
    return render_template('index.html', 
                         recipes=recipes_list,
                         cuisine_types=Config.CUISINE_TYPES,
                         dietary_restrictions=dietary_restrictions)

@main_bp.route('/social')
def social():
    """Social feed showing recent reviews"""
    reviews_data = ReviewModel.get_recent_reviews(Config.MAX_REVIEWS_DISPLAY)
    reviews = []
    for review in reviews_data:
        rating, comment, recipe_id, user_id = review[1], review[2], review[4], review[3]
        
        recipe_name = ReviewModel.get_recipe_name(recipe_id)
        username = ReviewModel.get_username(user_id)
        
        reviews.append({
            'rating': rating,
            'comment': comment,
            'recipename': recipe_name,
            'username': username,
            'recipeid': recipe_id
        })
    
    return render_template('social.html', reviews=reviews)