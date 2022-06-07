#!/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import subprocess
from datetime import date
import time

def get_login_credentials():
    user = os.getlogin()
    if ( user == 'alex' ):
        out = subprocess.check_output(['pass', 'show', 'Fitness/cronometer'])
        # using a multi line password file for user and pw
        email_login = out.decode("utf-8").split('\n')[1].split(': ')[1]
        password_login = out.decode("utf-8").split('\n')[0]
    elif ( user == 'till'):
        email_login = 'spam@dieminger.ch' #TODO
        out = subprocess.check_output(['pass', 'show', 'cronometer.com/spam@dieminger.ch'])
        password_login = out.decode("utf-8")
    else:
        email_login = os.environ.get('RN_EMAIL')
        password_login = os.environ.get('RN_PW')
        assert email_login and password_login, "please setup credential get method for this user or use env vars (RN_EMAIL & RN_PW)"

    return email_login, password_login

def login_to_cronometer(email_login, password_login):
    driver.get("https://cronometer.com/login/")
    email_input = driver.find_element(by=By.CSS_SELECTOR, value="input#usernameBox.textbox--1.login-fields")
    password_input = driver.find_element(by=By.CSS_SELECTOR, value="input#password.textbox--1.login-fields")
    email_input.send_keys(email_login)
    password_input.send_keys(password_login)
    button = driver.find_element(by=By.CSS_SELECTOR, value="button#login-button.submit--1.login-fields")
    button.click()
    WebDriverWait(driver, timeout=10).until(lambda d: d.title != "Cronometer Login")

def remove_cookie_banner():
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//button[@class="ncmp__btn"]'))).click()


def change_meta_data(recipe_name):
    today = date.today()
    name_box = driver.find_element(By.XPATH, '//input[@title="New Recipe"]')
    name_box.click()
    name_box.clear()
    name_box.send_keys(recipe_name)
    notes_box = driver.find_element(By.XPATH,'//textarea[@class="gwt-TextArea"]')
    notes_box.click()
    notes_box.send_keys(f"Added on {today.strftime('%d.%m.%Y')}")

def change_serving_size(serving_size):
    serving_size_image = driver.find_element(By.XPATH, value="//img[@title='Add Measure']")
    serving_size_image.click()
    serving_size_field = driver.find_element(By.XPATH, value='/html/body/div[1]/div[4]/div[2]/div[3]/div/div/table/tbody/tr[2]/td/div/div[1]/div/div/div[2]/div[2]/div[2]/div[4]/div[1]/div[5]/div[2]/table/tbody/tr/td/table/tbody/tr[2]/td[3]')
    serving_size_field.click()
    serving_size_field = driver.find_element(By.XPATH, value='/html/body/div[1]/div[4]/div[2]/div[3]/div/div/table/tbody/tr[2]/td/div/div[1]/div/div/div[2]/div[2]/div[2]/div[4]/div[1]/div[5]/div[2]/table/tbody/tr/td/table/tbody/tr[2]/td[3]/input')
    serving_size_field.send_keys(serving_size)

def save_recipe():
    save_button = driver.find_element(By.XPATH, value="//button[text()='Save Changes']")
    save_button.click()

def export_recipe():
    time.sleep(1)
    menu_button = driver.find_element(By.XPATH, value="/html/body/div[1]/div[4]/div[2]/div[3]/div/div/table/tbody/tr[2]/td/div/div[1]/div/div/div[2]/div[2]/div[2]/div[1]/img")
    menu_button.click()
    export_div = driver.find_element(By.XPATH, value="//div[contains(@class, 'gwt-Label') and text()='Export to CSV File...']")
    export_div.click()

email_login, password_login = get_login_credentials()

chrome_options = Options()
chrome_options.add_argument('--force-device-scale-factor=1.5')
chrome_options.page_load_strategy = 'normal'

driver = webdriver.Chrome(options=chrome_options)
#works for login, consider slowing down for other parts or using waits
#https://www.selenium.dev/documentation/webdriver/capabilities/shared/#pageloadstrategy
#https://www.selenium.dev/documentation/webdriver/waits/
login_to_cronometer(email_login, password_login)

driver.get("https://cronometer.com/#foods")

remove_cookie_banner()

add_recipe = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.XPATH, value="//button[text()='+ Add Recipe']"))
add_recipe.click()


change_meta_data("test")
change_serving_size("5")

time.sleep(20)

save_recipe()
export_recipe()
time.sleep(1)
