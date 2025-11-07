import string

# Full ASCII 32-126
ASCII_CHARS = ''.join([chr(i) for i in range(32, 127)])

def generate_playfair_matrix(key: str):
    """
    Generate Playfair matrix 10x10 (atau sesuai kebutuhan) dari key.
    Untuk full ASCII, kita buat 10x10 grid cukup untuk 95 karakter.
    """
    seen = set()
    matrix = []

    # Masukkan karakter dari key dulu
    for char in key:
        if char not in seen and char in ASCII_CHARS:
            seen.add(char)
            matrix.append(char)

    # Masukkan karakter ASCII yang belum ada
    for char in ASCII_CHARS:
        if char not in seen:
            seen.add(char)
            matrix.append(char)

    # Bentuk matrix 10x10
    grid_size = 10
    # Pastikan semua row panjang sama (padding jika perlu)
    while len(matrix) % grid_size != 0:
        matrix.append(' ')  # padding karakter agar row penuh
    matrix_grid = [matrix[i:i+grid_size] for i in range(0, len(matrix), grid_size)]
    return matrix_grid

def find_position(matrix, char):
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char:
                return i, j
    return None, None

def sanitize_text(text):
    return ''.join(c if c in ASCII_CHARS else ' ' for c in text)

def playfair_encrypt(text, key):
    matrix = generate_playfair_matrix(key)
    result = ""

    # Tambahkan padding jika panjang ganjil
    if len(text) % 2 != 0:
        text += " "  # bisa pakai karakter padding lain

    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        row_a, col_a = find_position(matrix, a)
        row_b, col_b = find_position(matrix, b)

        if row_a == row_b:
            # Sama baris: geser kanan
            result += matrix[row_a][(col_a + 1) % 10]
            result += matrix[row_b][(col_b + 1) % 10]
        elif col_a == col_b:
            # Sama kolom: geser bawah
            result += matrix[(row_a + 1) % 10][col_a]
            result += matrix[(row_b + 1) % 10][col_b]
        else:
            # Kotak persegi: tukar kolom
            result += matrix[row_a][col_b]
            result += matrix[row_b][col_a]

    return result

def playfair_decrypt(ciphertext, key):
    matrix = generate_playfair_matrix(key)
    result = ""

    for i in range(0, len(ciphertext), 2):
        a, b = ciphertext[i], ciphertext[i+1]
        row_a, col_a = find_position(matrix, a)
        row_b, col_b = find_position(matrix, b)

        if row_a == row_b:
            # Sama baris: geser kiri
            result += matrix[row_a][(col_a - 1) % 10]
            result += matrix[row_b][(col_b - 1) % 10]
        elif col_a == col_b:
            # Sama kolom: geser atas
            result += matrix[(row_a - 1) % 10][col_a]
            result += matrix[(row_b - 1) % 10][col_b]
        else:
            # Kotak persegi: tukar kolom
            result += matrix[row_a][col_b]
            result += matrix[row_b][col_a]

    return result