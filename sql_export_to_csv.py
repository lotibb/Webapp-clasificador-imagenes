import pymysql
import pandas as pd

# Table name and output file name as variables
table_name = "solidaridad_imagenes"  # Replace with the table name
output_file = "resultados_solidaridad_imagenes.csv"  # Replace with the desired CSV file name

# Connect to your existing MySQL database
connection = pymysql.connect(
    host='localhost',  # Update with your MySQL host
    user='root',       # Update with your MySQL username
    password='aMerica8dic&?',  # Update with your MySQL password
    database='webapp_image_viewer'  # Update with your database name
)


try:
    # Read the entire table into a pandas DataFrame
    query = f"SELECT * FROM {table_name};"
    data = pd.read_sql(query, connection)
    
    # Export the DataFrame to a CSV file
    data.to_csv(output_file, index=False)
    print(f"Data successfully exported to `{output_file}`.")

except Exception as e:
    print("An error occurred:", e)

finally:
    connection.close()
