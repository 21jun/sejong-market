import requests, json, base64
import urllib
from pathlib import Path

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

from monthly import app


def get_client_key():
    CLIENT_ID = app.config['CLIENT_ID']
    CLIENT_SECRET = app.config['CLIENT_SECRET']
    return CLIENT_ID, CLIENT_SECRET

def get_public_key():
    PUBKEY = app.config['PUBKEY']
    return PUBKEY

def http_sender(url, token, body):
    headers = {'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

    response = requests.post(url, headers = headers, data = urllib.parse.quote(str(json.dumps(body))))

    # print('response.status_code = ' + str(response.status_code))
    # print('response.text = ' + urllib.parse.unquote_plus(response.text))

    return response

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def publicEncRSA(publicKey, data):
    keyDER = base64.b64decode(publicKey)
    keyPub = RSA.importKey(keyDER)
    cipher = Cipher_PKCS1_v1_5.new(keyPub)
    cipher_text = cipher.encrypt(data.encode())

    encryptedData = base64.b64encode(cipher_text).decode("utf-8")
    # print('encryptedData = ' + encryptedData)

    return encryptedData