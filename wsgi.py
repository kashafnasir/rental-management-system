import sys
import os

# Add your project directory to the sys.path
project_folder = '/home/YOUR_USERNAME/final_rental_management_system'
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

# For debugging (remove in production)
# application.config['DEBUG'] = False