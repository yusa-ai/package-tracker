import os

import gspread
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# URL to track shipping (should probably contain the tracking number as a GET parameter)
TRACKING_URL = os.environ.get("TRACKING_URL")

# Google Sheets API
GOOGLE_CREDENTIALS = {
  "type": "service_account",
  "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
  "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
  "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
  "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
  "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL")
}
GOOGLE_SPREADSHEET_NAME = "package-tracker"

# Pushover API
PUSHOVER_APP_TOKEN = os.environ.get("PUSHOVER_APP_TOKEN")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")


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

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# THIS MAKES SURE THAT THE CONTENTS OF THE WEBPAGE (STATUS 
# UPDATES) ARE FULLY LOADED BEFORE SCRAPING AND YOU SHOULD 
# PROBABLY EDIT IT
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Wait for page loading
while not page_loaded:
    try:
        # Webpage displays a loading animation with a spinning wheel 
        # while loading my package's data
        driver.find_element(By.CSS_SELECTOR, ".el-loading-mask")

    # The loading animation is gone so the page is done rendering
    except NoSuchElementException:
        page_loaded = True

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# THIS HAS TO BE EDITED DEPENDING ON THE TRACKING WEBSITE SO THAT 
# latest_update CONTAINS YOUR PACKAGE'S LATEST STATUS AS A STRING
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Get latest tracking status
updates = driver.find_elements(By.CSS_SELECTOR, ".timeline-main.clearfix")
updates = [item for item in update if item.text != ""]
latest_update = updates[0].text
latest_update = latest_update.replace("\n", " ")

# Initialize Google Spreadsheet
gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
sh = gc.open(GOOGLE_SPREADSHEET_NAME)
worksheet = sh.get_worksheet(0)

# Read latest status from Google Sheets
saved_status = worksheet.acell("A1").value

if latest_update != saved_status:
    # Update Google Sheets
    worksheet.update("A1", latest_update)

    # Send push notification
    result = requests.post("https://api.pushover.net/1/messages.json", json={
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": latest_update
    })
    result.raise_for_status()
    print(f"[PackageTracker] Notification sent: {latest_update}")

else:
    print(f"[PackageTracker] Package status up to date")
