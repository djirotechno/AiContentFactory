import requests

url = "http://localhost:8000/models/download"
body = """{
  "model_name": "qwen-tts-1.7B"
}"""
response = requests.request("POST", url, data = body, headers = {
  "Content-Type": "application/json"
})

print(response.text)