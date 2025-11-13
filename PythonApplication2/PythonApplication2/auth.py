import pyodbc

#Conexión a la base de datos SQL Server
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
    
    #Se verifica si existe el correo en la tabla Usuarios
    cursor.execute("SELECT id, password_hash, estado FROM Usuarios WHERE correo = ?", (correo,))
    user = cursor.fetchone()

    if not user:
        #Si el usuario no existe entonces se guarda un registro en auditoria_login
        cursor.execute(
            "INSERT INTO auditoria_login (correo, motivo) VALUES (?, ?)",
            (correo, "NO_REGISTRADO")
        )
        conn.commit()
        #Retorna que el usuario no fue encontrado
        return {"resultado": "error", "code": "USER_NOT_FOUND"}

    #Si existe el usuario
    return {"resultado": "ok", "usuario_id": user[0]}

#ejemplos
print(login("noexiste@example.com", "abc123"))   #Se prueba con un correo que no existe
print(login("user1@example.com", "abc123"))      #Se prueba con un correo que si existe


