from flask import Blueprint, render_template, session, redirect, url_for
from models import UserModel, SaveModel
from utils import login_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/account-settings')
@login_required
def account_settings():
    """User account settings page"""
    try:
        user_id = session['UserID']
        
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return redirect(url_for('auth.login'))
        
        saved_recipes = SaveModel.get_saved_recipes(user_id)
        
        return render_template('account_settings.html', 
                             user=user, 
                             recipes=saved_recipes)
    except Exception as e:
        print(f"Error loading account settings: {e}")
        return redirect(url_for('auth.login'))

@user_bp.route('/saved-recipes')
@login_required
def saved_recipes():
    """User's saved recipes page"""
    return render_template('saved_recipes.html')