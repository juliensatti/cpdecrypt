# Password Decrypter for Chromium-based browsers

![](https://git.duework.org/julien/cpdecrypt/-/wikis/uploads/5747a35a1b5a3f1cf97b8a8bc1702da1/header.jpg)

This program is a Python-based Windows decryption tool for credentials saved by the following Chromium-based browsers:

| Browser | Version |
| ------ | ------ |
| [Google Chrome](https://www.google.com/chrome/) | All, even >= 80 |
| [Chromium Project](https://chromium.woolyss.com/download/en/) | All, even >= 80 |
| [Microsoft Edge](https://www.microsoft.com/en-us/edge) | >= 80 |


It works with the new Microsoft Edge as well as the most recent versions (post version-80) of Google Chrome and Chromium which use a new encryption mechanism.

## Installation

1. Clone this repository
````bash
# retrieve the script
git clone https://git.duework.org/julien/cpdecrypt.git
cd cpdecrypt
````

2. Intall Python by visiting the official [source](https://www.python.org/downloads/windows/]) and selecting the appropriate and desired release (we use python3.8).

3. Install dependencies. Our code requires the latest pywin32 and aead.
````bash
# install requirements
pip install pywin32
pip install aead
````
4. Run
````bash
python cpd.py
````

## Author

This program has been created is being made available to you by Julien SATTI.

## Context

The project was mandated by Raphaël Khoury — for an internship at *Laboratoire d'Informatique Formelle* (LIF) — who provided a first rough version of this decrypter for Chrome/Chromium prior to version 80.
