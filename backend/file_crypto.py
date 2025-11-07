# file_crypto.py
from Crypto.Cipher import CAST
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Kunci CAST-128 (HARUS 16 bytes / 128 bits)
CAST_KEY = b'ini_kunci_16_byte' 

# CAST-128 (seperti Blowfish) memiliki blok 8 bytes
BLOCK_SIZE = CAST.block_size  # Ini akan menjadi 8 bytes

def encrypt_file_data(data: bytes) -> bytes:
    """
    Enkripsi data file (bytes) menggunakan CAST-128 dalam mode CBC.
    
    PERINGATAN: Ukuran blok 8-byte tidak ideal untuk enkripsi
    file bervolume besar karena risiko serangan Sweet32.
    
    Format output: [IV][CIPHERTEXT]
    """
    
    # 1. Buat IV (Initialization Vector) acak
    iv = get_random_bytes(BLOCK_SIZE) # 8 bytes
    
    # 2. Buat cipher
    cipher = CAST.new(CAST_KEY, CAST.MODE_CBC, iv)
    
    # 3. Pad data agar pas dengan ukuran blok
    padded_data = pad(data, BLOCK_SIZE)
    
    # 4. Enkripsi
    ciphertext = cipher.encrypt(padded_data)
    
    # 5. Gabungkan IV di awal ciphertext agar bisa dipakai untuk dekripsi
    return iv + ciphertext

def decrypt_file_data(data: bytes) -> bytes:
    """
    Dekripsi data file (bytes) dari format CAST-128 CBC.
    Membaca [IV][CIPHERTEXT]
    """
    try:
        # 1. Ekstrak IV (8 byte pertama)
        iv = data[:BLOCK_SIZE]
        
        # 2. Ekstrak ciphertext (sisanya)
        ciphertext = data[BLOCK_SIZE:]
        
        # 3. Buat cipher
        cipher = CAST.new(CAST_KEY, CAST.MODE_CBC, iv)
        
        # 4. Dekripsi
        decrypted_padded = cipher.decrypt(ciphertext)
        
        # 5. Unpad data
        plaintext = unpad(decrypted_padded, BLOCK_SIZE)
        
        return plaintext
        
    except (ValueError, KeyError) as e:
        # Error ini bisa terjadi jika kunci salah, IV salah,
        # atau data korup/padding rusak.
        print(f"Error dekripsi CAST-128: {e}")
        return None # Kembalikan None jika gagal