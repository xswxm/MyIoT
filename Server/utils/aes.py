#!/usr/bin/python
# -*- coding: UTF-8 -*-

import string
from Crypto.Cipher import AES
from itsdangerous import base64_encode,base64_decode
import logging

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

# AES Encryption Part
# key = os.urandom(16) # the length can be (16, 24, 32)
key = b'1234567890123456'
cipher = AES.new(key)

def encrypt(text):
    encryptText = base64_encode(cipher.encrypt(pad(str(text))))
    logging.debug(encryptText)
    return encryptText
def decrypt(ciphertext):
    decryptText = cipher.decrypt(base64_decode(ciphertext))
    decryptText = decryptText.replace(":true", ":True").replace(":false", ":False")
    decryptText = filter(lambda x: x in set(string.printable), decryptText)
    logging.debug(decryptText)
    return decryptText
