from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
import base64

# Kunci Blowfish (harus bytes, 4-56 byte panjangnya)
BLOWFISH_KEY = b"ini_kunci_blowfish"
BLOCK_SIZE = Blowfish.block_size  # 8 bytes

def encrypt_blowfish(plaintext: str) -> str:
    """
    Enkripsi string plaintext menjadi string Base64.
    """
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_ECB)
    plaintext_bytes = plaintext.encode('utf-8')
    padded_text = pad(plaintext_bytes, BLOCK_SIZE)
    ciphertext = cipher.encrypt(padded_text)
    # encode ke Base64 supaya bisa disimpan di DB
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt_blowfish(ciphertext_b64: str) -> str:
    """
    Dekripsi string Base64 ciphertext menjadi string plaintext.
    """
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_ECB)
    ciphertext_bytes = base64.b64decode(ciphertext_b64)
    decrypted_padded = cipher.decrypt(ciphertext_bytes)
    plaintext_bytes = unpad(decrypted_padded, BLOCK_SIZE)
    return plaintext_bytes.decode('utf-8')
