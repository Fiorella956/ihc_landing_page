import pyodbc

# Datos de conexión
server = r'DESKTOP-177AQC0\MSSQLSERVER01'
database = 'AuthDB'

conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
)
cursor = conn.cursor()

def login(correo, password):
    # Verificar si existe el correo
    cursor.execute("SELECT id, password_hash, estado FROM Usuarios WHERE correo = ?", (correo,))
    user = cursor.fetchone()

    if not user:
        # Insertar en la tabla auditoria si no existe el correo
        cursor.execute(
            "INSERT INTO auditoria (correo, motivo) VALUES (?, ?)",
            (correo, "NO_REGISTRADO")
        )
        conn.commit()
        return {"status": "error", "code": "USER_NOT_FOUND"}

    # Si el correo existe (por ahora no validamos contraseña ni estado, eso es otra tarea)
    return {"status": "ok", "usuario": user[0]}

# ------------------------
# PRUEBA: usuario que no existe
print(login("noexiste@example.com", "abc123"))

# PRUEBA: usuario que sí existe (ejemplo de los que sembraste en la tabla Usuarios)
print(login("user1@example.com", "abc123"))
