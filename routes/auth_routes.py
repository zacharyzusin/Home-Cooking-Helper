from flask import Blueprint, render_template, request, redirect, url_for, session
from models import UserModel
from utils import validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@auth_bp.route('/logged-in', methods=['POST'])
def login_submit():
    """Handle login form submission"""
    username_or_email = request.form.get('usernameOrEmail')
    password = request.form.get('password')
    
    if not username_or_email or not password:
        return render_template('login.html', error='Username/email and password are required.')
    
    try:
        user = UserModel.get_user_by_credentials(username_or_email, password)
        if user:
            session['UserID'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')
    except Exception as e:
        print(f'Error during login: {e}')
        return render_template('login.html', error='An error occurred. Please try again.')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/account-creation')
def register():
    """Registration page"""
    return render_template('account_creation.html')

@auth_bp.route('/create-account', methods=['POST'])
def register_submit():
    """Handle registration form submission"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not username or not email or not password:
        return render_template('account_creation.html', 
                             error='All fields are required.')
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return render_template('account_creation.html', error=message)
    
    try:
        if UserModel.check_user_exists(username, email):
            return render_template('account_creation.html', 
                                 error='Username or email already in use.')
        
        user_id = UserModel.create_user(username, email, password)
        
        session['UserID'] = user_id
        session['username'] = username
        
        return redirect(url_for('main.index'))
        
    except Exception as e:
        print(f'Error creating account: {e}')
        return render_template('account_creation.html', 
                             error='Account creation failed. Please try again.')