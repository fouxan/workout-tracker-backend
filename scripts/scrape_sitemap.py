from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Wait for the cells to load
import time

# Set up Chrome options (optional)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

# Path to your ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"  # Replace with the path to your chromedriver

# Set up the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the page
url = "https://www.muscleandstrength.com/exercises"

# Open the page
driver.get(url)

# Wait for the page to load (adjust sleep time as needed)
time.sleep(5)  # You can replace this with explicit waits for better reliability


wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
cells = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cell")))

# Extract links
links = []
for cell in cells:
    try:
        link_tag = cell.find_element(By.CSS_SELECTOR, "a[href]")
        full_url = "https://www.muscleandstrength.com" + link_tag.get_attribute("href")
        links.append(full_url)
    except:
        continue  # Skip if the element is not found

# Print the extracted links
for link in links:
    print(link)

# Optionally, save the links to a file
with open('muscle_group_links.txt', 'w') as file:
    for link in links:
        file.write(link + '\n')

print(f"Extracted {len(links)} links and saved to 'muscle_group_links.txt'.")

# Close the browser
driver.quit()