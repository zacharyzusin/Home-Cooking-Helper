from flask import session, redirect, url_for
from functools import wraps
from config import Config

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'UserID' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_password(password):
    """Validate password meets requirements"""
    if len(password) < Config.MIN_PASSWORD_LENGTH:
        return False, f'Password must be at least {Config.MIN_PASSWORD_LENGTH} characters'
    return True, 'Password is valid'

def validate_recipe_data(data):
    """Validate recipe creation data"""
    errors = []
    
    required_fields = ['recipeName', 'ingredients', 'instructions', 'time', 
                      'numSteps', 'numIngredients', 'complexity', 'cuisineType']
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} is required')
    
    try:
        time = int(data.get('time', 0))
        num_steps = int(data.get('numSteps', 0))
        num_ingredients = int(data.get('numIngredients', 0))
        
        if time < 0:
            errors.append('Time cannot be negative')
        if num_steps <= 0:
            errors.append('Number of steps must be positive')
        if num_ingredients <= 0:
            errors.append('Number of ingredients must be positive')
            
    except (ValueError, TypeError):
        errors.append('Invalid numeric values provided')
    
    if data.get('complexity') not in Config.COMPLEXITY_LEVELS:
        errors.append('Invalid complexity level')
    
    if data.get('cuisineType') not in Config.CUISINE_TYPES:
        errors.append('Invalid cuisine type')
    
    return len(errors) == 0, errors

def parse_ingredients(ingredients_str):
    """Parse ingredients string into list"""
    if not ingredients_str:
        return []
    
    ingredients = ingredients_str.split(',')
    return [ingredient.strip().lower() for ingredient in ingredients if ingredient.strip()]

def format_recipe_instructions(instructions_str):
    """Format recipe instructions for display"""
    if not instructions_str:
        return []
    
    instructions = instructions_str.strip('[]').split(', ')
    return [instruction.strip().strip('"\'') for instruction in instructions]

def safe_int_conversion(value, default=0):
    """Safely convert value to integer"""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default

def safe_float_conversion(value, default=0.0):
    """Safely convert value to float"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def format_user_display_name(username):
    """Format username for display"""
    if not username:
        return "Unknown User"
    return username.strip("'").title()

def build_search_filters(request_args):
    """Build search filters from request arguments"""
    filters = {}
    
    ingredients_str = request_args.get('ingredients', '')
    if ingredients_str:
        filters['ingredients'] = parse_ingredients(ingredients_str)
    
    if request_args.get('averageRating'):
        filters['average_rating'] = safe_float_conversion(request_args.get('averageRating'))
    
    if request_args.get('cuisineType'):
        filters['cuisine_type'] = request_args.get('cuisineType')
    
    if request_args.get('complexity'):
        filters['complexity'] = request_args.get('complexity')
    
    if request_args.get('time'):
        filters['time'] = safe_int_conversion(request_args.get('time'))
    
    dietary_restrictions = request_args.getlist('dietaryRestrictions')
    if dietary_restrictions:
        filters['dietary_restrictions'] = dietary_restrictions
    
    filters['limit'] = Config.MAX_SEARCH_RESULTS
    
    return filters

def prepare_recipe_data_for_creation(form_data, user_id):
    """Prepare recipe data from form for database insertion"""
    return {
        'recipe_name': form_data.get('recipeName', '').lower(),
        'ingredients': parse_ingredients(form_data.get('ingredients', '')),
        'instructions': form_data.get('instructions', ''),
        'time': safe_int_conversion(form_data.get('time')),
        'num_steps': safe_int_conversion(form_data.get('numSteps')),
        'num_ingredients': safe_int_conversion(form_data.get('numIngredients')),
        'complexity': form_data.get('complexity', ''),
        'cuisine_type': form_data.get('cuisineType', ''),
        'user_id': user_id,
        'calories': safe_int_conversion(form_data.get('calories')),
        'totalfat': safe_float_conversion(form_data.get('totalfat')),
        'sugar': safe_float_conversion(form_data.get('sugar')),
        'sodium': safe_float_conversion(form_data.get('sodium')),
        'protein': safe_float_conversion(form_data.get('protein')),
        'saturatedfat': safe_float_conversion(form_data.get('saturatedfat')),
        'carbs': safe_float_conversion(form_data.get('carbs')),
        'spicelevel': form_data.get('spicelevel', ''),
        'servingtemp': form_data.get('servingtemp', ''),
        'mealtype': form_data.get('mealtype', ''),
        'coursetype': form_data.get('coursetype', ''),
        'taste': form_data.get('taste', ''),
        'restrictions': form_data.getlist('restrictions', [])
    }