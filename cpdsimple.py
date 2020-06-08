#! /usr/bin/env python3

"""
__author__ = "Julien SATTI"
__copyright__ = "Copyright 2020, Julien SATTI @ LIF"
__email__ = "julien.satti1@uqac.ca"
__source__ =  https://git.duework.org/julien/cpdecrypt

La version de ce script boucle sur tous les navigateurs compatibles testés avec ce déchiffreur ;
il ne contient aucune fonction : tout est réalisé dans le main contrairement à cpd.py ; il est également
rédigé en français pour aider les étudiants québecois de l'UQAC, cibles première de ce programme.
"""

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
    "5": ["Vivaldi",
          appdata + r"\..\Local\Vivaldi\User Data\Default\Login Data",
          appdata + r"\..\Local\Vivaldi\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "6": ["Brave Browser",
          appdata + r"\..\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data",
          appdata + r"\..\Local\BraveSoftware\Brave-Browser\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "7": ["Comodo Dragon",
          appdata + r"\..\Local\Comodo\Dragon\User Data\Default\Login Data",
          appdata + r"\..\Local\Comodo\Dragon\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "8": ["Coc Coc Browser",
          appdata + r"\..\Local\CocCoc\Browser\User Data\Default\Login Data",
          appdata + r"\..\Local\CocCoc\Browser\User Data\Local State",
          "SELECT origin_url, username_value, password_value FROM logins"],
    "9": ["UC Browser",
          appdata + r"\..\Local\UCBrowser\User Data_i18n\Default\UC Login Data.17",
          appdata + r"\..\Local\UCBrowser\User Data_i18n\Local State",
          "SELECT origin_url, username_value, password_value FROM wow_logins"],
    "10": ["QQ Browser (Tencent)",
           appdata + r"\..\Local\Tencent\QQBrowser\User Data\Default\Login Data",
           appdata + r"\..\Local\Tencent\QQBrowser\User Data\Local State",
           "SELECT origin_url, username_value, password_value FROM logins"]
}  # Dictionnaire des navigateurs supportés, des fichiers clés (Login Data & Pref Service) et de la requête SQL

if __name__ == "__main__":

    print("==== Chromium Password Decrypter (Windows) ====")
    print("\t=== by Julien SATTI @ LIF ===")

    # Boucle sur tous les navigateurs
    for x in browser_choice:
        print("\nPour le navigateur {} :".format(browser_choice[x][0]))

        # Vérifie si le navigateur est présent
        try:
            copyfile(browser_choice[x][1], db_path)  # Copie le fichier contenant les mots de passes (pour simultanéité)
        except FileNotFoundError:
            print("Navigateur non installé, suivant...")
            continue  # Saute le navigateur

        # Créée la connexion à la BDD
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        data = cursor.execute(browser_choice[x][3])

        # Lance la boucle dans la BDD pour déchiffrer et afficher les identifiants
        for url, user, encrypted_password in data:
            print("\n * Site : {}".format(url))
            print(" * Utilisateur : {}".format(user))

            # On traite le mot de passe chiffré
            if not encrypted_password.startswith(v10_prefix):
                # Appel à DPAPI si commence par 'v10' (avant version 80)
                decrypted_password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
            else:
                # Nouvelle méthode AESGCM-256
                # Récupère et déchiffre la clé
                with open(browser_choice[x][2]) as f:
                    d = json.load(f)
                encrypted_key = base64.decodebytes(bytes(d['os_crypt']['encrypted_key'], 'utf-8'))[len(DPAPI_prefix):]
                key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

                # Récupère la nonce de 12 bytes en l'isolant
                nonce = encrypted_password[len(v10_prefix):nonce_size + len(v10_prefix)]

                # Isole le cipher en retirant le préfixe
                raw_cipher = encrypted_password[len(v10_prefix) + nonce_size:]

                # Construit AEAD avec la clé récupérée dans le PrefService déchiffrée préalablement
                cryptor = AESGCM(key)

                # Déchiffre le mot de passe
                decrypted_password = cryptor.decrypt(nonce, raw_cipher, b"")

                print(" * Mot de passe: {}".format(decrypted_password.decode('utf-8')))
