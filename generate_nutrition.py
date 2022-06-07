#!/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
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
    email_input = driver.find_element(By.CSS_SELECTOR, value="input#usernameBox.textbox--1.login-fields")
    password_input = driver.find_element(By.CSS_SELECTOR, value="input#password.textbox--1.login-fields")
    email_input.send_keys(email_login)
    password_input.send_keys(password_login)
    button = driver.find_element(by=By.CSS_SELECTOR, value="button#login-button.submit--1.login-fields")
    button.click()
    WebDriverWait(driver, timeout=10).until(lambda d: d.title != "Cronometer Login")

def match_unit(select_list, amount, unit):
    if(unit == 'g'):
        for el in select_list:
            if el.text == 'g':
                return amount, el.text
    elif(unit == 'EL'):
        for el in select_list:
            if 'tbsp' in el.text: #TODO: check whether fraction units of tbsp exist
                return amount, el.text
    elif(unit == 'TL'):
        for el in select_list:
            if 'tsp' in el.text: #TODO: check whether fraction units of tsp exist
                return amount, el.text
    # generic catcher
    else:
        for el in select_list:
            if el.text == unit:
                return amount, el.text
        print("Found no matching unit") #TODO: soft catch and continue
        exit(1)

def add_ingredient(amount, unit, ingredient):
    '''Assumes that it starts on recipe page and adds one ingredient
    to the recipe
    amount: int/float with amount in later specified unit
    unit: unit of amount (e.g. "g" for grams)
    ingredient: string with name for ingredient
    '''
    #go to ingredient popup
    driver.find_element(By.XPATH, value="//img[@title='Add Ingredient']").click()

    #search and wait for results to load
    search = driver.find_element(By.XPATH, value='//div[@class="popupContent"]//div/img/following-sibling::input')
    search.send_keys(ingredient)
    spinner_xpath_expr = '//div[@class="popupContent"]//img[@src="img/spin2.gif"]'
    driver.find_element(By.XPATH, value='//div[@class="popupContent"]//button[text()="Search"]').click()
    WebDriverWait(driver, timeout=10).until(EC.invisibility_of_element_located((By.XPATH, spinner_xpath_expr)))

    #click on first result
    first_result= driver.find_element(By.XPATH, value='//div[@class="popupContent"]//tr[@class="prettyTable-header"]/following-sibling::tr[1]/td[1]/div[@class="gwt-Label"]')
    first_result.click()

    #wait for amount and unit input to appear
    unit_el_xpath_expr = '//div[text()="Serving:"]/following-sibling::div//div[@class="select-pretty"]/select[@class="gwt-ListBox"]'
    WebDriverWait(driver, timeout=10).until( EC.presence_of_element_located( (By.XPATH, unit_el_xpath_expr) ) )
    unit_el = driver.find_element(By.XPATH, value=unit_el_xpath_expr)
    WebDriverWait(driver, timeout=10).until( EC.element_to_be_clickable(unit_el) )
    unit_select_object = Select(unit_el)
    options = unit_select_object.options

    amount, element_text = match_unit(options, amount,  unit)
    unit_select_object.select_by_visible_text(element_text)
    amount_el = driver.find_element(By.XPATH, value='//div[text()="Serving:"]/following-sibling::div//div[@class="select-pretty"]/input[@class="input-enabled"]')
    amount_el.clear()
    amount_el.send_keys(amount)
    print(f'Added {amount} * "{element_text}" of {ingredient}')

    add_button = driver.find_element(By.XPATH, value='//div[text()="Serving:"]/following-sibling::div//div[@class="select-pretty"]//button[text()="Add"]')
    add_button.click()

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
add_ingredient(300, "TL", "Pfefferminz") # For testing, TODO: integrate into adding ingredients loop
