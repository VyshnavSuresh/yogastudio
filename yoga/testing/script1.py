import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

service = Service(executable_path=r"\Users\city7\OneDrive\Desktop\FINAL\yogastudio\chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("http://127.0.0.1:8000/login/")

username_field = driver.find_element(By.NAME, "email")
username_field.send_keys("city789vice@gmail.com")

password_field = driver.find_element(By.NAME, "password")
password_field.send_keys("Anitha1")
password_field.send_keys(Keys.RETURN)


dashboard_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'INSTRUCTOR DASHBOARD')]")
if dashboard_element:
    print("Test Passed")
else:
    print("Test failed.")
time.sleep(3)
driver.quit()
