import pyodbc

# Conexión usando Autenticación de Windows
server = r'DESKTOP-177AQC0\MSSQLSERVER01'   # Nombre de tu servidor
database = 'master'                         # Base de datos de prueba

try:
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION;")  # Consulta de prueba
    row = cursor.fetchone()
    print("✅ Conexión exitosa a SQL Server con Windows Authentication")
    print("Versión:", row[0])

    conn.close()
except Exception as e:
    print("❌ Error al conectar:", e)
