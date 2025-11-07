from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from backend.playfair_algo import playfair_encrypt, playfair_decrypt
from backend.db import get_db
import base64


# ----------------------------
# DES3
# ----------------------------

# Kunci DES3 
DES3_KEY = b"thisis24bytekey123456789"  # 24 bytes

def encrypt_3des(plaintext: str) -> bytes:
    cipher = DES3.new(DES3_KEY, DES3.MODE_ECB)  
    data = plaintext.encode('utf-8')
    ciphertext = cipher.encrypt(pad(data, DES3.block_size))
    return ciphertext

def decrypt_3des(ciphertext: bytes) -> str:
    cipher = DES3.new(DES3_KEY, DES3.MODE_ECB)
    decrypted = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return decrypted.decode('utf-8')



# ----------------------------
# Super Enkripsi (Playfair + 3DES)
# ----------------------------
def super_encrypt(text: str, pf_key: str) -> bytes:
    """Enkripsi gabungan: Playfair + 3DES"""
    pf_text = playfair_encrypt(text, pf_key)
    ciphertext_bytes = encrypt_3des(pf_text)
    return base64.b64encode(ciphertext_bytes).decode('utf-8')

def super_decrypt(ciphertext_b64: str, pf_key: str) -> str:
    """Dekripsi gabungan: 3DES -> Playfair"""
    ciphertext_bytes = base64.b64decode(ciphertext_b64.encode('utf-8'))
    pf_text = decrypt_3des(ciphertext_bytes)
    return playfair_decrypt(pf_text, pf_key)


# ----------------------------
# Implementasi ke database
# ----------------------------
PF_KEY = "uaskriptoplayfair"

def add_note(user_id, title, note):
    conn = get_db()
    cursor = conn.cursor()
    
    # Enkripsi title & note
    title_enc = super_encrypt(title, PF_KEY)
    note_enc = super_encrypt(note, PF_KEY)
    
    sql = "INSERT INTO notes (user_id, title, note) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_id, title_enc, note_enc))
    conn.commit()

def get_notes(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "SELECT note_id, title, note, created_at FROM notes WHERE user_id=%s ORDER BY created_at DESC"
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    
    notes = []
    for note_id, title_enc, note_enc, created_at in rows:
        title = super_decrypt(title_enc, PF_KEY)
        note = super_decrypt(note_enc, PF_KEY)
        notes.append({
            "note_id": note_id,
            "title": title,
            "note": note,
            "created_at": created_at
        })
    return notes

def update_note(user_id, note_id, title, note):
    """
    Update catatan di database dengan enkripsi Playfair + 3DES
    """
    conn = get_db()
    cursor = conn.cursor()

    # Enkripsi title & note
    title_enc = super_encrypt(title, PF_KEY)
    note_enc = super_encrypt(note, PF_KEY)

    sql = "UPDATE notes SET title=%s, note=%s WHERE note_id=%s AND user_id=%s"
    cursor.execute(sql, (title_enc, note_enc, note_id, user_id))
    conn.commit()

def delete_note(user_id, note_id):
    """
    Hapus catatan berdasarkan note_id dan user_id
    """
    conn = get_db()
    cursor = conn.cursor()
    sql = "DELETE FROM notes WHERE note_id=%s AND user_id=%s"
    cursor.execute(sql, (note_id, user_id))
    conn.commit()
