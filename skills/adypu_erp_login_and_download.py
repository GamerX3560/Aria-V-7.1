from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

# Set up the Firefox driver
driver = webdriver.Firefox()

# Open the ADYPU ERP login page
driver.get("https://adypu-erp.com/login.php")

# Wait for the page to load
time.sleep(5)

# Find the username and password fields and enter the credentials
try:
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
except:
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

username_field.send_keys("2024-B-31072004")
password_field.send_keys("2024-B-31072004")

# Click the login button
login_button = driver.find_element(By.NAME, "login")
login_button.click()

# Wait for the page to load
time.sleep(10)

# Navigate to the transcript section
# Update the following line with the correct attribute
transcript_link = driver.find_element(By.ID, "correct_id_for_transcript_link")
transcript_link.click()

# Wait for the page to load
time.sleep(10)

# Download the transcript
# Update the following line with the correct attribute
download_button = driver.find_element(By.ID, "correct_id_for_download_button")
download_button.click()

# Wait for the download to complete
time.sleep(10)

# Close the browser
driver.quit()
