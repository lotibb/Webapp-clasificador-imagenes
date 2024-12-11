import os

class Config:
    # Flask Configurations
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pinchellave')  # Replace 'put_your_secret_key_here' with your actual key

    # MySQL Database Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'aMerica8dic&?'
    MYSQL_DB = 'webapp_image_viewer'
    MYSQL_CURSORCLASS = 'DictCursor'

    # Image Directory Configuration
    BASE_IMAGE_DIRECTORY = os.path.join(os.getcwd(), 'images')
    USER_IMAGE_DIRECTORIES = {
        "lotibb": r"D:\IG\calderitas\01_calderitas\03_imagenes_frentes_predios\imagenes",
        "user2": os.path.join(BASE_IMAGE_DIRECTORY, "user2"),
        "user3": os.path.join(BASE_IMAGE_DIRECTORY, "user3"),
    }

    # Default Username
    DEFAULT_USERNAME = "lotibb"

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'pinchellave'  # Replace with a unique key for development

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pinchellave')  # Ensure this is set in production
