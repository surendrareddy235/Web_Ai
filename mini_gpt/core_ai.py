from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content": "you are a helpful assistant"},
            {"role":"user", "content":prompt}
        ]
    )
    return response.choices[0].message.content.strip()
