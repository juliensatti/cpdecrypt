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
legacy = 0  # Indice du tableau 'counter'
v10 = 1  # Indice du tableau 'counter'


# Copie le fichier contenant les mots de passes (pour permissions)
def init_db(browser):
    if browser == "3":
        path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Microsoft\Edge\User Data\Default\Login Data")
        db_path = os.path.abspath(getenv("APPDATA") + r"\..\..\LoginFile")
    elif browser == "2":
        path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Chromium\User Data\Default\Login Data")
        db_path = os.path.abspath(getenv("APPDATA") + r"\..\..\LoginFile")
    else:
        path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Login Data")
        db_path = os.path.abspath(getenv("APPDATA") + r"\..\..\LoginFile")
    copyfile(path, db_path)
    return db_path


# Récupère la clé utilisée pa os_crypt
def get_os_crypt_key(browser):
    if browser == "3":
        pref_service_path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Microsoft\Edge\User Data\Local State")
    elif browser == "2":
        pref_service_path = os.path.abspath(getenv("APPDATA") + r"\..\Local\Chromium\User Data\Local State")
    else:
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


# Teste si la string est chiffrée avec la méthode legacy
def legacy_string(string):
    return not string.startswith(v10_prefix)


# Déchiffre la string/le mot de passe avec la methode legacy (DPAPI sans entropie secondaire)
def get_decrypted_data_legacy(legacy_encrypted_password):
    return win32crypt.CryptUnprotectData(legacy_encrypted_password, None, None, None, 0)[1]


# Obtient la nonce à partir de la string chiffrée
def get_nonce(ciphertext):
    # 'v10' is 3 bytes, we remove that
    return ciphertext[len(v10_prefix):nonce_size + len(v10_prefix)]


# Déchiffre la string/le mot de passe avec la methode v10 (AES256-GCM avec nonce)
def get_decrypted_data(string, browser):
    # Récupère la nonce de 12 bytes en l'isolant
    nonce = get_nonce(string)

    # Isole le cipher en retirant le préfixe
    raw_cipher = string[len(v10_prefix) + nonce_size:]

    # Construit AEAD avec la clé récupérée dans le PrefService
    cryptor = AESGCM(get_os_crypt_key(browser))

    return cryptor.decrypt(nonce, raw_cipher, b"")


# Sélectionne la méthode adéquate pour déchiffrer la string
def multi_decrypt(encrypted_data, browser, count):
    if legacy_string(encrypted_data):
        count[legacy] += 1
        return get_decrypted_data_legacy(encrypted_data)
    else:
        count[v10] += 1
        return get_decrypted_data(encrypted_data, browser)


# Définit les navigateurs recensés compatibles
def switch_browser(argument):
    browser_choice = {
        "1": "Google Chrome",
        "2": "Chromium (Project)",
        "3": "Microsoft Edge (>= 80)"
    }
    if not input_browser.isdigit() or int(input_browser) > 3 or int(input_browser) < 1:
        print("\nInvalid browser, exiting...")
        exit()
    else:
        return browser_choice.get(argument)


if __name__ == "__main__":

    print("==== Chromium Password Decrypter (Windows) ====")
    print("\t=== by Julien SATTI @ LIF ===")

    # Demande le navigateur sur lequel agir
    print("\nSelect your browser:")
    print("  1. Google Chrome\n  2. Chromium (Project)\n  3. Microsoft Edge (>= 80)")
    input_browser = input()
    print("\rWorking on: {}".format(switch_browser(input_browser)))

    # Initialise le compteur d'identifiants
    counter = [0, 0]

    # Lance la boucle dans la BDD pour déchiffrer et afficher les identifiants
    for url, user, encrypted_password in get_encrypted_data(init_db(input_browser)):
        if url:  # Vérifie que l'enregistrement SQL n'est pas vide
            print("\nProcessing record number " + str(counter[legacy] + counter[v10]) + ":")
            print(" * Website: {}".format(url))
            print(" * Username: {}".format(user))
            print("\r * Password: {}".format(multi_decrypt(encrypted_password, input_browser, counter).decode('utf-8')))

    print("\nA total of " + str(counter[legacy] + counter[v10]) + " credentials have been decrypted, including " + str(
        counter[legacy]) + " using the legacy DPAPI encryption...")
