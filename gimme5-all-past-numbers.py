from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import os
from datetime import datetime
import re
import time
import random

LOTTERY_LAUNCH_DATE = datetime(2013, 5, 12)
DATA_FILE = "gimme5_data.json"

def fetch_lottery_data(url):
    """Fetches Gimme 5 lottery data from the given URL using Selenium."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        # ... add more user-agents
    ]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(random.uniform(5, 15))  # Longer initial delay
        print(driver.page_source)  # Print HTML for debugging

        # Scroll the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 7))

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        return driver.page_source
    except TimeoutException:
        print("Timeout waiting for page to load.")
        return None
    finally:
        driver.quit()

def parse_lottery_data(html):
    """Parses the Gimme 5 lottery data from the <pre> tag."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    pre_tag = soup.find("pre")

    if not pre_tag:
        print("Could not find the <pre> tag containing lottery data.")
        return []

    data = []

    text = pre_tag.text
    lines = text.strip().split('\n')

    for line in lines:
        # Use a regular expression to extract date and numbers
        match = re.search(r'(\d{1,2}/\d{1,2}/\d{2})\s+([A-Z]{3})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
        if match:
            date_str = match.group(1)
            numbers = [int(match.group(i)) for i in range(3, 8)]

            try:
                date = datetime.strptime(date_str, "%m/%d/%y")
                if date >= LOTTERY_LAUNCH_DATE:
                    data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "numbers": numbers,
                    })
            except ValueError:
                print(f"Error parsing date: {date_str}")

    return data

def load_existing_data():
    """Loads existing Gimme 5 lottery data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Error decoding JSON data. Returning empty data.")
                return []
    return []

def save_data(data):
    """Saves the Gimme 5 lottery data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_lottery_data(url):
    """Fetches, parses, and updates Gimme 5 lottery data, saving only new entries."""
    existing_data = load_existing_data()
    latest_existing_date_str = existing_data[0]["date"] if existing_data else None

    html = fetch_lottery_data(url)
    if not html:
        return

    all_data = parse_lottery_data(html)

    # Handle case when no data has ever been downloaded
    if not latest_existing_date_str:
        save_data(all_data)
        print("Initial data downloaded.")
        return

    new_data = []
    latest_existing_date = datetime.strptime(latest_existing_date_str, "%Y-%m-%d")

    for item in all_data:
        item_date = datetime.strptime(item["date"], "%Y-%m-%d")
        if item_date > latest_existing_date:
            new_data.append(item)

    if new_data:
        updated_data = new_data + existing_data
        save_data(updated_data)
        print(f"Added {len(new_data)} new entries.")
    else:
        print("No new data found.")

if __name__ == "__main__":
    # Correct URL for all Gimme 5 results
    url = "https://www.mainelottery.com/cgi/all.results.pl"
    update_lottery_data(url)