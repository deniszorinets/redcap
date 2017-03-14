import binascii
from Crypto.PublicKey import RSA
from Crypto.Util.number import *
from random import choice


def pem_to_openssh(key):
    """
    convert pem key to openssh key
    :param key:
    :return:
    """
    eb = long_to_bytes(key.e)
    nb = long_to_bytes(key.n)
    if bord(eb[0]) & 0x80: eb = bchr(0x00) + eb
    if bord(nb[0]) & 0x80: nb = bchr(0x00) + nb
    keyparts = [b'ssh-rsa', eb, nb]
    keystring = b''.join([struct.pack(b">I", len(kp)) + kp for kp in keyparts])
    return b'ssh-rsa ' + binascii.b2a_base64(keystring)[:-1]


def opsenssh_keypair(passphrase):
    """
    generate openssh keypair
    :param passphrase:
    :return:
    """
    key = RSA.generate(4096)

    privateKey = key.exportKey('PEM', passphrase.__str__(), pkcs=8)
    public = key.publickey()
    publicKey = pem_to_openssh(public)
    return privateKey, publicKey


def random_key(length):
    """
    generate random secure key
    :param length:
    :return:
    """
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    letters += str.lower(letters)
    chars = "0123456789!@#$%^&*()_{}[];:.,/\\`~" + letters

    return ''.join(choice(chars) for _ in range(length))
