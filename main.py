import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

TRACKING_URL = "***REMOVED***"

APP_TOKEN = "***REMOVED***"
USER_KEY = "***REMOVED***"

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")

service = Service(EdgeChromiumDriverManager().install())

driver = webdriver.ChromiumEdge(options=options, service=service)

driver.get(TRACKING_URL)

page_loaded = False

# Wait for page loading
while not page_loaded:
    try:
        driver.find_element(By.CSS_SELECTOR, ".el-loading-mask")

    except NoSuchElementException:
        page_loaded = True

print("tracking page loaded")
# driver.get_screenshot_as_file("screenshot.png")

# Get last tracking status
timeline = driver.find_elements(By.CSS_SELECTOR, ".timeline-main.clearfix")

timeline = [item for item in timeline if item.text != ""]
last_update = timeline[0].text
last_update = last_update.replace("\n", " ")

print(last_update)

# Read last status from file
with open("status.txt", "r+") as file:
    file_status = file.read()

    if last_update != file_status:
        # Update file
        file.seek(0)
        file.write(last_update)
        file.truncate()

        # Send push notification
        result = requests.post("https://api.pushover.net/1/messages.json", json={
            "token": APP_TOKEN,
            "user": USER_KEY,
            "message": last_update
        })
        result.raise_for_status()
        print("notification sent")

    else:
        print("up to date")
