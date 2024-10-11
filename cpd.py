#! /usr/bin/env python3

"""
__author__ = "Julien Satti"
__copyright__ = "Copyright 2020, Julien Satti @ LIF"
__email__ = "julien.satti1@uqac.ca"
__source__ =  https://github.com/juliensatti/cpdecrypt

CPDecrypt displays on screen the user-saved credentials from compatible Chromium-based web browsers on Windows
by decrypting legacy passwords thanks to the DPAPI and new ones (post version-80 of Chromium) using the aead library
for their AESGCM-256 encryption/decryption method.
"""

import sqlite3
import os
from os import getenv
from shutil import copyfile
import json
import cryptography
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

DPAPI_prefix = b'DPAPI'
v10_prefix = b'v10'
nonce_size = 12  # 96/8
key_length = 32  # 256/8
legacy = 0  # Indice du tableau 'counter'
v10 = 1  # Indice du tableau 'counter'
appdata = os.path.abspath(getenv("APPDATA"))
db_path = os.path.abspath(getenv("APPDATA") + r"\..\..\LoginFileCPD")  # Emplacement temporaire pour Login File
browser_choice = {
    "1": ["Google Chrome",
          appdata + r"\..\Local\Google\Chrome\User Data\Default\Login Data",
          appdata + r"\..\Local\Google\Chrome\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "2": ["Chromium Project",
          appdata + r"\..\Local\Chromium\User Data\Default\Login Data",
          appdata + r"\..\Local\Chromium\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "3": ["Microsoft Edge (>= 80)",
          appdata + r"\..\Local\Microsoft\Edge\User Data\Default\Login Data",
          appdata + r"\..\Local\Microsoft\Edge\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "4": ["Opera Browser (>= 15)",
          appdata + r"\Opera Software\Opera Stable\Login Data",
          appdata + r"\Opera Software\Opera Stable\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "5": ["Yandex Browser (no Master Password)",
          appdata + r"\..\Local\Yandex\YandexBrowser\User Data\Default\Ya Passman Data",
          appdata + r"\..\Local\Yandex\YandexBrowser\User Data\Local State",
          "SELECT action_url, username_value, password_value FROM logins"],
    "6": ["Vivaldi",
          appdata + r"\..\Local\Vivaldi\User Data\Default\Login Data",
          appdata + r"\..\Local\Vivaldi\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "7": ["Brave Browser",
          appdata + r"\..\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data",
          appdata + r"\..\Local\BraveSoftware\Brave-Browser\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "8": ["Comodo Dragon",
          appdata + r"\..\Local\Comodo\Dragon\User Data\Default\Login Data",
          appdata + r"\..\Local\Comodo\Dragon\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "9": ["Coc Coc Browser",
          appdata + r"\..\Local\CocCoc\Browser\User Data\Default\Login Data",
          appdata + r"\..\Local\CocCoc\Browser\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "10": ["UC Browser",
           appdata + r"\..\Local\UCBrowser\User Data_i18n\Default\UC Login Data.17",
           appdata + r"\..\Local\UCBrowser\User Data_i18n\Local State",
           "SELECT origin_url, username_value, password_value FROM wow_logins"],
    "11": ["QQ Browser (Tencent)",
           appdata + r"\..\Local\Tencent\QQBrowser\User Data\Default\Login Data",
           appdata + r"\..\Local\Tencent\QQBrowser\User Data\Local State",
           "SELECT origin_url, username_value, password_value FROM logins"]
}  # Dictionnaire des navigateurs supportés, des fichiers clés (Login Data & Pref Service) et de la requête SQL


# Copie le fichier contenant les mots de passes (pour simultanéité)
def init_db(browser):
    copyfile(browser_choice[browser][1], db_path)
    return db_path


# Supprime le fichier temporaire créé par le programme
def end():
    os.remove(db_path)


# Récupère la clé utilisée pa os_crypt
def get_os_crypt_key(browser):
    with open(browser_choice[browser][2]) as f:
        d = json.load(f)
    encrypted_key = base64.decodebytes(bytes(d['os_crypt']['encrypted_key'], 'utf-8'))[len(DPAPI_prefix):]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]


# Renvoie depuis la base de données les valeurs chiffrées
def get_encrypted_data(browser):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    data = cursor.execute(browser_choice[browser][3])
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

    try:
        return cryptor.decrypt(nonce, raw_cipher, b"")
    except cryptography.exceptions.InvalidTag:
        return b"(erreur)"


# Sélectionne la méthode adéquate pour déchiffrer la string
def multi_decrypt(encrypted_data, browser, count):
    if legacy_string(encrypted_data) and browser != "5":  # Yandex n'ajoute aucun préfixe
        count[legacy] += 1
        return get_decrypted_data_legacy(encrypted_data)
    else:
        count[v10] += 1
        return get_decrypted_data(encrypted_data, browser)


# Définit les navigateurs recensés compatibles
def switch_browser(argument):
    if not input_browser.isdigit() or int(input_browser) > 11 or int(input_browser) < 1:
        print("\nInvalid browser, exiting...")
        exit()
    else:
        return browser_choice.get(argument)[0]


if __name__ == "__main__":

    print("==== Chromium Password Decrypter (Windows) ====")
    print("\t=== by Julien SATTI @ LIF ===")

    # Demande le navigateur sur lequel agir
    print("\nSelect your browser:")
    for x in browser_choice:
        print("   "+x+". " + browser_choice[x][0])
    input_browser = input()
    print("\rWorking on: {}".format(switch_browser(input_browser)))

    # Initialise le compteur d'identifiants
    counter = [0, 0]

    # Initialise la BDD
    init_db(input_browser)

    # Lance la boucle dans la BDD pour déchiffrer et afficher les identifiants
    for url, user, encrypted_password in get_encrypted_data(input_browser):
        if url:  # Vérifie que l'enregistrement SQL n'est pas vide
            print("\nProcessing record number " + str(counter[legacy] + counter[v10]) + ":")
            print(" * Website: {}".format(url))
            print(" * Username: {}".format(user))
            print(" * Password: {}".format(multi_decrypt(encrypted_password, input_browser, counter).decode('utf-8')))

    print("\nA total of " + str(counter[legacy] + counter[v10]) + " credentials have been decrypted, including " + str(
        counter[legacy]) + " using the legacy DPAPI encryption...")

    end()
