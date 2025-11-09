# file_db_ops.py
from backend.db import get_db
from backend.blowfish_algo import encrypt_blowfish, decrypt_blowfish
from backend.file_crypto import encrypt_file_data, decrypt_file_data

def add_file(user_id, filename, file_data):
    """
    Enkripsi dan simpan file ke database.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Enkripsi nama file (bisa pakai Blowfish-ECB/Base64 Anda)
    filename_enc = encrypt_blowfish(filename)
    
    # 2. Enkripsi data file (WAJIB pakai CBC baru)
    file_data_enc = encrypt_file_data(file_data)
    
    sql = """
        INSERT INTO files (user_id, filename, file_data) 
        VALUES (%s, %s, %s)
    """
    # Simpan filename terenkripsi dan file_data terenkripsi
    cursor.execute(sql, (user_id, filename_enc, file_data_enc))
    conn.commit()

def get_files_by_user(user_id):
    """
    Ambil daftar file untuk user, dekripsi nama filenya untuk ditampilkan.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "SELECT file_id, filename, uploaded_at FROM files WHERE user_id=%s ORDER BY uploaded_at DESC"
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    
    files = []
    for file_id, filename_enc, uploaded_at in rows:
        files.append({
            "file_id": file_id,
            "filename": decrypt_blowfish(filename_enc), # Dekripsi nama file
            "uploaded_at": uploaded_at
        })
    return files

def get_file_for_download(user_id, file_id):
    """
    Ambil satu file (data dan nama) untuk di-download.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "SELECT filename, file_data FROM files WHERE user_id=%s AND file_id=%s"
    cursor.execute(sql, (user_id, file_id))
    result = cursor.fetchone()
    
    if not result:
        return None, None
        
    filename_enc, file_data_enc = result
    
    # 1. Dekripsi nama file
    filename = decrypt_blowfish(filename_enc)
    
    # 2. Dekripsi data file
    file_data = decrypt_file_data(file_data_enc)
    
    return filename, file_data

def delete_file(user_id, file_id):
    """
    Hapus file dari database, HANYA jika user_id cocok.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Perintah SQL DELETE
        # PENTING: Cek user_id DAN file_id untuk keamanan
        sql = "DELETE FROM files WHERE user_id = %s AND file_id = %s"
        cursor.execute(sql, (user_id, file_id))
        conn.commit()
        
        # Cek apakah ada baris yang terhapus
        if cursor.rowcount > 0:
            return True # Sukses
        else:
            return False # Gagal (file tidak ditemukan atau bukan milik user)
            
    except Exception as e:
        print(f"Error saat menghapus file: {e}")
        return False