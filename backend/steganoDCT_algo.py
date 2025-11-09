# backend/stegano_dct.py
import io
import math
import base64
from typing import Tuple
from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct

# ====== Utility: text <-> bits ======
def text_to_bits(s: str) -> str:
    return ''.join(f"{b:08b}" for b in s.encode('utf-8'))

def bits_to_text(bstr: str) -> str:
    # bstr length must be multiple of 8
    bytes_list = [int(bstr[i:i+8], 2) for i in range(0, len(bstr), 8)]
    return bytes(bytes_list).decode('utf-8', errors='replace')

# ====== DCT helpers (8x8 block, 2D DCT type II + inverse) ======
def dct2(block: np.ndarray) -> np.ndarray:
    # apply dct on rows then columns
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block: np.ndarray) -> np.ndarray:
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

# ====== Embedding / Extraction parameters ======
BLOCK_SIZE = 8
# mid-frequency coefficient to use (row, col) within 8x8 block.
# choose something not (0,0) and not too high frequency
MID_FREQ_POS = (4, 3)

# header size: store message byte-length in 32 bits
HEADER_BITS = 32

# ====== Core functions ======
def _image_to_y_channel(img: Image.Image) -> Tuple[np.ndarray, tuple]:
    """
    Convert PIL image to Y channel (uint8) and return size (w,h).
    Works for RGB input.
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
    ycbcr = img.convert('YCbCr')
    y, cb, cr = ycbcr.split()
    return np.array(y, dtype=np.float32), img.size

def _y_channel_to_image(y_channel: np.ndarray, original_img: Image.Image) -> Image.Image:
    """
    Recombine Y channel (numpy float) with original CbCr and return PIL RGB image.
    """
    # clip and make uint8
    y_channel_clipped = np.clip(np.rint(y_channel), 0, 255).astype(np.uint8)
    # re-create YCbCr image: reuse CbCr from original
    y_img = Image.fromarray(y_channel_clipped, mode='L')
    cb, cr = original_img.convert('YCbCr').split()[1:]
    merged = Image.merge('YCbCr', (y_img, cb, cr)).convert('RGB')
    return merged

def _embed_bits_in_y(y: np.ndarray, bits: str) -> np.ndarray:
    """
    Embed bits string into Y channel using DCT per 8x8 block, at MID_FREQ_POS.
    Returns modified Y array (float).
    """
    h, w = y.shape
    # ensure multiple of 8 - pad by repeating last row/col
    pad_h = (-h) % BLOCK_SIZE
    pad_w = (-w) % BLOCK_SIZE
    if pad_h or pad_w:
        y = np.pad(y, ((0, pad_h), (0, pad_w)), mode='edge')
        h, w = y.shape

    max_blocks = (h // BLOCK_SIZE) * (w // BLOCK_SIZE)
    if len(bits) > max_blocks:
        raise ValueError(f"Message too large: {len(bits)} bits > capacity {max_blocks} bits")

    out = y.copy()
    bit_idx = 0
    for by in range(0, h, BLOCK_SIZE):
        for bx in range(0, w, BLOCK_SIZE):
            if bit_idx >= len(bits):
                break
            block = out[by:by+BLOCK_SIZE, bx:bx+BLOCK_SIZE]
            d = dct2(block)
            r, c = MID_FREQ_POS
            # embed by adjusting the sign/LSB of coefficient magnitude
            coef = d[r, c]
            bit = bits[bit_idx]
            # Strategy: force coefficient parity of rounded absolute value to bit
            # This is simple but works for demonstration.
            mag = int(abs(round(coef)))
            if (mag % 2) != int(bit):
                # flip parity by adding/subtracting 1 while preserving sign
                if coef >= 0:
                    coef += 1.0
                else:
                    coef -= 1.0
            d[r, c] = coef
            # inverse dct
            block_rec = idct2(d)
            out[by:by+BLOCK_SIZE, bx:bx+BLOCK_SIZE] = block_rec
            bit_idx += 1
        if bit_idx >= len(bits):
            break

    return out[:y.shape[0]-pad_h if pad_h else h, :y.shape[1]-pad_w if pad_w else w]

def _extract_bits_from_y(y: np.ndarray, num_bits: int) -> str:
    """
    Extract num_bits from Y channel's DCT mid coefficients.
    """
    h, w = y.shape
    pad_h = (-h) % BLOCK_SIZE
    pad_w = (-w) % BLOCK_SIZE
    if pad_h or pad_w:
        y = np.pad(y, ((0, pad_h), (0, pad_w)), mode='edge')
        h, w = y.shape

    bits = []
    bit_idx = 0
    for by in range(0, h, BLOCK_SIZE):
        for bx in range(0, w, BLOCK_SIZE):
            if bit_idx >= num_bits:
                break
            block = y[by:by+BLOCK_SIZE, bx:bx+BLOCK_SIZE]
            d = dct2(block)
            r, c = MID_FREQ_POS
            coef = d[r, c]
            mag = int(abs(round(coef)))
            bits.append(str(mag % 2))
            bit_idx += 1
        if bit_idx >= num_bits:
            break
    return ''.join(bits)

# ====== Public API: embed / extract ======
def embed_text_into_image(pil_img: Image.Image, message: str) -> Image.Image:
    """
    Embed message text into pil_img (PIL Image). Returns a PIL Image (RGB) with stego.
    """
    y, size = _image_to_y_channel(pil_img)
    # prepare bits: 32-bit length (bytes), then payload bits
    message_bytes = message.encode('utf-8')
    msg_len = len(message_bytes)  # number of bytes
    header = f"{msg_len:032b}"
    payload = text_to_bits(message)
    full_bits = header + payload
    # embed
    y_mod = _embed_bits_in_y(y, full_bits)
    out_img = _y_channel_to_image(y_mod, pil_img)
    return out_img

def extract_text_from_image(pil_img: Image.Image) -> str:
    """
    Extract text embedded in pil_img (PIL Image). Returns string message.
    """
    y, size = _image_to_y_channel(pil_img)
    h, w = y.shape
    max_blocks = (h // BLOCK_SIZE) * (w // BLOCK_SIZE)
    # first read header 32 bits
    header_bits = _extract_bits_from_y(y, HEADER_BITS)
    msg_len = int(header_bits, 2)
    payload_bits_len = msg_len * 8
    if payload_bits_len + HEADER_BITS > max_blocks:
        raise ValueError("Invalid message length or image too small")
    payload_bits = _extract_bits_from_y(y, HEADER_BITS + payload_bits_len)[HEADER_BITS:]
    return bits_to_text(payload_bits)

# ====== Helpers to convert PIL image to bytes ======
def pil_image_to_jpeg_bytes(pil_img: Image.Image, quality=95) -> bytes:
    buf = io.BytesIO()
    pil_img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def bytes_to_base64_str(b: bytes) -> str:
    return base64.b64encode(b).decode('utf-8')
