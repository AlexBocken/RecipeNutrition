#!/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import os
import subprocess

def get_login_credentials():
    user = os.getlogin()
    if ( user == 'alex' ):
        out = subprocess.check_output(['pass', 'show', 'Fitness/cronometer'])
        # using a multi line password file for user and pw
        email_login = out.decode("utf-8").split('\n')[1].split(': ')[1]
        password_login = out.decode("utf-8").split('\n')[0]
    elif ( user == 'till'):
        email_login = '<email>' #TODO
        out = subprocess.check_output(['pass', 'show', 'Fitness/cronometer'])
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

def add_ingredient(amount, ingredient):
    '''Assumes that it starts on recipe page and adds one ingredient
    to the recipe
    amount: string which needs to be parsed to understand
                a) amount
                b) unit
    ingredient: string with name for ingredient
    '''
    img = driver.find_element(By.XPATH, value="//img[@title='Add Ingredient']")
    print('Found Add ingredient img')
    img.click()
    search = driver.find_element(By.CSS_SELECTOR, value="div > img + input")
    search.send_keys(ingredient)
    ingredient_popup = driver.find_element(By.XPATH, value='//div[@class="popupContent"]')
    #first_result= ingredient_popup.find_element(By.XPATH, value='/div/div[@class="titlebar"]/following-sibling::div/div/div/div/div/div/div/table/tbody/tr[@class="prettyTable-header"]/following-sibling::tr[1]/td[1]')
    ingredient_popup.find_element(By.XPATH, value="//img/following-sibling::button[text()='Search']").click()
    first_result= ingredient_popup.find_element(By.XPATH, value='//tr[@class="prettyTable-header"]/following-sibling::tr[1]/td[1]')
    first_result.click()


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
add_recipe = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.XPATH, value="//button[text()='+ Add Recipe']"))
add_recipe.click()
WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.XPATH, value="//img[@title='Add Ingredient']"))
add_ingredient("300 g", "Magerquark")

#print(test)
