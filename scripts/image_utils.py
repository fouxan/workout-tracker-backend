from turtle import st
import requests
import time

url = 'https://cdn.muscleandstrength.com/sites/all/themes/mnsnew/images/taxonomy/exercises/muscle-groups/full/Shoulders.jpg'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.muscleandstrength.com/",
}

def download_image(url, path, retries=3):
  for i in range(retries):
    try:
      response = requests.get(url, headers=headers, stream=True)
      print(response)
      if response.status_code == 200:
        with open(path, 'wb') as image_file:
          for chunk in response.iter_content(1024):
            image_file.write(chunk)
          print(f"Downloaded image: {path}")
        return True
      else:
        print(f"Failed to download image (attempt {i + 1}): {url}")
    except Exception as e:
      print(f"Error downloading image (attempt {i + 1}): {e}")
    time.sleep(2)  # Wait before retrying
  return False

download_image(url, 'shoulders.jpg')  # Replace 'shoulders.jpg' with the desired file path