# =-- Dependencies --= #
from Crypto.Random import get_random_bytes
from Crypto.Util import Padding
from Crypto.Cipher import AES
import hashlib
import base64

# =-- KEY --= #
KEY_BYTES = b'\xa4js\x1f\x87\x96\x11\xf8\xe7\xdfA\x08G\x8d\x03<'
KEY_BASE64 = b'pGpzH4eWEfjn30EIR40DPA=='

# =-- AES Encrypt/Decrypt --= #
def encrypt(plaintext: str, key_b64: bytes):
    """
    Encrypts the given plaintext using AES-CBC 128.
    :param plaintext:
    :param key_b64: A 16 byte AES key encoded in Base64.
    :return: iv_b64, ciphertext_b64
    """
    key = base64.b64decode(key_b64)

    if len(key) != 16:
        raise ValueError("Key must be 16 bytes long")

    # Initialize cipher
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv

    # Pad with PCKS#7
    padded = Padding.pad(plaintext.encode(), 16, style="pkcs7")

    # Encrypt and encode plaintext + iv
    b64_ciphertext = base64.b64encode(cipher.encrypt(padded))
    iv_encrypted = base64.b64encode(iv)

    return iv_encrypted, b64_ciphertext

def decrypt(ciphertext_b64: str, iv_b64: str, key_b64: bytes):
    """
    Decrypts the given ciphertext using AES-CBC 128.
    :param ciphertext_b64:
    :param iv_b64: The initialization vector in base64 format.
    :param key_b64: A 16 byte AES key encoded in Base64.
    :return: Unencrypted plaintext
    """
    key = base64.b64decode(key_b64)

    if len(key) != 16:
        raise ValueError("Key must be 16 bytes long")

    # Process ciphertext
    ciphertext = base64.b64decode(ciphertext_b64)
    iv = base64.b64decode(iv_b64)

    # Initialize cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Unpack
    decrypted_padded = cipher.decrypt(ciphertext)
    plaintext_unpadded = Padding.unpad(decrypted_padded, 16, style="pkcs7")

    return plaintext_unpadded.decode()

def hash_sha512(text: str):
    """
    Hashes the given text using SHA-512,
    splitting into an authentication key (32 bytes) and an encryption key (16 bytes).
    :param text: The unhashed text
    :return: (16 byte encryption key, 32 byte authentication key)
    """
    full_hash = hashlib.sha512(text.encode()).digest()

    k_auth = base64.b64encode(full_hash[:32]).decode()
    k_enc = base64.b64encode(full_hash[32:48]).decode() # Only 16 bytes for AES 128 support

    return k_enc, k_auth

def verify_password(plaintext_password: str, k_auth: str) -> bool:
    """
    Verifies a given plaintext password against an authentication key.
    :param plaintext_password: The plaintext password to verify.
    :param k_auth: The authentication key to verify.
    :return: True/False
    """
    _, given_auth = hash_sha512(plaintext_password)

    return given_auth == k_auth