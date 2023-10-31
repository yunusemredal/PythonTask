import requests

url = "https://api.baubuddy.de/index.php/login"

payload = {
    "username": "365",
    "password": "1"
}

headers = {
    "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)


data = response.json()
if "oauth" in data and "access_token" in data["oauth"]:
    access_token = data["oauth"]["access_token"]
    print("Access Token:", access_token)
else:
    print("Access Token bulunamadı.")
