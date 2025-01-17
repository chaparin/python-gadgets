import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

LOTTERY_LAUNCH_DATE = datetime(2013, 5, 12)  # Assuming Gimme 5 also started on this date
DATA_FILE = "gimme5_data.json"


def fetch_lottery_data(url):
    """Fetches Gimme 5 lottery data from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def parse_lottery_data(html):
    """Parses the Gimme 5 lottery data from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    draws_container = soup.find("div", class_="draws-container")

    if not draws_container:
        print("Could not find the Gimme 5 draws container.")
        return []

    data = []
    for draw in draws_container.find_all("div", class_="single-draw"):
        date_str = draw.find("div", class_="date").text.strip()

        try:
            date = datetime.strptime(date_str, "%d %b %Y")
            if date >= LOTTERY_LAUNCH_DATE:
                numbers = []
                for ball in draw.find_all("span", class_="ball"):
                    numbers.append(int(ball.text.strip()))

                data.append({
                    "date": date.strftime("%Y-%m-%d"),  # Format date to YYYY-MM-DD
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
    # CORRECT URL FOR GIMME 5
    url = "https://www.mainelottery.com/games/gimme5-previous.html"
    update_lottery_data(url)