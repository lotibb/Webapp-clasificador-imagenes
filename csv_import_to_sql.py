import pymysql
import pandas as pd
from urllib.parse import urlparse

# Load the CSV data (treat the first row as data, not column names)
file_path = 'D:/IG/links_ovh_cloud/control_calidad_atributo_en_obra.csv'
data = pd.read_csv(file_path, header=None)

# Table name as a variable
table_name = "solidaridad_imagenes"

# Connect to your existing MySQL database
connection = pymysql.connect(
    host='localhost',  # Update with your MySQL host
    user='root',       # Update with your MySQL username
    password='aMerica8dic&?',  # Update with your MySQL password
    database='webapp_image_viewer'  # Update with your database name
)

try:
    with connection.cursor() as cursor:
        # Create the table dynamically using the variable
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id_imagen INT AUTO_INCREMENT PRIMARY KEY,
            image_url TEXT NOT NULL,
            imagen_nombre VARCHAR(255) NOT NULL
        );
        """
        cursor.execute(create_table_sql)

        # Prepare data for bulk insertion
        insert_data = []
        for _, row in data.iterrows():
            image_url = row[0]  # Use the first column (index 0) for the URL
            image_name = urlparse(image_url).path.split("/")[-1]  # Extract the image name from the URL
            insert_data.append((image_url, image_name))

        # Bulk insert data
        insert_sql = f"INSERT INTO {table_name} (image_url, imagen_nombre) VALUES (%s, %s)"
        cursor.executemany(insert_sql, insert_data)

        # Commit the transaction
        connection.commit()
        print(f"Data successfully inserted into the `{table_name}` table.")

except Exception as e:
    print("An error occurred:", e)

finally:
    connection.close()
