from flask import Flask, render_template, jsonify, send_from_directory, request, session, url_for
from flask_mysqldb import MySQL
import os
from config_image_pull import Config
import shutil

app = Flask(__name__, template_folder='template')
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

        # Fetch user from the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE nmusuario = %s AND contraseña = %s', (_nmusuario, _contraseña,))
        account = cur.fetchone()
        cur.close()

        if account:
            # Set session data
            session['logueado'] = True
            session['id'] = account['usuarioid']
            session['username'] = account['nmusuario']

            # Fetch the user's base path and folders
            user_config = app.config['USER_DIRECTORY_CONFIG'].get(account["nmusuario"])
            if not user_config:
                return f"No folder configuration found for user '{account['nmusuario']}'", 404

            base_path = user_config.get("base_path")
            folders = user_config.get("folders", [])  # List of folders

            if not base_path or not os.path.exists(base_path):
                return f"No base path found or accessible for user '{account['nmusuario']}'", 404

            # Fetch images only directly within the base path
            image_files = sorted(
                [
                    file for file in os.listdir(base_path)
                    if os.path.isfile(os.path.join(base_path, file)) and file.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))
                ]
            )
            image_urls = [
                url_for('serve_image', username=account["nmusuario"], filename=img) for img in image_files
            ]

            return render_template(
                "image_clas.html",
                nombre_usuario=account["nmusuario"],
                atri_clas=account["atributo_clasificando"],
                num_imagenes_clasificadas=account["num_imagenes_clasificadas"],
                images=image_urls,
                folders=folders  # Pass folders to template
            )
        else:
            return render_template('index.html', mensaje="Usuario O Contraseña Incorrectas")
    return render_template('index.html')



@app.route('/images/<username>/<filename>')
def serve_image(username, filename):
    """
    Serve an image from the user's base directory.
    """
    user_config = app.config['USER_DIRECTORY_CONFIG'].get(username)

    if not user_config:
        return f"No folder configuration found for user '{username}'", 404

    base_path = user_config.get("base_path")
    if not base_path or not os.path.exists(base_path):
        return f"No base path found or accessible for user '{username}'", 404

    return send_from_directory(base_path, filename)

@app.route('/move-image', methods=['POST'])
def move_image():
    """
    Move the current image to the selected folder.
    """
    data = request.json
    image = data.get('image')
    folder = data.get('folder')

    if not image or not folder:
        return jsonify({'error': 'Invalid data provided'}), 400

    # Debugging Logs
    print(f"Request to move image: {image} to folder: {folder}")

    user_config = app.config['USER_DIRECTORY_CONFIG'].get(session['username'])
    if not user_config:
        return jsonify({'error': 'User configuration not found'}), 404

    base_path = user_config['base_path']
    folder_path = os.path.join(base_path, folder)

    # Validate paths
    source_path = os.path.join(base_path, image)
    destination_path = os.path.join(folder_path, image)

    print(f"Source Path: {source_path}")
    print(f"Destination Path: {destination_path}")

    if not os.path.exists(source_path):
        return jsonify({'error': f"Image '{image}' not found at {source_path}"}), 404

    # Ensure folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        shutil.move(source_path, destination_path)
        print(f"Image '{image}' moved successfully!")
        return jsonify({'message': f"Image '{image}' moved to folder '{folder}'"}), 200
    except Exception as e:
        print(f"Error moving image: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.secret_key = app.config.get('SECRET_KEY', 'default_secret_key')  # Ensure a secure key
    app.run(debug=True)
