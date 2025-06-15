import requests

url = "http://127.0.0.1:5000/api/cirurgia/alterar_status"
payload = {
    "prontuario": "123456",
    "data": "2025-06-17",
    "novo_status": "realizada"
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.text)
