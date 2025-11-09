# backend/EOF_algo.py
import io
from .blowfish_algo import encrypt_blowfish, decrypt_blowfish

# Marker unik untuk menandai awal pesan
MARKER_START = b"::PESAN_RAHASIA::"
MARKER_END = b"\x00\xFF\xAA\x55"  # marker tambahan opsional

def embed_text_eof(file_bytes: bytes, text: str) -> bytes:
    """
    Sembunyikan pesan di akhir file (EOF) dengan marker unik.
    """
    encrypted = encrypt_blowfish(text).encode("utf-8")  # encrypt pesan
    result = file_bytes + MARKER_START + MARKER_END + encrypted
    return result

def extract_text_eof(file_bytes: bytes) -> str:
    """
    Ekstrak pesan dari file EOF.
    """
    marker = MARKER_START + MARKER_END
    idx = file_bytes.rfind(marker)
    if idx == -1:
        return ""  # tidak ada pesan
    encrypted = file_bytes[idx + len(marker):]
    decrypted = decrypt_blowfish(encrypted.decode("utf-8"))
    return decrypted
