import os

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

TRACKING_URL = os.environ.get("TRACKING_URL")

# Pushover
APP_TOKEN = os.environ.get("APP_TOKEN")
USER_KEY = os.environ.get("USER_KEY")

# Sheety
SHEETY_ENDPOINT = os.environ.get("SHEETY_ENDPOINT")

options = Options()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.headless = True
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))

driver = webdriver.Chrome(options=options, service=service)


driver.get(TRACKING_URL)

page_loaded = False

# Wait for page loading
while not page_loaded:
    try:
        driver.find_element(By.CSS_SELECTOR, ".el-loading-mask")

    except NoSuchElementException:
        page_loaded = True

# driver.get_screenshot_as_file("screenshot.png")

# Get last tracking status
timeline = driver.find_elements(By.CSS_SELECTOR, ".timeline-main.clearfix")

timeline = [item for item in timeline if item.text != ""]
last_update = timeline[0].text
last_update = last_update.replace("\n", " ")

# Read last status from Google Sheets
response = requests.get(url=SHEETY_ENDPOINT)
response.raise_for_status()

response = response.json()
saved_status = response["packageTracker"][0]["response"]
row_id = response["packageTracker"][0]["id"]

if last_update != saved_status:
    # Update Google Sheets
    edit = requests.put(url=f"{SHEETY_ENDPOINT}/{row_id}", json={
        "packageTracker": {
            "response": last_update
        }
    })
    edit.raise_for_status()

    # Send push notification
    result = requests.post("https://api.pushover.net/1/messages.json", json={
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": last_update
    })
    result.raise_for_status()
    print(f"[PackageTracker] Notification sent: {last_update}")

else:
    print(f"[PackageTracker] Package status up to date")
