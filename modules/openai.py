from openai import OpenAI
import base64
import requests

# OpenAI API Key
api_key = "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"

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "images/acf.png"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What’s in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())

# Point to the local server
client = OpenAI(base_url="http://localhost:4192/v1", api_key="lm-studio")

completion = client.chat.completions.create(
  model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
  messages=[
    {"role": "system", "content": "请始终使用中文回答问题"},
    {"role": "user", "content": "请介绍一下你自己"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)