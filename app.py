from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename
from backend.EOF_algo import embed_text_eof, extract_text_eof
from PIL import Image
import io
from backend.file_db_ops import add_file, get_files_by_user, get_file_for_download, delete_file
from backend.auth import register_user,login_user
from backend.superteks_algo import add_note, get_notes, update_note, delete_note

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
    username = session.get('username', 'Guest')
    notes = get_notes(user_id)  # sudah mengembalikan list dict dengan title & note didekripsi
    files = get_files_by_user(user_id)
    total_notes = len(notes)
    total_files = len(files)
    return render_template("index.html", user_email=session['user_email'],  username=username, notes=notes, total_notes=total_notes, files=files, total_files=total_files)

@app.route("/add_note", methods=["POST"])
def add_note_route():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    note = request.form['note']
    user_id = session['user_id']  
    add_note(user_id, title, note)
    return redirect(url_for('index'))

@app.route("/update_note", methods=["POST"])
def update_note_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    note_id = request.form['note_id']
    title = request.form['title']
    note = request.form['note']
    user_id = session['user_id']

    update_note(user_id, note_id, title, note)

    return redirect(url_for('index') + "#mynotes-section")

@app.route("/delete_note", methods=["POST"])
def delete_note_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    note_id = request.form['note_id']
    user_id = session['user_id']

    # Hapus catatan dari database
    delete_note(user_id, note_id)

    return redirect(url_for('index') + "#mynotes-section")

@app.route("/upload_file", methods=["POST"])
def upload_file_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash("Tidak ada file yang dipilih", "danger")
        return redirect(url_for('dashboard'))
        
    file = request.files['file']
    
    if file.filename == '':
        flash("Tidak ada file yang dipilih", "danger")
        return redirect(url_for('dashboard'))
        
    if file:
        user_id = session['user_id']
        filename = secure_filename(file.filename) # Ambil nama file asli
        file_data = file.read() # Baca data biner file
        
        # Panggil fungsi DB Anda
        add_file(user_id, filename, file_data)
        
        flash("File berhasil di-upload dan dienkripsi!", "success")
        
    return redirect(url_for('index')) # Arahkan kembali ke dashboard

@app.route("/download_file/<int:file_id>")
def download_file_route(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    filename, file_data = get_file_for_download(user_id, file_id)
    
    if filename is None:
        flash("File tidak ditemukan atau Anda tidak punya akses.", "danger")
        return redirect(url_for('dashboard'))
        
    # Kirim file kembali ke browser
    return send_file(
        io.BytesIO(file_data),
        as_attachment=True,
        download_name=filename # Nama file saat di-download
    )

@app.route("/delete_file/<int:file_id>", methods=["POST"])
def delete_file_route(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Panggil fungsi hapus dari file_db_ops
    if delete_file(user_id, file_id):
        flash("File berhasil dihapus.", "success")
    else:
        flash("Gagal menghapus file. File tidak ditemukan atau Anda tidak memiliki izin.", "danger")
        
    return redirect(url_for('dashboard'))

@app.route("/steg_hide", methods=["POST"])
def steg_hide():
    f = request.files.get("cover")
    message = request.form.get("message", "")
    if not f or not message:
        return "Gambar dan pesan dibutuhkan", 400

    file_bytes = f.read()
    stego_bytes = embed_text_eof(file_bytes, message)

    return send_file(
        io.BytesIO(stego_bytes),
        mimetype=f.mimetype,
        as_attachment=True,
        download_name="stego_" + f.filename
    )

@app.route("/steg_extract", methods=["POST"])
def steg_extract():
    f = request.files.get("stego")
    if not f:
        return "File stego dibutuhkan", 400

    file_bytes = f.read()
    message = extract_text_eof(file_bytes)
    return render_template("index.html", extracted_message=message, active_tab="reveal")


@app.route("/logout")
def logout():
    # Hapus session user
    session.pop('user_email', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
