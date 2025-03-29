from pydantic import BaseModel
from typing import List, Optional

class Activity(BaseModel):
  id: str
  name: Optional[str]
  target_muscle_group: Optional[str]
  activity_type: Optional[str]
  mechanics: Optional[str]
  force_type: Optional[str]
  experience_level: Optional[str]
  secondary_muscles: Optional[str]
  equipment: Optional[str]
  overview: Optional[str]
  instructions: Optional[str]
  tips: Optional[str]
  image_url: Optional[str]
  video_url: Optional[str]
  muscle_group_image_url: Optional[str]
  calories_125lbs: Optional[int]
  calories_155lbs: Optional[int]
  calories_185lbs: Optional[int]
  data_links: List[str]

