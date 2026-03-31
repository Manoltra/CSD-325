from flask import Flask, request, jsonify, render_template, make_response
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
import pymysql
import cryptography
import secrets
from datetime import datetime, timedelta
import boto3
# import bcrypt
app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
ses = boto3.client("ses", region_name="us-west-2")

'''
Database
'''
# Establishes a connection to the RDS database
def get_connection():
    return pymysql.connect(
        host="database-1.cl0qai0s4ajo.us-west-2.rds.amazonaws.com",
        user="admin",
        password="csd425cloud2026",
        database="user_system",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

# Queries a user given their username
def get_user(username):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = "SELECT username, password_hash FROM users WHERE username=%s"
            cursor.execute(sql, (username,))
            return cursor.fetchone()
    except Exception as e:
        print("get_user() error: ", e)
    finally:        
        connection.close()

# Inserts a new username and password into the database
def insert_user(username, password):
    try:
        connection = get_connection()
        password_hash = hash_password(password)
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
            cursor.execute(sql, (username, password_hash))
        connection.commit()
        return True
    except Exception as e:
        print("insert_user() error: ", e)
        connection.rollback()
        return False
    finally:        
        connection.close()

# Updates an existing username and password in the database
def update_user(old_username, old_password, new_username, new_password):
    try:
        connection = get_connection()

        old_password_hash = hash_password(old_password)
        new_password_hash = hash_password(new_password)

        with connection.cursor() as cursor:
            sql = """
                UPDATE users
                SET username = %s, password_hash = %s
                WHERE username = %s AND password_hash = %s
            """
            cursor.execute(sql, (new_username, new_password_hash, old_username, old_password_hash))

        connection.commit()

        # Check if a row was actually updated
        if cursor.rowcount == 0:
            return False
        return True

    except Exception as e:
        print("update_user() error:", e)
        connection.rollback()
        return False

    finally:
        connection.close()

# Creates a new mfa session with relevant info
def insert_mfa(username):
    code = generate_code()
    now = datetime.utcnow()
    expires = now + timedelta(minutes=5)
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO mfa_codes (username, code, created_at, expires_at, used)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (username, code, now, expires, False))
        connection.commit()
        return True
    except Exception as e:
        print("insert_mfa() error: ", e)
        connection.rollback()
        return False
    finally:        
        connection.close()

# Returns an mfa session stored in mfa_codes
def get_mfa(username, submitted_code=None):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                SELECT *
                FROM mfa_codes
                WHERE username=%s
                  AND used=FALSE
                  AND expires_at > UTC_TIMESTAMP()
            """
            params = [username]
            if submitted_code:
                sql += " AND code=%s"
                params.append(submitted_code)
            sql += " ORDER BY created_at DESC LIMIT 1"
            cursor.execute(sql, tuple(params))
            return cursor.fetchone()
    except Exception as e:
        print("get_mfa() error: ", e)
    finally:
        connection.close()

# Updates field in mfa_codes table to be marked as used
def update_mfa(mfa_id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE mfa_codes SET used=TRUE WHERE id=%s"
            cursor.execute(sql, (mfa_id,))
        connection.commit()
    except Exception as e:
        print("update_mfa() error: ", e)
        connection.rollback()
    finally:
        connection.close()
'''
Security
'''
# Generates mfa code
def generate_code():
    return str(secrets.randbelow(900000) + 100000)

# Compares input unhashed and stored hashed passwords.
def verify_password(password, stored_hash): 
    '''
    password_bytes = password.encode('utf-8')
    stored_hash_bytes = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_hash_bytes)
    '''
    return password == stored_hash

# Hashes a password
def hash_password(password): 
    '''
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return password_hash_bytes.decode('utf-8')
    '''
    return password
'''
Routing
'''
# Route to handle login authentication
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return make_response("", 200)
    
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({
            "success": False,
            "message": "Username and password are required"
        }), 400
    username = data["username"]
    password = data["password"]
    db_user = get_user(username)
    if not db_user or not verify_password(password, db_user["password_hash"]):
        return jsonify({
        "success": False,
        "message": "Invalid credentials"
        }), 401
    if insert_mfa(username):
        return jsonify({
        "success": True,
        "mfa_required": True,
        "username": username,   # frontend stores temporarily
        "redirect": "mfa.html"
    }), 200
    else:
        return jsonify({
        "success": False,
        "message": "Failed to establish MFA session"
        }), 401  
        
# Route to handle registration
@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return make_response("", 200)
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400
    username = data["username"]
    password = data["password"]
    db_user = get_user(username)
    if db_user:
        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 409
    elif insert_user(username, password):
        return jsonify({
        "success": True
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Error: registration failed"
        }), 500    

# Route for sending mfa code to email
@app.route("/send-mfa", methods=["POST"])
def send_mfa():
    try:
        data = request.get_json()
        username = data["username"]
        db_mfa = get_mfa(username)
        if not db_mfa:
            return jsonify({
                "success": False,
                "message": "Failed to find MFA session"
                }), 400
        print("Sending email")
        response = ses.send_email(
            Source="csd415lwtech@gmail.com",
            Destination={"ToAddresses": ["S-Alexander.Covi@lwtech.edu"]}, # Originally [username]
            # Destination={"ToAddresses": [username]},
            Message={
                "Subject": {"Data": "Your MFA Code"},
                "Body": {"Text": {"Data": f"Your code is {db_mfa['code']}"}}
            }
        )
        print("SES response:", response)
        return jsonify({"success": True}), 200
    except Exception as e:
        print("send_mfa() error: ", e)
        return jsonify({"success": False, "message": str(e)}), 500

# Route for verifying user's inputted code
@app.route("/verify-mfa", methods=["POST"])
def verify_mfa():
    data = request.get_json()
    username = data["username"]
    submitted_code = data["code"]
    action = data["action"]
    db_mfa = get_mfa(username, submitted_code)

    if not db_mfa:
        return jsonify({"success": False, "message": "Invalid or expired code"}), 401
    update_mfa(db_mfa["id"])

    if (action == "login"):
        return jsonify({
            "success": True,
            "redirect": "landing.html"
        }), 200
    elif (action == "update"):
        return jsonify({
            "success": True,
            "redirect": "landing.html"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Error. No action supplied."
        }), 400

# Route for updating user
@app.route("/update-username", methods=["POST", "OPTIONS"])
def update_username():
    print("update_username() called")
    if request.method == "OPTIONS":
        return make_response("", 200)
    data = request.get_json()
    if not data:
         return jsonify({
            "success": False,
            "message": "Error: No data received"
        }), 400
    elif "old_username" not in data or "old_password" not in data:
        return jsonify({
            "success": False,
            "message": "Old email and password are required"
        }), 400
    elif "new_username" not in data or "new_password" not in data:
        return jsonify({
            "success": False,
            "message": "New email and password are required"
        }), 400
    old_username = data["old_username"]
    old_password = data["old_password"]
    print("Incoming data received")
    old_user = get_user(old_username)
    if not old_user:
        return jsonify({
            "success": False,
            "message": "Old email doesn't exist"
        }), 409
    print("Old data verified")
    new_username = data["new_username"]
    new_password = data["new_password"]

    if new_username != old_username: # Fails if username belongs to someone else.
        new_user = get_user(new_username)
        if new_user:
            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 409
    print("New data verified")
    if update_user(old_username, old_password, new_username, new_password):
        return jsonify({
        "success": True
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Error: Update failed. Data is unchanged."
        }), 500    
    print("Update complete")
handler = Mangum(asgi_app, lifespan="off")