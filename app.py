from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='frontend')

@app.route("/")
def home():
    return redirect(url_for('login'))  # langsung ke login

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # nanti di sini kita cek ke database atau hash password
        # sementara kita tes UI dulu
        if username == "admin" and password == "123":
            return "Login berhasil!"
        else:
            return "Login gagal!"
    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            return "Password tidak cocok!"
        else:
            # sementara hanya test UI
            return f"Register berhasil! Username: {username}, Email: {email}"
    return render_template("register.html")

@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
