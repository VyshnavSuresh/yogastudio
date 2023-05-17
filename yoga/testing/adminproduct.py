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
username_field.send_keys("admin")

password_field = driver.find_element(By.NAME, "password")
password_field.send_keys("admin")

# Submit the login form
password_field.send_keys(Keys.RETURN)

driver.get("http://127.0.0.1:8000/login/admin/yogaapp/product/add/")

# Locate the username and password fields and input the credentials
productname_field = driver.find_element(By.NAME, "name")
productname_field .send_keys("Yoga Bag")

category_field = driver.find_element(By.NAME, "category")
category_field .send_keys("Bag")


productimage_field = driver.find_element(By.NAME, "product_image")
productimage_field.send_keys(r"C:\Users\city7\OneDrive\Desktop\FINAL\yogastudio\file\product_image\yogabag.jpeg")

price_field = driver.find_element(By.NAME, "price")
price_field.send_keys("100")

stock_field = driver.find_element(By.NAME, "stock")
stock_field.send_keys("1")


desc_field = driver.find_element(By.NAME, "description")
desc_field .send_keys("Yoga Bag for everyday purposes. ")

desc_field.send_keys(Keys.RETURN)
time.sleep(2)
driver.get("http://127.0.0.1:8000/login/admin/yogaapp/product/")
time.sleep(5)

# Wait for the page to load and check for the presence of the dashboard element
dashboard_element = driver.find_element(By.XPATH, "//h1[contains(text(), 'Select product to change')]")
if dashboard_element:
    print("Test Passed")
else:
    print("Test failed.")

