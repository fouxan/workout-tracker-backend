import os
import json
import time
import requests
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

# Path to your ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"  # Replace with the path to your chromedriver

# Set up the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.muscleandstrength.com/",
}

# Database setup
DATABASE_NAME = "fitness.db"

def download_image(url, path, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(path, "wb") as image_file:
                    for chunk in response.iter_content(1024):
                      image_file.write(chunk)
                return True
            else:
                print(f"Failed to download image (attempt {i + 1}): {url}")
        except Exception as e:
            print(f"Error downloading image (attempt {i + 1}): {e}")
        time.sleep(2)  # Wait before retrying
    return False


def create_activities_table():
    """Create the `activities` table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Delete table if already exists
    cursor.execute("DROP TABLE IF EXISTS activities")

    # Create activities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            name TEXT,
            target_muscle_group TEXT DEFAULT NULL,
            activity_type TEXT DEFAULT NULL,
            mechanics TEXT DEFAULT NULL,
            force_type TEXT DEFAULT NULL,
            experience_level TEXT DEFAULT NULL,
            secondary_muscles TEXT DEFAULT NULL,
            equipment TEXT DEFAULT NULL,
            overview TEXT DEFAULT NULL,
            instructions TEXT DEFAULT NULL,
            tips TEXT DEFAULT NULL,
            image_url TEXT DEFAULT NULL,
            video_url TEXT DEFAULT NULL,
            muscle_group_image_url TEXT DEFAULT NULL,
            calories_125lbs INTEGER DEFAULT 0,
            calories_155lbs INTEGER DEFAULT 0,
            calories_185lbs INTEGER DEFAULT 0,
            data_links TEXT DEFAULT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_to_database(exercise_data):
    """Save exercise data to the `activities` table and update `items` with activity IDs."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert or replace activity data
    cursor.execute("""
        INSERT OR REPLACE INTO activities (
            id, name, target_muscle_group, activity_type, mechanics, force_type,
            experience_level, secondary_muscles, equipment, overview, instructions,
            tips, image_url, video_url, muscle_group_image_url, calories_125lbs, calories_155lbs, calories_185lbs, data_links
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        exercise_data.get("id"),
        exercise_data.get("name"),
        exercise_data.get("target_muscle_group", ""),
        exercise_data.get("activity_type", ""),
        exercise_data.get("mechanics", ""),
        exercise_data.get("force_type", ""),
        exercise_data.get("experience_level", ""),
        exercise_data.get("secondary_muscles", ""),
        exercise_data.get("equipment", ""),
        exercise_data.get("overview", ""),
        exercise_data.get("instructions", ""),
        exercise_data.get("tips", ""),
        exercise_data.get("media-links", {}).get("exercise", ""),
        exercise_data.get("media-links", {}).get("video", ""),
        exercise_data.get("media-links", {}).get("muscle-group", ""),
        exercise_data.get("calories_125lbs", 0),
        exercise_data.get("calories_155lbs", 0),
        exercise_data.get("calories_185lbs", 0),
        json.dumps(exercise_data.get("data-links"))
    ))

    # Update the `items` table with the activity ID
    cursor.execute("""
        UPDATE items
        SET activity_ids = ?
        WHERE name = ?
    """, (
        exercise_data["id"],
        exercise_data.get("target_muscle_group")  # Assuming `items.name` matches `target_muscle_group`
    ))

    conn.commit()
    conn.close()



def scrape_exercise_links(driver, muscle_group_url, category_name):
    """Scrape exercise links and metadata from a muscle group page."""
    driver.get(muscle_group_url)
    exercise_links = []

    # Create the base folder for the category
    base_folder = os.path.join("exercises", category_name.lower().replace(" ", "-"))
    os.makedirs(base_folder, exist_ok=True)

    while True:
        # Wait for the exercise cells to load
        wait = WebDriverWait(driver, 10)
        exercise_cells = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.taxonomy-body div.cell.small-12.bp600-6"))
        )

        # Extract exercise links and metadata
        for cell in exercise_cells:
            try:
                # Extract the exercise URL
                link_tag = cell.find_element(By.CSS_SELECTOR, "div.node-title a[href]")
                exercise_url = link_tag.get_attribute("href")
                if not exercise_url.startswith("https://www.muscleandstrength.com"):
                  exercise_url = "https://www.muscleandstrength.com" + exercise_url

                # Extract metadata (type, equipment, mechanics, experience level)
                meta_boxes = cell.find_elements(By.CSS_SELECTOR, "div.exercise-meta div.meta-box")
                metadata = {
                    "type": meta_boxes[0].text.strip() if len(meta_boxes) > 0 else None,
                    "equipment": meta_boxes[1].text.strip() if len(meta_boxes) > 1 else None,
                    "mechanics": meta_boxes[2].text.strip() if len(meta_boxes) > 2 else None,
                    "experience_level": meta_boxes[3].text.strip() if len(meta_boxes) > 3 else None,
                }

                # Extract the thumbnail image URL
                thumbnail_tag = cell.find_element(By.CSS_SELECTOR, "div.node-image img[src]")
                thumbnail_url = thumbnail_tag.get_attribute("src")

                # Download the thumbnail image
                exercise_name = link_tag.text.strip().lower().replace(" ", "-")
                image_filename = f"{exercise_name}.jpg"
                image_path = os.path.join(base_folder, image_filename)

                download_image(thumbnail_url, image_path)

                # Add the exercise URL, metadata, and image path to the list
                exercise_links.append({
                    "url": exercise_url,
                    "name": link_tag.text.strip(),
                    "metadata": metadata,
                    "image_path": image_path,
                    "image_url": thumbnail_url
                })
            except Exception as e:
                print(f"Error extracting exercise data: {e}")
                continue

        # Check for a "Next" button and click it if it exists
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.pager-next > a[href]")
            if "disabled" in next_button.get_attribute("class"):
                break  # Exit if there's no next page
            next_button.click()
            time.sleep(2)  # Wait for the next page to load
        except:
            print("No more pages to load.")
            print(f"Found {len(exercise_links)} Exercises for {category_name} ")
            break  # Exit if no "Next" button is found

    return exercise_links

def scrape_exercise_data(driver, exercise_url, exercise_image, exercise_name):
    """Scrape detailed exercise data from an exercise page."""
    driver.get(exercise_url)
    exercise_data = {}

    try:
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)

        # Extract the YouTube video link
        try:
            video_iframe = driver.find_element(By.CSS_SELECTOR, "div.video-wrap iframe")
            video_url = video_iframe.get_attribute("src")
        except:
            video_url = None
        exercise_data["media-links"] = {
            "video": video_url
        }
        exercise_data["media-links"]["exercise"] = exercise_image

        # Extract metadata from the exercise profile
        metadata = {}
        profile_items = driver.find_elements(By.CSS_SELECTOR, "div.node-stats-block ul li")
        for item in profile_items:
            label = item.find_element(By.CSS_SELECTOR, "span.row-label").text.strip()
            if label == "Target Muscle Group":
                metadata["target_muscle_group"] = item.find_element(By.CSS_SELECTOR, "a").text.strip()
            elif label == "Exercise Type":
                metadata["activity_type"] = item.text.replace(label, "").strip()
            elif label == "Equipment Required":
                metadata["equipment"] = item.text.replace(label, "").strip()
            elif label == "Mechanics":
                metadata["mechanics"] = item.text.replace(label, "").strip()
            elif label == "Force Type":
                metadata["force_type"] = item.text.replace(label, "").strip()
            elif label == "Experience Level":
                metadata["experience_level"] = item.text.replace(label, "").strip()
            elif label == "Secondary Muscles":
                metadata["secondary_muscles"] = item.find_element(By.CSS_SELECTOR, "div.field-type-list-text").text.strip()

        exercise_data.update(metadata)

        # Extract the muscle group image
        try:
            muscle_group_img = driver.find_element(By.CSS_SELECTOR, "div.target-muscles img")
            muscle_group_img_url = muscle_group_img.get_attribute("src")
            exercise_data["media-links"]["muscle-group"] = muscle_group_img_url
        except:
            exercise_data["media-links"]["muscle-group"] = None

        # Extract the exercise overview
        try:
            overview = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-exercise-overview")
            exercise_data["overview"] = overview.text.strip()
        except:
            exercise_data["overview"] = None

        # Extract the exercise instructions
        try:
            instructions = driver.find_element(By.CSS_SELECTOR, "div.field-name-body")
            exercise_data["instructions"] = instructions.text.strip()
        except:
            exercise_data["instructions"] = None

        # Extract the exercise tips
        try:
            tips = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-exercise-tips")
            exercise_data["tips"] = tips.text.strip()
        except:
            exercise_data["tips"] = None

        # Add the exercise URL
        exercise_data["data-links"] = [exercise_url]

        # Add a placeholder ID (you can generate a unique ID if needed)
        exercise_data["id"] = exercise_url.split("/")[-1].replace(".html", "")
        exercise_data["name"] = exercise_name

    except Exception as e:
        print(f"Error scraping {exercise_url}: {e}")
        return None
    
    print("Scraped exercise data: ", exercise_data["name"])

    return exercise_data

def main():
    # Create the database and tables
    create_activities_table()

    # Load categories from the JSON file
    with open('categories.json', 'r') as file:
        data = json.load(file)
    
    categories = data['categories']

    # Iterate through each category and its items
    for category in categories:
        for item in category['items']:
            print(f"Scraping exercises from: {item['name']} - {item['url']}")

            # Scrape exercise links and thumbnails
            exercise_links = scrape_exercise_links(driver, item['url'], item['name'])

            # Scrape detailed data for each exercise
            for exercise in exercise_links:
                print(f"Scraping exercise: {exercise['url']}")
                exercise_data = scrape_exercise_data(driver, exercise["url"], exercise["image_url"], exercise['name'])

                if exercise_data:
                    # Save exercise data to the database
                    save_to_database(exercise_data)

                    # Create a folder for the exercise
                    exercise_folder = os.path.join("exercises", item['name'].lower().replace(" ", "-"), exercise_data["id"])
                    os.makedirs(exercise_folder, exist_ok=True)

                    # Save the thumbnail image
                    try:
                      thumbnail_path = os.path.join(exercise_folder, "thumbnail.jpg")
                      if not download_image(exercise["image_url"], thumbnail_path):
                          print(f"Failed to download thumbnail: {exercise['image_url']}")

                      # Save the muscle group image (if available)
                      if exercise_data["media-links"]["muscle-group"]:
                          muscle_group_image_url = exercise_data["media-links"]["muscle-group"]
                          muscle_group_image_path = os.path.join(exercise_folder, "muscle-group.jpg")
                          if not download_image(muscle_group_image_url, muscle_group_image_path):
                              print(f"Failed to download muscle group image: {muscle_group_image_url}")

                      # Save exercise metadata and image paths to a JSON file
                      metadata = {
                          "name": exercise_data.get("name"),
                          "target_muscle_group": exercise_data.get("target_muscle_group"),
                          "activity_type": exercise_data.get("activity_type"),
                          "mechanics": exercise_data.get("mechanics"),
                          "force_type": exercise_data.get("force_type"),
                          "experience_level": exercise_data.get("experience_level"),
                          "secondary_muscles": exercise_data.get("secondary_muscles"),
                          "equipment": exercise_data.get("equipment"),
                          "image_paths": {
                              "thumbnail": thumbnail_path,
                              "muscle_group": muscle_group_image_path if exercise_data.get("media-links").get("muscle-group") else None
                          }
                      }

                      json_filename = f"{exercise_data['id']}.json"
                      json_path = os.path.join(exercise_folder, json_filename)
                      with open(json_path, "w") as json_file:
                          json.dump(metadata, json_file, indent=4)

                      print(f"Saved exercise data: {json_path}")
                    except Exception as e:
                      print(f"Error saving exercise data: {e}")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()