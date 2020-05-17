# Password Decrypter for Chromium-based browsers
![](https://git.duework.org/julien/cpdecrypt/-/wikis/uploads/5747a35a1b5a3f1cf97b8a8bc1702da1/header.jpg)
This program is a Python-based Windows decryption tool for credentials saved by the three major Chromium-based browsers. It works with the **new** Microsoft Edge as well as the most recent versions (post version-80) of Google Chrome and Chromium which use a new encryption mechanism.

| Browser | Version |
| ------ | ------ |
| [Google Chrome](https://www.google.com/chrome/) | All, even >= 80 |
| [Chromium Project](https://chromium.woolyss.com/download/en/) | All, even >= 80 |
| [Microsoft Edge](https://www.microsoft.com/en-us/edge) | >= 80 |

## ⚡️ Automatic installation

1. Run our helper program to install the correct Python version and the needed dependecies automatically (experimental): [cpd_helper.exe](uploads/68ee1b7fc512146667e5aeb92da7324f/cpd_helper.exe)

2. Clone this repository
````bash
git clone https://git.duework.org/julien/cpdecrypt.git
cd cpdecrypt
````

3. Run
````bash
python cpd.py
````

## 🤓 Manual installation

1. Intall Python by visiting the official [source](https://www.python.org/downloads/windows/]) and selecting the appropriate and desired release (we use python3.8).

2. Install dependencies. Our code requires the latest pywin32 and aead.
````bash
pip install pywin32
pip install aead
````

> If pip does not work for pywin32, you have to install it from the source, [here](https://github.com/mhammond/pywin32/releases/tag/b227) (we use build 277).

3. Clone this repository
````bash
git clone https://git.duework.org/julien/cpdecrypt.git
cd cpdecrypt
````

4. Run
````bash
python cpd.py
````

## Author

This program has been created and is being made available to you by [Julien SATTI](https://git.duework.org/julien).

## Context

The project was mandated by Raphaël Khoury — for an internship at *Laboratoire d'Informatique Formelle* (LIF) — who provided a first rough version of this decrypter for Chrome/Chromium prior to version 80.
