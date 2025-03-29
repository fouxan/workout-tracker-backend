from google import genai

client = genai.Client(api_key="AIzaSyAKPBbfsR0mgEGUBfOslnnEMn9l1xaAU4A")

def generate_content(prompt, model="gemini-2.0-flash"):
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text