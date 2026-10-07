import requests

url = "http://127.0.0.1:17493/generate"
body = """{
  "profile_id": "46c660d0-68b9-44ef-94bb-62a7ecf6308c",
  "text": "Bonjour et bienvenue dans notre laboratoire STEM. Aujourd'hui, nous allons découvrir comment fonctionne un ESP32."
}"""
response = requests.request("POST", url, data = body, headers = {
  "Content-Type": "application/json"
})

print(response.text)


