import requests

url = "https://6240-34-19-101-6.ngrok-free.app/generate"  

data = {
    "text": "the course has already started, can I still enroll?",
    "max_length": 50
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("Generated Text:", response.json().get("generated_text"))
else:
    print("Request failed with status code:", response.status_code)