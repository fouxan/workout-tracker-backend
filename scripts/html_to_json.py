from bs4 import BeautifulSoup
import json

def html_to_json(html_file, json_file):
    # Load the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table rows
    rows = soup.find_all('tr')

    # Initialize a list to store the data
    data = []

    # Iterate through the rows (skip the header row)
    for row in rows[1:]:
        cells = row.find_all('td')
        if len(cells) == 5:  # Ensure the row has the correct number of columns
            activity = cells[0].get_text(strip=True)
            calories_130lb = int(cells[1].get_text(strip=True))
            calories_155lb = int(cells[2].get_text(strip=True))
            calories_180lb = int(cells[3].get_text(strip=True))
            calories_205lb = int(cells[4].get_text(strip=True))

            # Add the data to the list
            data.append({
                "name": activity,
                "calories_130lb": calories_130lb,
                "calories_155lb": calories_155lb,
                "calories_180lb": calories_180lb,
                "calories_205lb": calories_205lb
            })

    # Save the data to a JSON file
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    print(f"Data saved to {json_file}")

# Example usage
html_file = 'activities.html'  # Replace with your HTML file path
json_file = 'activities.json'  # Replace with your desired JSON file path
html_to_json(html_file, json_file)