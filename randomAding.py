import mysql.connector
import random
import string
from datetime import datetime, timedelta

# 🔹 Conectar a la base de datos
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="Taller_Mecanico"
        )
        return connection
    except Exception as e:
        print("Error en la conexión:", e)
        return None

# 🔹 Generar datos aleatorios según tipo de columna
def random_data(dtype):
    if "int" in dtype:
        return random.randint(1, 9999)
    elif "char" in dtype or "text" in dtype:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    elif "date" in dtype:
        start = datetime(2000, 1, 1)
        end = datetime(2025, 1, 1)
        return start + timedelta(days=random.randint(0, (end - start).days))
    elif "decimal" in dtype or "float" in dtype or "double" in dtype:
        return round(random.uniform(10, 9999), 2)
    else:
        return None

# 🔹 Insertar datos random en todas las tablas
def fill_database(connection, rows_per_table=5):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

        col_names = []
        col_types = []
        for col in columns:
            if "auto_increment" in col[5].lower():
                continue
            col_names.append(col[0])
            col_types.append(col[1])

        for _ in range(rows_per_table):
            values = []
            for dtype in col_types:
                val = random_data(dtype)
                if isinstance(val, str):
                    values.append(f"'{val}'")
                elif isinstance(val, datetime):
                    values.append(f"'{val.date()}'")
                elif val is None:
                    values.append("NULL")
                else:
                    values.append(str(val))

            query = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({', '.join(values)})"
            try:
                cursor.execute(query)
            except Exception as e:
                print(f"❌ Error insertando en {table_name}: {e}")

        connection.commit()
        print(f"✅ Insertados {rows_per_table} registros en {table_name}")

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        fill_database(conn, rows_per_table=10)  # cambia el número de filas que quieras
        conn.close()
