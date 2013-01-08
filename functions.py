from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2
import random


def encipher(note, password):
	iv = SHA256.new(str(random.randint(0, 2**20))).hexdigest()[0:16]
        key = PBKDF2(password, iv).read(32)
        dnote_to_encrypt = AES.new(key, AES.MODE_CFB, iv)
        dnote = dnote_to_encrypt.encrypt(note)
