import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

service = Service(executable_path=r"\Users\city7\OneDrive\Desktop\FINAL\yogastudio\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("http://127.0.0.1:8000/login/")

# Locate the username and password fields and input the credentials
username_field = driver.find_element(By.NAME, "email")
username_field.send_keys("malavikaanitha14@gmail.com")

password_field = driver.find_element(By.NAME, "password")
password_field.send_keys("Mala1")

# Submit the login form
password_field.send_keys(Keys.RETURN)

# Wait for the page to load and check for the presence of the dashboard element
dashboard_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'STUDENT DASHBOARD')]")
if dashboard_element:
    print("Test Passed")
else:
    print("Test failed.")

driver.get("http://127.0.0.1:8000/product")
driver.get("http://127.0.0.1:n8000/addcart/1")
time.sleep(5)
product_addcart = driver.find_element(By.XPATH, "//div[contains(text(), 'Product Already in the cart')]")

if product_addcart:
    print("Test Passed")
else:
    print("Test Failed")

# driver.get("http://127.0.0.1:8000/cart")
time.sleep(5)
# Close the browser
driver.quit()
