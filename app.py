from flask import Flask, render_template, request, redirect, url_for, session
from backend.auth import register_user,login_user
from backend.superteks_algo import add_note, get_notes

app = Flask(__name__, template_folder='frontend')
app.secret_key = 'kunci_session_bebas'

@app.route("/")
def home():
    return redirect(url_for('login'))  # langsung ke login

@app.route("/login", methods=['GET','POST'])
def login():
    # Jika user sudah login, arahkan ke index
    if 'user_email' in session:
        return redirect(url_for('index'))
    error = None
    email = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        success, message, username, user_id = login_user(email, password)
        if success:
            # SET SESSION
            session['user_email'] = email
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            error = message

    return render_template("login.html", error=error, email=email)

@app.route("/register", methods=['GET','POST'])
def register():
    # Jika user sudah login, arahkan ke index
    if 'user_email' in session:
        return redirect(url_for('index'))
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
    # Cek apakah user sudah login
    if 'user_email' not in session:
        return redirect(url_for('login'))  # jika belum login, arahkan ke login
    user_id = session['user_id']
    notes = get_notes(user_id)  # sudah mengembalikan list dict dengan title & note didekripsi
    total_notes = len(notes)
    return render_template("index.html", user_email=session['user_email'],  username = session.get('username', 'Guest'), notes=notes, total_notes=total_notes)

@app.route("/add_note", methods=["POST"])
def add_note_route():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    note = request.form['note']
    user_id = session['user_id']  
    add_note(user_id, title, note)
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    # Hapus session user
    session.pop('user_email', None)
    return redirect(url_for('login')) + '#mynotes-section'

if __name__ == "__main__":
    app.run(debug=True)
