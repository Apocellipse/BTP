# Server :: port 5000
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import csv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import requests
import base64

# generate set of RSA (public, private) key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# serialize the public key
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# convert the public key to string
public_key_str = pem.decode('utf-8')

# enlist the public key to 127.0.0.1:5050/upload_public_key
try:
    url = 'http://key_server:5050/upload_public_key'
    data = {'username': 'prot1_serv', 'public_key': public_key_str}
    response = requests.post(url, json=data)
    print(response.json())
except Exception as e:
    print('Error: Could not upload RSA public key to the key server => ', e)
    exit(1)

# define FastAPI app
app = FastAPI()

AESkey = None
Y = None
DATASET = {}
t = 5

# Define request body model
class Inputs(BaseModel):
    key: str
    Y: str
    iv: str

# Fetch data from CSV file
with open('/prot1_serv/biobits.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        li = str(row[0])
        Xi = np.array(row[1:], dtype=int)
        DATASET[li] = Xi
# print("Keanu: ", DATASET["Keanu Reeves0"])

def AES_decrypt(data, aes_key, aes_iv):
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(aes_iv))
    decryptor = cipher.decryptor()
    pt = decryptor.update(data) + decryptor.finalize()
    return pt

def RSA_decrypt(data, private_key):
    pt = private_key.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return pt
# Route to receive inputs
@app.post('/inputs')
async def get_inputs(inputs: Inputs):
    global AESkey, Y, private_key
    AESkey = inputs.key
    AESkey = RSA_decrypt(base64.b64decode(AESkey.encode()), private_key)
    enc_Y = inputs.Y
    AESIV = inputs.iv
    Y = AES_decrypt(base64.b64decode(enc_Y), AESkey, base64.b64decode(AESIV))
    Y = Y.decode()
    nY = []
    for i in range(len(Y)):
        nY.append(int(Y[i]))

    Y = nY
    # print("Y:", Y)
    return {'message': 'success'}

# Route to compute function
@app.get('/compute')
async def compute_function():
    global AESkey, Y, DATASET, t

    if AESkey is None or Y is None:
        raise HTTPException(status_code=400, detail='Key or Y is not provided')

    for li, Xi in DATASET.items():
        Xi = Xi.tolist()
        if np.sum(np.bitwise_xor(Xi, Y)) <= t:
            return {'text': 'success', 'result': li}

    return {'text': 'nomatch'}

# if __name__ == '__main__':
#    pre_fetch_data()