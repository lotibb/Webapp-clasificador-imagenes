from flask import Flask, render_template, jsonify, send_from_directory, request, session, url_for
from flask_mysqldb import MySQL
import os
from config_image_pull import Config

app = Flask(__name__,template_folder='template')
app.config.from_object(Config)  # Load configurations from Config

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')   


@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    """
    Handle user login and redirect to the image classification page if successful.
    """
    if request.method == 'POST' and 'txtUsuario' in request.form and 'txtPassword' in request.form:
        _nmusuario = request.form['txtUsuario']
        _contraseña = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE nmusuario = %s AND contraseña = %s', (_nmusuario, _contraseña,))
        account = cur.fetchone()
        cur.close()

        if account:
            # Set session data
            session['logueado'] = True
            session['id'] = account['usuarioid']
            session['username'] = account['nmusuario']

            # Get user data
            user_data = {
                "nombre_usuario": account["nmusuario"],
                "atributo_clasificando": account["atributo_clasificando"],
                "ganancias_mxn": account["ganancias_mxn"]
            }

            # Fetch user-specific images
            user_image_directory = app.config['USER_IMAGE_DIRECTORIES'].get(user_data["nombre_usuario"])
            
            if not user_image_directory or not os.path.exists(user_image_directory):
                return f"No images found for user '{user_data['nombre_usuario']}'", 404

            image_files = sorted(os.listdir(user_image_directory))
            image_urls = [url_for('serve_image', username=user_data["nombre_usuario"], filename=img) for img in image_files]

            return render_template(
                "image_clas.html",
                nombre_usuario=user_data["nombre_usuario"],
                atri_clas=user_data["atributo_clasificando"],
                ganancias_din=user_data["ganancias_mxn"],
                images=image_urls
            )
        else:
            return render_template('index.html', mensaje="Usuario O Contraseña Incorrectas")
    return render_template('index.html')


@app.route('/image-classifier')
def image_classifier():
    """
    Render the image classifier page for the logged-in user.
    """
    if not session.get('logueado'):
        return render_template('index.html', mensaje="Por favor, inicie sesión.")

    username = session.get('username')

    # Fetch user-specific data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE nmusuario = %s", (username,))
    account = cur.fetchone()
    cur.close()

    if not account:
        return f"No user data found for '{username}'", 404

    # Construct the user-specific image directory
    user_image_directory = app.config['USER_IMAGE_DIRECTORIES'].get(username)
    if not user_image_directory or not os.path.exists(user_image_directory):
        return f"No images found for user '{username}'", 404

    # Fetch images for the user
    image_files = sorted(os.listdir(user_image_directory))
    image_urls = [url_for('serve_image', username=username, filename=img) for img in image_files]

    return render_template(
        'image_clas.html',
        images=image_urls,
        nombre_usuario=account['nmusuario'],
        atri_clas=account['atributo_clasificando'],
        ganancias_din=account['ganancias_mxn']
    )


@app.route('/images/<username>/<filename>')
def serve_image(username, filename):
    """
    Serve an image from the user-specific directory.
    """
    user_image_directory = app.config['USER_IMAGE_DIRECTORIES'].get(username)

    if not user_image_directory or not os.path.exists(user_image_directory):
        return f"No directory found for user '{username}'", 404

    return send_from_directory(user_image_directory, filename)


@app.route('/save-position', methods=['POST'])
def save_position():
    """
    Save the user's current position (index) in the database.
    """
    if not session.get('logueado'):
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['id']
    current_index = request.json.get('currentIndex', 0)

    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuarios SET current_index = %s WHERE usuarioid = %s", (current_index, user_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Position saved successfully", "currentIndex": current_index})

@app.route('/get-position', methods=['GET'])
def get_position():
    """
    Get the user's last saved position (index) from the database.
    """
    if not session.get('logueado'):
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT current_index FROM usuarios WHERE usuarioid = %s", (user_id,))
    current_index = cur.fetchone()
    cur.close()

    return jsonify({"currentIndex": current_index['current_index']})

if __name__ == '__main__':
    app.secret_key = app.config.get('SECRET_KEY', 'default_secret_key')  # Ensure a secure key
    app.run(debug=True)
