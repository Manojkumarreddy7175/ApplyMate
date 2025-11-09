import os
from dotenv import load_dotenv
from google.generativeai import configure, list_models

load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    models = list_models()
    for model in models:
        print(f"Name: {model.name}")
        print(f"Supported generation methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error: {e}")
