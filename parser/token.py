import requests

client_id = 'S62DUEJDTBA2RQCB0V44O7SLN77Q6NFDHNM6D3TG8L3OL56KFRMJNAI1P3VEKL9J'
client_secret = 'OVF6LPUPK19QBP273LIP8TB696HN44KJNC48JA4B8DBDQN33NCQ4V0DBTP8MMC4N'
code = 'G62LCKGRJGI7MU1R1DALUKVPFP8RH8UD2JLNQ4ERD5236CN1M79HGTFJ1O81DKM3' #Возможно нужно обновлять

oauth_end = "https://hh.ru/oauth/token"

response = requests.post(
    oauth_end,
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'code': code,
        'redirect_uri': 'https://misis.ru/'
    }
)

content = response.json()
print(content)