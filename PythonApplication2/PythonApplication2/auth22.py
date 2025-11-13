import pyodbc
import bcrypt
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# -------- Conexion a la base de datos -------- #
def conexion():
    server = r'DESKTOP-177AQC0\MSSQLSERVER01'
    database = 'AuthDB'
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )
    return conn


# -------- Recuperacion de contrasena: START -------- #
@app.route('/auth/recovery/start', methods=['POST'])
def recovery_start():
    data = request.get_json()
    correo = data.get('correo')

    if not correo:
        return jsonify({"status": "error", "message": "Correo requerido"}), 400

    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, estado FROM Usuarios WHERE correo = ?", (correo,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "USER_NOT_FOUND"}), 404

    usuario_id, estado = user
    if estado.upper() == "SUSPENDIDO":
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "ACCOUNT_SUSPENDED"}), 403

    # Generar token y vencimiento
    token = str(uuid.uuid4())
    vence_en = datetime.now() + timedelta(minutes=30)

    cursor.execute(
        "INSERT INTO tokens_reset (usuario_id, token, vence_en) VALUES (?, ?, ?)",
        (usuario_id, token, vence_en)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "ok", "message": "Token generado", "token": token})


# -------- Recuperacion de contrasena: CONFIRM -------- #
@app.route('/auth/recovery/confirm', methods=['POST'])
def recovery_confirm():
    data = request.get_json()
    correo = data.get('correo')
    token = data.get('token')
    nueva_password = data.get('nueva_password')

    if not correo or not token or not nueva_password:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    conn = conexion()
    cursor = conn.cursor()

    # Buscar usuario
    cursor.execute("SELECT id, estado FROM Usuarios WHERE correo = ?", (correo,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "USER_NOT_FOUND"}), 404

    usuario_id, estado = user
    if estado.upper() == "SUSPENDIDO":
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "ACCOUNT_SUSPENDED"}), 403

    # Validar token
    cursor.execute(
        "SELECT vence_en FROM tokens_reset WHERE usuario_id = ? AND token = ?",
        (usuario_id, token)
    )
    token_row = cursor.fetchone()
    if not token_row:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "TOKEN_INVALID"}), 400

    vence_en = token_row[0]
    if datetime.now() > vence_en:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "TOKEN_EXPIRED"}), 400

    # Actualizar contrasena
    password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("UPDATE Usuarios SET password_hash = ? WHERE id = ?", (password_hash, usuario_id))

    # Eliminar el token usado
    cursor.execute("DELETE FROM tokens_reset WHERE usuario_id = ? AND token = ?", (usuario_id, token))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "ok", "message": "Contrasena actualizada correctamente"})


# -------- Ruta de prueba -------- #
@app.route('/', methods=['GET'])
def index():
    return "Servicio AuthDB funcionando. Endpoints: /auth/recovery/start y /auth/recovery/confirm"


# -------- Inicialización -------- #
if __name__ == "__main__":
    print("Servicio listo. Ejecutando Flask...")
    app.run(debug=True)
