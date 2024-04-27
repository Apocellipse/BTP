import requests
import time
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
ITER = 100

# Generate AES key and IV
AES_KEY = os.urandom(16)
AES_IV = os.urandom(16)

# fetch RSA key from key server running on localhost:5050
try:
    url = 'http://0.0.0.0:5050/get_public_key'
    username = 'prot1_serv'
    response = requests.get(url, params={'username': username})
    public_key = response.json()['public_key']
except:
    print('Error: Could not fetch RSA public key from the key server')
    exit(1)

# Encrypt AES key using RSA public key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
import base64

public_key = serialization.load_pem_public_key(public_key.encode(), backend=default_backend())
encrypted_aes_key = public_key.encrypt(AES_KEY, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))\

def AES_encrypt(data, aes_key, aes_iv):
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(aes_iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data.encode()) + encryptor.finalize()
    return ct

# note start time
start = time.time()

for i in range(ITER):
    # Read input Y from a local file
    with open('input.txt', 'r') as file:
        Y = file.read()
        Y = Y.split(',')
        Y = [int(i) for i in Y]
        Y = "".join(str(i) for i in Y)
        # print("Y : ", Y)
        enc_data = AES_encrypt(Y, AES_KEY, AES_IV)

    # Make POST request to send key and Y to the server
    url = 'http://127.0.0.1:5000'
    data = {'key': base64.b64encode(encrypted_aes_key).decode(), 'Y': base64.b64encode(enc_data).decode(), 'iv': base64.b64encode(AES_IV).decode()}
    # print(data)

    response = requests.post(url + '/inputs', json=data)

    # Check if the POST request was successful
    if response.status_code == 200:
        # Make GET request to get the result from the server
        result = requests.get(url + '/compute').json()

        # Print the result to the terminal
        # print(result)
    else:
        pass
        # print('Error:', response.text)

# note end time
end = time.time()
print('Time taken:', end - start)
