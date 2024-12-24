import pymysql
from flask import Flask, render_template, jsonify, request, redirect, session
from flask_mysqldb import MySQL
from configuration_file import DevelopmentConfig  # Import your config class

app = Flask(__name__, template_folder='template')

# Load configuration from config.py
app.config.from_object(DevelopmentConfig)

# Initialize MySQL
mysql = MySQL(app)

def initialize_user_columns():
    """
    Dynamically creates a column in the 'solidaridad_imagenes' table for each user 
    based on the value of 'atributo_clasificando' in the 'usuarios' table.
    The column will be of type VARCHAR(15) and allow NULL values.
    """
    db_config = {
        "host": DevelopmentConfig.MYSQL_HOST,
        "user": DevelopmentConfig.MYSQL_USER,
        "password": DevelopmentConfig.MYSQL_PASSWORD,
        "database": DevelopmentConfig.MYSQL_DB,
        "cursorclass": pymysql.cursors.DictCursor  # Use DictCursor to fetch rows as dictionaries
    }

    # Establish database connection
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Fetch users' data including 'atributo_clasificando' and the table name
        cursor.execute("SELECT nmusuario, atributo_clasificando, pull_table_images_name FROM usuarios")
        users = cursor.fetchall()

        for user in users:
            username = user['nmusuario']
            atributo = user['atributo_clasificando']
            table_name = user['pull_table_images_name']

            if atributo:
                sanitized_column = atributo.replace(" ", "_")

                # Check if the column already exists
                check_column_sql = f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{DevelopmentConfig.MYSQL_DB}' 
                AND TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME = '{sanitized_column}';
                """
                cursor.execute(check_column_sql)
                column_exists = cursor.fetchone()['COUNT(*)']

                # Add the column if it does not exist
                if column_exists == 0:
                    sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{sanitized_column}` VARCHAR(15) NULL;"
                    cursor.execute(sql)
                    print(f"Added column '{sanitized_column}' to table '{table_name}' for user '{username}'.")

        connection.commit()
        print("All columns initialized successfully.")
    except Exception as e:
        print(f"Error initializing columns: {e}")
    finally:
        cursor.close()
        connection.close()

# Initialize columns when the app starts
initialize_user_columns()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtUsuario' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtUsuario']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE nmusuario = %s AND contraseña = %s', (_correo, _password,))
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account['usuarioid']
            session['username'] = account['nmusuario']
            session['indice'] = account['indice']
            session['pull_table_images_name'] = account['pull_table_images_name']

            # Fetch additional attributes
            atri_clas = account['atributo_clasificando']
            nombre_usuario = account['nmusuario']
            num_imagenes_clasificadas = account['num_imagenes_clasificadas']  # Fetch the number of images classified

            # Get classification options for the user
            classification_options = DevelopmentConfig.USER_CLASSIFICATIONS.get(nombre_usuario, {}).get("classification_options", [])

            return render_template(
                "image_classification.html", 
                atri_clas=atri_clas, 
                nombre_usuario=nombre_usuario, 
                classification_options=classification_options, 
                num_imagenes_clasificadas=num_imagenes_clasificadas  # Pass the value to the template
            )
        else:
            return render_template('index.html', mensaje="Usuario o Contraseña Incorrectas")

@app.route('/get-image', methods=['GET'])
def get_image():
    pull_table_images_name = session.get('pull_table_images_name')
    indice = session.get('indice')

    if not pull_table_images_name or indice is None:
        return jsonify({"error": "Missing session data"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT image_url FROM {pull_table_images_name} WHERE id_imagen = %s", (indice,))
        image = cur.fetchone()
        cur.close()

        if image:
            return jsonify(image)
        else:
            return jsonify({"error": "Image not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-index', methods=['POST'])
def update_index():
    action = request.json.get('action')
    classification_value = request.json.get('classification')  # Get classification value from request

    if action not in ['next', 'previous']:
        return jsonify({"error": "Invalid action"}), 400

    try:
        cur = mysql.connection.cursor()

        # Get current session data
        current_indice = session.get('indice')
        user_id = session.get('id')
        pull_table_images_name = session.get('pull_table_images_name')

        # Fetch 'atributo_clasificando' and other user-specific details
        cur.execute("SELECT atributo_clasificando, num_imagenes_clasificadas FROM usuarios WHERE usuarioid = %s", (user_id,))
        user_data = cur.fetchone()
        atributo_clasificando = user_data['atributo_clasificando']
        num_imagenes_clasificadas = user_data['num_imagenes_clasificadas']

        if action == 'next':
            # Check if the image is already classified before proceeding
            if classification_value and pull_table_images_name and atributo_clasificando:
                sanitized_column = atributo_clasificando.replace(" ", "_")

                # Check if the current image is unclassified
                cur.execute(
                    f"SELECT `{sanitized_column}` FROM `{pull_table_images_name}` WHERE id_imagen = %s",
                    (current_indice,)
                )
                current_classification = cur.fetchone()[sanitized_column]

                # Update the classification only if it's currently unclassified
                if not current_classification:
                    cur.execute(
                        f"UPDATE `{pull_table_images_name}` SET `{sanitized_column}` = %s WHERE id_imagen = %s",
                        (classification_value, current_indice)
                    )

                    # Increment the user's classified images count
                    cur.execute(
                        "UPDATE usuarios SET num_imagenes_clasificadas = num_imagenes_clasificadas + 1 WHERE usuarioid = %s",
                        (user_id,)
                    )
                    num_imagenes_clasificadas += 1

            # Get the next image index
            cur.execute(f"SELECT MIN(id_imagen) FROM {pull_table_images_name} WHERE id_imagen > %s", (current_indice,))
            new_indice = cur.fetchone()["MIN(id_imagen)"]

        elif action == 'previous':
            # Get the previous image index
            cur.execute(f"SELECT MAX(id_imagen) FROM {pull_table_images_name} WHERE id_imagen < %s", (current_indice,))
            new_indice = cur.fetchone()["MAX(id_imagen)"]

        # Update the session and database with the new index
        if new_indice:
            session['indice'] = new_indice
            cur.execute("UPDATE usuarios SET indice = %s WHERE usuarioid = %s", (new_indice, user_id))
            mysql.connection.commit()

        cur.close()

        # Return the updated count along with success
        return jsonify({"success": True, "indice": new_indice, "num_imagenes_clasificadas": num_imagenes_clasificadas})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
