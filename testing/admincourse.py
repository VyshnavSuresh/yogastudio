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

driver.get("http://127.0.0.1:8000/login/admin/yogaapp/courses/add/")

# Locate the username and password fields and input the credentials
course_field = driver.find_element(By.NAME, "course")
course_field.send_keys("Meditation")


courseimage_field = driver.find_element(By.NAME, "course_image")
courseimage_field.send_keys(r"C:\Users\city7\OneDrive\Desktop\FINAL\yogastudio\file\course_image\yoga2.jpeg")

desc_field = driver.find_element(By.NAME, "desc")
desc_field .send_keys("Meditation is a practice in which an individual uses a technique – such as mindfulness, or focusing the mind ")


startdate_field = driver.find_element(By.NAME, "start_date")
startdate_field.send_keys("2023-05-18")

enddate_field = driver.find_element(By.NAME, "end_date")
enddate_field.send_keys("2023-06-18")

ins_field = driver.find_element(By.NAME, "user_id")
ins_field.send_keys("Anitha Kumari")

ins_field.send_keys(Keys.RETURN)

time.sleep(2)
driver.get("http://127.0.0.1:8000/login/admin/yogaapp/courses/")
time.sleep(5)

# Wait for the page to load and check for the presence of the dashboard element
dashboard_element = driver.find_element(By.XPATH, "//h1[contains(text(), 'Select Courses to change')]")
if dashboard_element:
    print("Test Passed")
else:
    print("Test failed.")

