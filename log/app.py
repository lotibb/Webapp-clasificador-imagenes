from flask import Flask, render_template, jsonify, request, redirect, session
from flask_mysqldb import MySQL
import os

app = Flask(__name__, template_folder='template')

# Configure app
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aMerica8dic&?'
app.config['MYSQL_DB'] = 'webapp_image_viewer'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = os.environ.get('SECRET_KEY', 'pinchellave')

# Initialize MySQL
mysql = MySQL(app)

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

            return render_template("image_classification.html")
        else:
            return render_template('index.html', mensaje="Usuario O Contraseña Incorrectas")

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

    if action not in ['next', 'previous']:
        return jsonify({"error": "Invalid action"}), 400

    try:
        cur = mysql.connection.cursor()

        # Get current indice
        current_indice = session.get('indice')
        pull_table_images_name = session.get('pull_table_images_name')

        # Update the indice
        if action == 'next':
            cur.execute(f"SELECT MIN(id_imagen) FROM {pull_table_images_name} WHERE id_imagen > %s", (current_indice,))
        else:
            cur.execute(f"SELECT MAX(id_imagen) FROM {pull_table_images_name} WHERE id_imagen < %s", (current_indice,))

        new_indice = cur.fetchone()["MIN(id_imagen)"] if action == 'next' else cur.fetchone()["MAX(id_imagen)"]

        if new_indice:
            session['indice'] = new_indice
            cur.execute("UPDATE usuarios SET indice = %s WHERE usuarioid = %s", (new_indice, session['id']))
            mysql.connection.commit()

        cur.close()
        return jsonify({"success": True, "indice": new_indice})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
