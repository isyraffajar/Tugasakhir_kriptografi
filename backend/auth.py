import hashlib
from backend.db import get_db
from backend.blowfish_algo import encrypt_blowfish, decrypt_blowfish

def register_user(username, email, password):
    conn = get_db()
    cursor = conn.cursor()

    # Enkripsi username dan email dgn BLOWFISH
    username_enc = encrypt_blowfish(username)
    email_enc = encrypt_blowfish(email)

    # cek apakah sudah ada user
    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username_enc, email_enc))
    existing = cursor.fetchone()

    if existing:
        return False, "Username atau email sudah digunakan!"

    # hash password SHA-512
    hash_obj = hashlib.sha512(password.encode())
    password_hash = hash_obj.hexdigest()

    # simpan ke database
    sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(sql, (username_enc, email_enc, password_hash))
    conn.commit()
    return True, "Register berhasil!"

def login_user(email, password):
    """
    Fungsi untuk login user.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Enkripsi email input dgn BLOWFISH
    email_enc = encrypt_blowfish(email)

    # Ambil hash password dari database berdasarkan email 
    # Ambil username dan user_id jg untuk session
    cursor.execute("SELECT user_id, password_hash, username FROM users WHERE email=%s", (email_enc,))
    result = cursor.fetchone()

    if not result:
        return False, "Email tidak ditemukan!"

    user_id, stored_hash, username_enc = result
    username = decrypt_blowfish(username_enc)  # dekripsi username

    # Hash password input
    password_hash = hashlib.sha512(password.encode()).hexdigest()

    # Cek kecocokan
    if password_hash == stored_hash:
        return True, "Login berhasil!", username, user_id
    else:
        return False, "Password salah!", None, None
