from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.get("https://cronometer.com")
login_link = driver.find_element(by=By.CSS_SELECTOR, value="a.link__hero-login")
login_link.click()
email_input = driver.find_element_by_css_selector("input#usernameBox.textbox--1.login-fields")
password_input = driver.find_element_by_css_selector("input#password.textbox--1.login-fields")
email_input.send_keys("alexander@bocken.org")
password_input.send_keys("PASSWORT")
test = driver.title
button = driver.find_element_by_css_selector("button#login-button.submit--1.login-fields")
button.click()
time.sleep(10)
foods_link = driver.find_element_by_link_text("Foods")
foods_link.click()
time.sleep(10)
add_recipe = driver.find_elements_by_name("+ Add Recipe")
#print(test)
