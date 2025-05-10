from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import os

BLOCK_SIZE = 16  # AES block size
SALT_SIZE = 16
KEY_SIZE = 32  # AES-256


def pad(data):
    pad_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([pad_len] * pad_len)


def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]


def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=KEY_SIZE)


def encrypt_file(file_path, password):
    salt = get_random_bytes(SALT_SIZE)
    key = derive_key(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_CBC)

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    padded = pad(plaintext)
    ciphertext = cipher.encrypt(padded)

    enc_path = file_path + ".enc"
    with open(enc_path, 'wb') as f:
        f.write(salt + cipher.iv + ciphertext)

    return enc_path


def decrypt_file(enc_path, output_path, password):
    with open(enc_path, 'rb') as f:
        salt = f.read(SALT_SIZE)
        iv = f.read(BLOCK_SIZE)
        ciphertext = f.read()

    key = derive_key(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext))

    with open(output_path, 'wb') as f:
        f.write(decrypted)

    return output_path
