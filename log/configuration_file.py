import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pinchellave')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'aMerica8dic&?')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'webapp_image_viewer')
    MYSQL_CURSORCLASS = os.environ.get('MYSQL_CURSORCLASS', 'DictCursor')

    # User classification options
    USER_CLASSIFICATIONS = {
        "lotibb": {
            "classification_options": ["Si", "No"],
        },
        "antonio": {
            "classification_options": ["si", "no"],
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'pinchellave'  # Replace with a unique key for development

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pinchellave')  # Ensure this is set in production