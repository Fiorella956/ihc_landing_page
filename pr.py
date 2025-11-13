import pyodbc

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
        # Insertar en auditoría
        cursor.execute(
            "INSERT INTO Auditoria_Login (correo, motivo) VALUES (?, ?)",
            (correo, "NO_REGISTRADO")
        )
        conn.commit()
        return {"status": "error", "code": "USER_NOT_FOUND"}

    # Aquí luego se compara password con el hash (pendiente para otra tarea)
    return {"status": "ok", "usuario": user[0]}

# Probar con un usuario que no existe
print(login("noexiste@example.com", "abc123"))
