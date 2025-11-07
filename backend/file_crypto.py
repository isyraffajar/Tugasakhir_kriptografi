# file_crypto.py
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

# Kunci yang sama dengan blowfish_algo.py
BLOWFISH_KEY = b"ini_kunci_blowfish"
BLOCK_SIZE = Blowfish.block_size  # 8 bytes

def encrypt_file_data(data: bytes) -> bytes:
    """
    Enkripsi data file (bytes) menggunakan Blowfish-CBC.
    Menghasilkan IV acak dan menyimpannya di awal ciphertext.
    """
    # Buat IV acak (8 byte)
    iv = get_random_bytes(BLOCK_SIZE)
    
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_CBC, iv)
    
    padded_data = pad(data, BLOCK_SIZE)
    ciphertext = cipher.encrypt(padded_data)
    
    # Kembalikan IV + ciphertext. Ini penting untuk dekripsi!
    return iv + ciphertext

def decrypt_file_data(data: bytes) -> bytes:
    """
    Dekripsi data file (bytes) dari format Blowfish-CBC.
    Membaca IV dari 8 byte pertama data.
    """
    # Ekstrak IV (8 byte pertama)
    iv = data[:BLOCK_SIZE]
    
    # Ekstrak ciphertext (sisanya)
    ciphertext = data[BLOCK_SIZE:]
    
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_CBC, iv)
    
    decrypted_padded = cipher.decrypt(ciphertext)
    
    try:
        plaintext = unpad(decrypted_padded, BLOCK_SIZE)
        return plaintext
    except ValueError as e:
        # Error ini bisa terjadi jika kunci salah atau data korup
        print(f"Error unpadding: {e}")
        return b"Error: Gagal dekripsi file."