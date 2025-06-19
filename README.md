# Home Cooking Helper

A comprehensive web application for sharing, discovering, and managing recipes. This platform serves as your complete home cooking companion, offering users guidance on everything they need to know to prepare food in the comfort of their own homes. Users can create accounts, share their own recipes, save favorites, write reviews, and discover new recipes through advanced search functionality.

![Homepage](/static/cooking_home.png)

## Features

### Advanced Search
Users can search recipes using multiple criteria:
- **Ingredients**: Find recipes containing specific ingredients
- **Cuisine Type**: Filter by cuisine (American, Chinese, Italian, etc.)
- **Dietary Restrictions**: Filter by dietary needs (vegetarian, gluten-free, etc.)
- **Complexity**: Filter by cooking skill level
- **Time**: Find recipes within time constraints
- **Rating**: Filter by minimum average rating

### Recipe Management
- **Create Recipes**: Add detailed recipes with ingredients, instructions, and metadata
- **Nutritional Info**: Include calorie and nutrient information
- **Flavor Profiles**: Categorize by spice level, temperature, meal type
- **Save System**: Bookmark recipes for quick access

### Review System
- **Rating**: 1-5 star rating system
- **Comments**: Detailed text reviews
- **Auto-calculation**: Recipe ratings automatically update with new reviews
- **Social Feed**: Browse recent community reviews

### Recipe Collection Interface
![Recipe Collection](/static/cooking_recipes.png)

### Create Recipe Form
![Create Recipe](/static/cooking_create.png)

### Account Settings Dashboard
![Account Settings](/static/cooking_account.png)

### Recipe Details View
![Recipe Details](/static/cooking_recipe.png)

## Tech Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL, SQLAlchemy
- **Frontend**: HTML, Jinja2

## Database Schema

The application uses a PostgreSQL database with the following main tables:

- **Users**: User account information
- **Recipes**: Recipe data including instructions, timing, and complexity
- **Ingredients**: Individual ingredients
- **Contains**: Many-to-many relationship between recipes and ingredients
- **DietaryRestrictions**: Available dietary restrictions
- **CompatibleWith**: Many-to-many relationship between recipes and restrictions
- **NutritionalInfo**: Nutritional data for recipes
- **FlavorProfiles**: Flavor and serving information
- **Reviews**: User reviews and ratings
- **Saves**: User's saved recipes

### Entity Relationship Diagram
![ER_Diagram](/static/entity_diagram.png)

## Project Structure

```
./
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── database.py                 # Database connection management
├── models.py                   # Database query functions and data models
├── utils.py                    # Utility functions and decorators
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── routes/                     # Route handlers organized by functionality
│   ├── __init__.py            # Route registration
│   ├── main_routes.py         # Homepage and search routes
│   ├── auth_routes.py         # Authentication routes
│   ├── recipe_routes.py       # Recipe management routes
│   └── user_routes.py         # User account routes
└── templates/                  # HTML templates
    ├── index.html
    ├── login.html
    ├── account_creation.html
    ├── recipe_info.html
    ├── recipe_creation.html
    ├── review_creation.html
    ├── account_settings.html
    ├── saved_recipes.html
    └── social.html
```

## File Descriptions

### Core Files

- **`app.py`**: Main application entry point using the factory pattern
- **`config.py`**: Centralized configuration management with environment variable support
- **`database.py`**: Database connection setup and request/teardown handlers
- **`models.py`**: Database interaction layer with organized model classes
- **`utils.py`**: Common utility functions, decorators, and data validation

### Route Modules

- **`routes/main_routes.py`**: Homepage, search functionality, and social feed
- **`routes/auth_routes.py`**: User login, logout, and registration
- **`routes/recipe_routes.py`**: Recipe creation, viewing, saving, and reviews
- **`routes/user_routes.py`**: User account management and saved recipes

## Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL database
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recipe-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="your-postgresql-connection-string"
   ```
   
   Or create a `.env` file:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

5. **Configure the database**
   - Update the `DATABASE_URI` in `config.py` if not using environment variables
   - Ensure your PostgreSQL database is running and accessible

### Running the Application

1. **Start the application**
   ```bash
   python app.py
   ```
   
   Or with custom settings:
   ```bash
   python app.py --debug --host 0.0.0.0 --port 8111
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8111`
   - Create an account or log in to start using the platform

### Command Line Options

- `--debug`: Enable debug mode for development
- `--threaded`: Enable threaded mode for better performance
- `HOST`: Specify the host address (default: 0.0.0.0)
- `PORT`: Specify the port number (default: 8111)

## Configuration

### Environment Variables

The application supports the following environment variables:

- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Set to 'development' for debug mode

### Application Settings

Key configuration options in `config.py`:

- `MIN_PASSWORD_LENGTH`: Minimum password length (default: 8)
- `MAX_SEARCH_RESULTS`: Maximum recipes returned in search (default: 20)
- `MAX_REVIEWS_DISPLAY`: Maximum reviews shown in social feed (default: 20)
- `CUISINE_TYPES`: Available cuisine categories
- `COMPLEXITY_LEVELS`: Recipe difficulty levels

## Security Features

- **Session Management**: Secure user sessions with Flask's session handling
- **Login Required**: Protected routes using decorators
- **Input Validation**: Server-side validation for all user inputs
- **SQL Injection Prevention**: Parameterized queries with SQLAlchemy
- **Password Requirements**: Minimum length and complexity validation
