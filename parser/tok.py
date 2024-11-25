import requests
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
code = os.getenv("CODE") #Возможно нужно обновлять

#https://hh.ru/oauth/authorize?response_type=code&client_id=S62DUEJDTBA2RQCB0V44O7SLN77Q6NFDHNM6D3TG8L3OL56KFRMJNAI1P3VEKL9J&redirect_uri=https://misis.ru/
# строкой выше можно получить code, он будет в url МИСИСА (code=)

oauth_end = os.getenv("OAUTH_END")

t = os.getenv("LAST_TOKEN") # Последний токен пиши сюда
response = requests.post(
    oauth_end,
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'code': code,
        'redirect_uri': os.getenv("RED_URL")
    }
)

content = response.json()
print(content)