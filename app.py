from flask import Flask, request, jsonify, render_template
import pymysql

app = Flask(__name__)

def get_admin():
    connection = pymysql.connect(
        host="database-1.cl0qai0s4ajo.us-west-2.rds.amazonaws.com",
        user="user_system",
        password="csd425cloud2026",
        port="3306",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, password FROM users WHERE username='admin'")
            return cursor.fetchone()
    finally:        
        connection.close()

# route to html
@app.route("/")
def index():
    return render_template("index.html")

# route to login page
@app.route("/login")
def login_page():
    return render_template("login.html")

# route to landing page (after successful login)
@app.route("/landing")
def landing():
    return render_template("landing.html")

# route to handle login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    db_admin = get_admin()

    if data["username"] == db_admin["username"] and data["password"] == db_admin["password"]:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    
if __name__ == "__main__":
    app.run(debug=True)