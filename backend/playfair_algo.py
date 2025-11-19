import string
import re

# ASCII printable 32–126 (95 chars)
ASCII_CHARS = ''.join(chr(i) for i in range(32, 127)) + "\n"

GRID_SIZE = 10  # 10x10 matrix (100 slots)


def generate_playfair_matrix(key: str):
    """Generate Playfair matrix 10x10 dengan karakter unik."""
    seen = set()
    matrix_list = []

    # Masukkan karakter key dulu
    for ch in key:
        if ch in ASCII_CHARS and ch not in seen:
            seen.add(ch)
            matrix_list.append(ch)

    # Tambahkan ASCII yang belum ada
    for ch in ASCII_CHARS:
        if ch not in seen:
            seen.add(ch)
            matrix_list.append(ch)

    # Tambah padding karakter unik seperti '\x00'
    padding_char = '\x00'
    while len(matrix_list) % GRID_SIZE != 0:
        if padding_char not in seen:
            matrix_list.append(padding_char)
            seen.add(padding_char)
        else:
            padding_char = chr(ord(padding_char) + 1)

    # Bentuk matrix 10x10
    matrix = [matrix_list[i:i + GRID_SIZE] for i in range(0, len(matrix_list), GRID_SIZE)]

    # Buat lookup posisi huruf --> O(1) lookup
    pos = {matrix[i][j]: (i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)}

    return matrix, pos


def prepare_text(text: str, filler='\x00'):
    """Siapkan teks agar valid untuk Playfair:
       - pasangan huruf sama → sisipkan filler
       - jika ganjil → tambah filler
    """

    cleaned = ""
    i = 0

    while i < len(text):
        a = text[i]
        b = text[i + 1] if i + 1 < len(text) else None

        if b is None:
            cleaned += a + filler
            break

        if a == b:
            cleaned += a + filler
            i += 1
        else:
            cleaned += a + b
            i += 2

    return cleaned


def playfair_encrypt(text: str, key: str):
    matrix, pos = generate_playfair_matrix(key)
    text = prepare_text(text)

    result = ""

    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        row_a, col_a = pos[a]
        row_b, col_b = pos[b]

        if row_a == row_b:  # sama baris → geser kanan
            result += matrix[row_a][(col_a + 1) % GRID_SIZE]
            result += matrix[row_b][(col_b + 1) % GRID_SIZE]

        elif col_a == col_b:  # sama kolom → geser bawah
            result += matrix[(row_a + 1) % GRID_SIZE][col_a]
            result += matrix[(row_b + 1) % GRID_SIZE][col_b]

        else:  # rectangle rule
            result += matrix[row_a][col_b]
            result += matrix[row_b][col_a]

    return result


def playfair_decrypt(ciphertext: str, key: str):
    matrix, pos = generate_playfair_matrix(key)
    result = ""

    for i in range(0, len(ciphertext), 2):
        a, b = ciphertext[i], ciphertext[i+1]
        row_a, col_a = pos[a]
        row_b, col_b = pos[b]

        if row_a == row_b:  # sama baris → geser kiri
            result += matrix[row_a][(col_a - 1) % GRID_SIZE]
            result += matrix[row_b][(col_b - 1) % GRID_SIZE]

        elif col_a == col_b:  # sama kolom → geser atas
            result += matrix[(row_a - 1) % GRID_SIZE][col_a]
            result += matrix[(row_b - 1) % GRID_SIZE][col_b]

        else:  # rectangle rule
            result += matrix[row_a][col_b]
            result += matrix[row_b][col_a]
    
    result = result.replace('\x00', '')
    return result

def sanitize_text_for_playfair(text: str) -> str:
    """
    Membersihkan teks dari karakter yang tidak dikenali Playfair.
    Mengubah tanda kutip miring → kutip biasa.
    Mengubah strip panjang → strip biasa.
    Menghapus simbol aneh.
    """
    replacements = {
        "“": '"',  "”": '"',
        "‘": "'",  "’": "'",
        "—": "-",  "–": "-",
        "…": "...",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Buang karakter NON ASCII (Playfair tidak mendukung unicode kompleks)
    text = re.sub(r"[^A-Za-z0-9 .,!?;:'\"()\-\/\n]", "", text)

    return text

