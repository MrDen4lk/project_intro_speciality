import requests

client_id = 'S62DUEJDTBA2RQCB0V44O7SLN77Q6NFDHNM6D3TG8L3OL56KFRMJNAI1P3VEKL9J'
client_secret = 'OVF6LPUPK19QBP273LIP8TB696HN44KJNC48JA4B8DBDQN33NCQ4V0DBTP8MMC4N'
code = 'VK9B5J37EJ24R0I9N79O0MHPS4BHGL824O02EK2NC9O6G52HIAFEL07NV7PCUO28' #Возможно нужно обновлять

#https://hh.ru/oauth/authorize?response_type=code&client_id=S62DUEJDTBA2RQCB0V44O7SLN77Q6NFDHNM6D3TG8L3OL56KFRMJNAI1P3VEKL9J&redirect_uri=https://misis.ru/
# строкой выше можно получить code, он будет в url МИСИСА (code=)

oauth_end = "https://hh.ru/oauth/token"

t = 'APPLVU2H540D1C9NE0FB8R3TMPDSLDA0TB8NKV8G9SNM4MKNECJIMD5UHIK87OGL' # Последний токен пиши сюда
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