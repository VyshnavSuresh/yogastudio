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
time.sleep(5)

driver.get("http://127.0.0.1:8000/instructorchangepassword")

oldpass_field = driver.find_element(By.NAME, "old_password")
oldpass_field.send_keys(str("Anitha1"))

newpass_field = driver.find_element(By.NAME, "new_password")
newpass_field.send_keys(str("Anitha2"))


conpass_field = driver.find_element(By.NAME, "confirm_password")
conpass_field.send_keys(str("Anitha2"))
conpass_field.send_keys(Keys.RETURN)
time.sleep(5)

driver.get("http://127.0.0.1:8000/login/")
username_field = driver.find_element(By.NAME, "email")
username_field.send_keys("city789vice@gmail.com")

password_field = driver.find_element(By.NAME, "password")
password_field.send_keys("Anitha2")
password_field.send_keys(Keys.RETURN)
time.sleep(5)

dashboard_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'INSTRUCTOR DASHBOARD')]")
if dashboard_element:
    print("Test Passed")
else:
    print("Test Failed")
time.sleep(3)
driver.quit()
