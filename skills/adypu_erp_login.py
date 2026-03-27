from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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

# Take a screenshot
driver.save_screenshot("/tmp/adypu_erp_screenshot.png")

# Close the browser
driver.quit()
