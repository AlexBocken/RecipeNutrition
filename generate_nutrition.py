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
        email_login = 'spam@dieminger.ch'
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

def highlight(element, effect_time, color, border):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)
    original_style = element.get_attribute('style')
    apply_style("border: {0}px solid {1};".format(border, color))
    time.sleep(effect_time)
    apply_style(original_style)

def change_serving_size(serving_size):
    serving_size_image = driver.find_element(By.XPATH, value="//img[@title='Add Measure']")
    serving_size_image.click()
    serving_size_field = driver.find_element(By.XPATH, value='//div[text()="Servings Per Recipe"]/parent::td/parent::tr/parent::tbody/tr[2]/td[3]')
    serving_size_field.click()
    serving_size_field = driver.find_element(By.XPATH, value='//div[text()="Servings Per Recipe"]/parent::td/parent::tr/parent::tbody/tr[2]/td[3]/input')
    serving_size_field.send_keys(serving_size)

def save_export_recipe(save_location,save_name):
    save_button = driver.find_element(By.XPATH, value="//button[text()='Save Changes']")
    save_button.click()
    time.sleep(1) # Wait for website to save the file
    menu_button = driver.find_element(By.XPATH, value="//div[@class='GO-RHEKCA3']/img")
    menu_button.click()
    export_div = driver.find_element(By.XPATH, value="//div[contains(@class, 'gwt-Label') and text()='Export to CSV File...']")
    export_div.click()
    time.sleep(2) # wait for file to be downloaded
    os.system(f"mv {save_location}/food.csv {save_location}/{save_name}.csv") # move file to be named after recipe

email_login, password_login = get_login_credentials()

# INPUT FROM PARSER
save_location = "/tmp/nutrition"
titel="Name des Rezeptes"
save_name=titel.replace(" ", "_").lower()
serving_size = 5


chrome_options = Options()
chrome_options.add_argument('--force-device-scale-factor=1.5')
chrome_options.page_load_strategy = 'normal'
prefs = {"download.default_directory": save_location,"download.prompt_for_download": False, "download.directory_upgrade": True }
chrome_options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(options=chrome_options)
#works for login, consider slowing down for other parts or using waits
#https://www.selenium.dev/documentation/webdriver/capabilities/shared/#pageloadstrategy
#https://www.selenium.dev/documentation/webdriver/waits/
login_to_cronometer(email_login, password_login)

driver.get("https://cronometer.com/#foods")

remove_cookie_banner()

add_recipe = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.XPATH, value="//button[text()='+ Add Recipe']"))
add_recipe.click()
change_meta_data(titel)
change_serving_size(serving_size)

# TODO RECIPE LOOP HERE - Time for manual edit
time.sleep(20)


save_export_recipe(save_location, save_name)
