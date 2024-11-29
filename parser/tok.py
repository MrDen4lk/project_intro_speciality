import requests
import os
from dotenv import load_dotenv

# получение данных из dotenv
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
code = os.getenv("CODE") #Возможно нужно обновлять

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