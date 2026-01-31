from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

admin_user = "admin"
admin_password = "cloud2026"

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

    if data["username"] == admin_user and data["password"] == admin_password:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    
if __name__ == "__main__":
    app.run(debug=True)