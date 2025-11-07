from flask import Flask, render_template, request, redirect, url_for
from backend.auth import register_user,login_user

app = Flask(__name__, template_folder='frontend')

@app.route("/")
def home():
    return redirect(url_for('login'))  # langsung ke login

@app.route("/login", methods=['GET','POST'])
def login():
    error = None
    email = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        success, message = login_user(email, password)
        if success:
            return redirect(url_for('index'))
        else:
            error = message

    return render_template("login.html", error=error, email=email)

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if len(password) < 8:
            return render_template("register.html", error="Password harus minimal 8 karakter!")

        if password != confirm:
            return render_template("register.html", error="Password tidak cocok!")
        success, message = register_user(username, email, password)
        if not success:
            # kirim pesan error ke template
            return render_template("register.html", error=message)
    
        if success:
            return redirect(url_for("login"))
        else:
            return message

    return render_template("register.html")

@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
