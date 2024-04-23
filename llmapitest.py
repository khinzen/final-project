# This example is the new way to use the OpenAI lib for python
from openai import OpenAI

client = OpenAI(
api_key = "LL-JsXHgYMuGCr4WmyOeWH5tVD03o57tlJBFXTJG5v2WsnybEoMB01JzbJWkZ8unAg7",
base_url = "https://api.llama-api.com"
)

response = client.chat.completions.create(
model="llama-13b-chat",
messages=[
    {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
    {"role": "user", "content": "How did world war II start?"}
]
)

print(response.choices[0].message.content)

