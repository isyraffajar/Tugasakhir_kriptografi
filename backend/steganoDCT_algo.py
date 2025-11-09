
import io
from typing import Tuple
from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct

# ------- Utility: text <-> bits -------
def text_to_bits(s: str) -> str:
    return ''.join(f"{b:08b}" for b in s.encode('utf-8'))

def bits_to_text(bstr: str) -> str:
    bytes_list = [int(bstr[i:i+8], 2) for i in range(0, len(bstr), 8)]
    return bytes(bytes_list).decode('utf-8', errors='replace')

# ------- DCT helpers -------
def dct2(block: np.ndarray) -> np.ndarray:
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block: np.ndarray) -> np.ndarray:
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

# ------- Parameters -------
BLOCK_SIZE = 8
MID_FREQ_POS = (4, 3)  # Koefisien mid-frequency untuk embed
HEADER_BITS = 32        # 32-bit untuk panjang pesan (bytes)

# ------- Y Channel convert -------
def _image_to_y_channel(img: Image.Image) -> Tuple[np.ndarray, tuple]:
    if img.mode != 'RGB':
        img = img.convert('RGB')
    ycbcr = img.convert('YCbCr')
    y, cb, cr = ycbcr.split()
    return np.array(y, dtype=np.float32), img.size

def _y_channel_to_image(y_channel: np.ndarray, original_img: Image.Image) -> Image.Image:
    y_clipped = np.clip(np.rint(y_channel), 0, 255).astype(np.uint8)
    y_img = Image.fromarray(y_clipped, mode='L')
    cb, cr = original_img.convert('YCbCr').split()[1:]
    return Image.merge('YCbCr', (y_img, cb, cr)).convert('RGB')

# ------- EMBEDDING -------
def _embed_bits_in_y(y: np.ndarray, bits: str) -> np.ndarray:
    h, w = y.shape
    pad_h = (-h) % BLOCK_SIZE
    pad_w = (-w) % BLOCK_SIZE
    if pad_h or pad_w:
        y = np.pad(y, ((0, pad_h), (0, pad_w)), mode='edge')
        h, w = y.shape

    max_blocks = (h // BLOCK_SIZE) * (w // BLOCK_SIZE)
    if len(bits) > max_blocks:
        raise ValueError(f"Message terlalu panjang! Maks: {max_blocks} bit")

    out = y.copy()
    bit_idx = 0
    for by in range(0, h, BLOCK_SIZE):
        for bx in range(0, w, BLOCK_SIZE):
            if bit_idx >= len(bits):
                break
            block = out[by:by+BLOCK_SIZE, bx:bx+BLOCK_SIZE]
            d = dct2(block)
            r, c = MID_FREQ_POS
            coef = d[r, c]
            bit = bits[bit_idx]
            mag = int(abs(round(coef)))
            if (mag % 2) != int(bit):
                if coef >= 0:
                    coef += 1
                else:
                    coef -= 1
            d[r, c] = coef
            out[by:by+BLOCK_SIZE, bx:bx+BLOCK_SIZE] = idct2(d)
            bit_idx += 1
    return out[:y.shape[0]-pad_h if pad_h else h, :y.shape[1]-pad_w if pad_w else w]

# ------- EXTRACTION -------
def _extract_bits_from_y(y: np.ndarray, num_bits: int, start_bit: int = 0) -> str:
    h, w = y.shape
    pad_h = (-h) % BLOCK_SIZE
    pad_w = (-w) % BLOCK_SIZE
    if pad_h or pad_w:
        y = np.pad(y, ((0, pad_h), (0, pad_w)), mode='edge')
        h, w = y.shape

    bits = []
    bit_count = 0
    target_end = start_bit + num_bits
    global_idx = 0
    for by in range(0, h, BLOCK_SIZE):
        for bx in range(0, w, BLOCK_SIZE):
            if global_idx >= target_end:
                break
            block = y[by:by+BLOCK_SIZE, bx:bx+BLOCK_SIZE]
            d = dct2(block)
            r, c = MID_FREQ_POS
            coef = d[r, c]
            mag = int(abs(round(coef)))
            if global_idx >= start_bit:
                bits.append(str(mag % 2))
            global_idx += 1
        if global_idx >= target_end:
            break

    if len(bits) < num_bits:
        raise ValueError("Blok gambar tidak cukup untuk mengekstrak pesan")
    return ''.join(bits)

# ------- PUBLIC API -------
def embed_text_into_image(pil_img: Image.Image, message: str) -> Image.Image:
    y, _ = _image_to_y_channel(pil_img)

    msg_bytes = message.encode('utf-8')
    msg_len = len(msg_bytes)

    header = f"{msg_len:032b}"
    payload = text_to_bits(message)

    # Debug
    print("=== DEBUG EMBED ===")
    print("Header bits:", header)
    print("Payload length (bits):", len(payload))
    print("First 64 bits of payload:", payload[:64])  # cek sebagian saja

    full_bits = header + payload
    y_mod = _embed_bits_in_y(y, full_bits)
    return _y_channel_to_image(y_mod, pil_img)

    

def extract_text_from_image(pil_img: Image.Image) -> str:
    y, _ = _image_to_y_channel(pil_img)

    header_bits = _extract_bits_from_y(y, HEADER_BITS)
    msg_len = int(header_bits, 2)
    payload_bits_len = msg_len * 8
    payload_bits = _extract_bits_from_y(y, payload_bits_len, start_bit=HEADER_BITS)

    # Debug
    print("=== DEBUG EXTRACT ===")
    print("Header bits:", header_bits)
    print("Message length (bytes):", msg_len)
    print("Payload length (bits):", len(payload_bits))
    print("First 64 bits of payload:", payload_bits[:64])

    return bits_to_text(payload_bits)


# ------- Output helpers -------
def pil_image_to_jpeg_bytes(image: Image.Image, quality: int = 100) -> bytes:
    buf = io.BytesIO()
    # subsampling=0 untuk hindari downsampling warna
    image.save(buf, format='JPEG', quality=quality, subsampling=0)
    return buf.getvalue()
