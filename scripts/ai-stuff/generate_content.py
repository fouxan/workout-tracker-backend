from utils.llm_connector import generate_content
from google import genai
from pydantic import BaseModel
import json

class ResponseSchema(BaseModel):
  id: str
  name: str
  target_muscle_group: str
  description: str
  activity_type: str
  mechanics: str
  force_type: str
  experience_level: str
  secondary_muscles: str
  equipment: str
  overview: str
  instructions: str
  tips: str
  video_url: str
  muscle_group_image_url: str
  exercise_image_url: str


client = genai.Client(api_key="AIzaSyAKPBbfsR0mgEGUBfOslnnEMn9l1xaAU4A")

def main():

  activities = []

  # Prompt for generating content
  for activity in activities:
    prompt = f"""
    Generate information based on your expertise in JSON format for the activity: {activity}. Use the below JSON Schema:
      {
        "id": "string",
        "name": "string",
        "target_muscle_group": "string",
        "description": "string",
        "activity_type": "string",
        "mechanics": "string",
        "force_type": "string",
        "experience_level": "string",
        "secondary_muscles": "string",
        "equipment": "string",
        "overview": "string",
        "instructions": "string",
        "tips": "string",
        "video_url": "string",
        "muscle_group_image_url": "string",
        "exercise_image_url": "string"
      }
    """

    response = client.models.generate_content(
      model='gemini-2.0-flash',
      contents=prompt,
      config={
          'response_mime_type': 'application/json',
          'response_schema': ResponseSchema,
      }
    )


    activities.append(response.text)