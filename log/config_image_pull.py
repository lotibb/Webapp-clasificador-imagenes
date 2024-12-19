import os

class Config:
    # Flask Configurations
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pinchellave')  # Replace with your actual key

    # MySQL Database Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'aMerica8dic&?'
    MYSQL_DB = 'webapp_image_viewer'
    MYSQL_CURSORCLASS = 'DictCursor'

    # Base Image Directory
    BASE_IMAGE_DIRECTORY = os.path.join(os.getcwd(), 'images')

    # User-Specific Directory Configuration
    USER_DIRECTORY_CONFIG = {
        "lotibb": {
            "base_path": r"D:\IG\calderitas\01_calderitas\03_imagenes_frentes_predios\imagenes_prueba_para_vizualizador_imagenes",
            "folders": ["Comercial", "No comercial"]
        },
        "antonio": {
            "base_path": r"D:\IG\calderitas\01_calderitas\03_imagenes_frentes_predios\imagenes_prubea_para_vizualizador_imagenes_2",
            "folders": ["Baldio", "No baldio", "Otro"]
        },
        "erick": {
            "base_path": r"D:\IG\calderitas\01_calderitas\03_imagenes_frentes_predios\imagenes_prubea_para_vizualizador_imagenes_3",
            "folders": ["Si", "No"]
        }
    }

    # User Image Directories (Will be populated dynamically)
    USER_IMAGE_DIRECTORIES = {}

    @classmethod
    def initialize_user_directories(cls):
        """
        Create user-specific folders based on USER_DIRECTORY_CONFIG.
        Ensures existing folders are not overwritten.
        """
        for user, config in cls.USER_DIRECTORY_CONFIG.items():
            base_path = config["base_path"]
            folder_names = config["folders"]

            # Ensure the base directory exists
            try:
                os.makedirs(base_path, exist_ok=True)  # Creates base directory if it doesn't exist
            except Exception as e:
                print(f"Error creating base path for user '{user}': {e}")
                continue  # Skip this user if the base path creation fails

            cls.USER_IMAGE_DIRECTORIES[user] = {}

            for folder_name in folder_names:
                folder_path = os.path.join(base_path, folder_name)
                try:
                    os.makedirs(folder_path, exist_ok=True)  # Creates the folder if it doesn't exist
                    cls.USER_IMAGE_DIRECTORIES[user][folder_name] = folder_path
                except Exception as e:
                    print(f"Error creating folder '{folder_name}' for user '{user}': {e}")

# Initialize user directories on app startup
Config.initialize_user_directories()


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'pinchellave'  # Replace with a unique key for development


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pinchellave')  # Ensure this is set in production
