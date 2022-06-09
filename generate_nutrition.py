#!/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import * # pyright: ignore
from time import sleep
import re
import os
import subprocess
from datetime import date


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
    email_input = driver.find_element(By.CSS_SELECTOR, value="input#usernameBox.textbox--1.login-fields")
    password_input = driver.find_element(By.CSS_SELECTOR, value="input#password.textbox--1.login-fields")
    email_input.send_keys(email_login)
    password_input.send_keys(password_login)
    button = driver.find_element(by=By.CSS_SELECTOR, value="button#login-button.submit--1.login-fields")
    button.click()
    WebDriverWait(driver, timeout=10).until(lambda d: d.title != "Cronometer Login")

def adjust_amount_by_multiplier(amount, unit, select_text):
    '''
    returns adjusted amount for given option. Can detect fractionals
    (e.g. adjust_amount_by_multiplier(3, 'tbsp', '1/4 tbsp - 0.5 g') returns 12
    amount: amount of initial unit (e.g. 300 for 300 mL)
    unit: base unit to match on cronometer.com such as "tbsp". NOT unit used in recipe
    select_text: whole option displayed such as "1/4 tbsp - 0.5 g"
    '''
    amount_unit = re.sub(f'[^0-9]*([0-9]+/)?([0-9]+)?\\s?{unit}.*', '\\1\\2', select_text)
    mul = re.sub(f'(.*){unit}', '\\1', amount_unit)
    if not mul:
        mul = '1'
    if '/' in mul:
        n = float( re.sub('([0-9])*/[0-9]*', '\\1', mul) )
        d = float( re.sub('([0-9])*/[0-9]*', '\\2', mul) )
        mul = n / d
    else:
        mul = float(mul)
    if(mul):
        amount /= mul
    return amount

def match_unit(select_list, amount, unit):
    '''matches personal unit convention from recipe with cronometer options
    if necessary, amount get's adjusted to compensate for multipliers found in cronometer unit
    '''
    if unit == 'g':
        for el in select_list:
            if el.text == 'g':
                return amount, el.text
    elif( re.search('m(l|L)', unit) ):
        for el in select_list:
            if 'mL' in el.text:
                amount = adjust_amount_by_multiplier(amount, 'mL', el.text)
                return amount, el.text
        for el in select_list:
            if( re.search('cup (-|—)', el.text) ):
                one_cup_ml = 236.5882365
                amount /= one_cup_ml
                #TODO: probably is "half" or "quarter" cup, not "0.5", "0.25" cups
                #TODO: maybe like tbsp '1/4', '1/2'?
                amount = adjust_amount_by_multiplier(amount, 'cup', el.text)
                return amount, el.text
    elif( re.search( '(medium(-sized)?|mittel(gro(ss|ß))?)', unit) ):
            for el in select_list:
                if( re.search('medium (-|—)', el.text) ):
                    return amount, el.text
    elif( re.search( '(very small|sehr klein)', unit) ):
            for el in select_list:
                if( re.search('very small (-|—)', el.text) ):
                    return amount, el.text
    elif( re.search( '(small|klein)', unit) ):
            for el in select_list:
                if( re.search('small (-|—)', el.text) ):
                    return amount, el.text
    elif( re.search( '(large(-sized)?|gro(ss|ß))', unit) ):
            for el in select_list:
                if( re.search('large (-|—)', el.text) ):
                    return amount, el.text
    elif( re.search( '(EL|tbsp)', unit) ):
        for el in select_list:
            if( re.search('tbsp (-|—)', el.text) ):
                amount = adjust_amount_by_multiplier(amount, 'tbsp', el.text)
                return amount, el.text
    elif( re.search( '(TL|tsp)', unit) ):
        for el in select_list:
            if( re.search('tsp (-|—)', el.text) ):
                amount = adjust_amount_by_multiplier(amount, 'tsp', el.text)
                return amount, el.text
    elif (re.search('c(l|L)', unit)):
        return match_unit(select_list, 10*amount, 'mL')
    elif (re.search('d(l|L)', unit)):
        return match_unit(select_list, 100*amount, 'mL')
    # needs to be last non-generic match as it is quite generic to just look for 'l'
    elif (re.search('(l|L)', unit)):
        return match_unit(select_list, 1000*amount, 'mL')
    # generic catcher
    for el in select_list:
        if el.text == unit:
            amount = adjust_amount_by_multiplier(amount, unit, el.text)
            return amount, el.text
    print("Found no matching unit, please select proper unit and amount manually")
    return None, None

def add_ingredient(amount, unit, ingredient):
    '''Assumes that it starts on recipe page and adds one ingredient
    to the recipe
    amount: int/float with amount in later specified unit
    unit: unit of amount (e.g. "g" for grams)
    ingredient: string with name for ingredient
    '''
    print(f'Trying to add {amount} {unit} of {ingredient}')

    try:
        #go to ingredient popup
        driver.find_element(By.XPATH, value="//img[@title='Add Ingredient']").click()
    except ElementClickInterceptedException:
        remove_cookie_banner()
        driver.find_element(By.XPATH, value="//img[@title='Add Ingredient']").click()

    #search and wait for results to load
    search = driver.find_element(By.XPATH, value='//div[@class="popupContent"]//div/img/following-sibling::input')
    search.send_keys(ingredient)
    spinner_xpath_expr = '//div[@class="popupContent"]//img[@src="img/spin2.gif"]'
    driver.find_element(By.XPATH, value='//div[@class="popupContent"]//button[text()="Search"]').click()
    try:
       WebDriverWait(driver, timeout=2).until(EC.visibility_of_element_located((By.XPATH, spinner_xpath_expr)))
       WebDriverWait(driver, timeout=2).until(EC.invisibility_of_element_located((By.XPATH, spinner_xpath_expr)))
    except (NoSuchElementException, TimeoutException) as e:
        sleep(2) #could be cleaner, let's be real, doesn't have to be
        pass
    #click on first result
    first_result = driver.find_element(By.XPATH, value='//div[@class="popupContent"]//tr[@class="prettyTable-header"]/following-sibling::tr[1]/td[1]/div[@class="gwt-Label"]')
    first_result.click()
    found_ingredient_name = first_result.text
    #wait for amount and unit input to appear
    unit_el_xpath_expr = '//div[text()="Serving:"]/following-sibling::div//div[@class="select-pretty"]/select[@class="gwt-ListBox"]'
    WebDriverWait(driver, timeout=10).until( EC.presence_of_element_located( (By.XPATH, unit_el_xpath_expr) ) )
    unit_el = driver.find_element(By.XPATH, value=unit_el_xpath_expr)
    WebDriverWait(driver, timeout=10).until( EC.element_to_be_clickable(unit_el) )
    unit_select_object = Select(unit_el)
    options = unit_select_object.options

    amount, element_text = match_unit(options, amount,  unit)
    amount_el = driver.find_element(By.XPATH, value='//div[text()="Serving:"]/following-sibling::div//div[@class="select-pretty"]/input[@class="input-enabled"]')
    add_button = driver.find_element(By.XPATH, value='//div[text()="Serving:"]/following-sibling::div//div[@class="select-pretty"]//button[text()="Add"]')
    if(amount is None):
        print("Please press enter in this window when manual entry is done.", end='')
        input()
        unit = unit_select_object.first_selected_option.text
        amount = amount_el.get_attribute("value")
        try:
            add_button.click()
            print(f'Added {amount} * "{unit}" of "{found_ingredient_name}"')
        except ElementClickInterceptedException:
            remove_cookie_banner()
            add_ingredient(amount, unit, ingredient)
        except StaleElementReferenceException:
            pass
        return
    else:
        unit_select_object.select_by_visible_text(element_text)
        amount_el.clear()
        amount_el.send_keys(amount)

    try:
        add_button.click()
        print(f'Added {amount} * "{element_text}" of "{found_ingredient_name}"')
    except ElementClickInterceptedException:
        remove_cookie_banner()
        add_ingredient(amount, unit, ingredient)

def remove_cookie_banner():
    print("Removing cookie banner...")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//button[@class="ncmp__btn"]'))).click()

def add_recipe(name, servings, ingredients):
    '''Main loop for a single recipe. Adding name, servings, ingredients and export after it's done
       name: string of recipe name
       servings: int amount of servings in recipe
       ingredients: list of three-tuple (amount, unit, ingredient)
    '''
    add_recipe = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.XPATH, value="//button[text()='+ Add Recipe']"))
    add_recipe.click()
    change_meta_data(titel)
    try:
        change_servings(servings)
    except ElementClickInterceptedException:
        remove_cookie_banner()
        change_servings(servings)
    for amount, unit, ingredient in ingredients:
        add_ingredient(amount, unit, ingredient)
    save_name = name.replace(" ", "_").lower()
    save_export_recipe(save_name)


def change_meta_data(recipe_name):
    today = date.today()
    name_box = driver.find_element(By.XPATH, '//input[@title="New Recipe"]')
    name_box.click()
    name_box.clear()
    name_box.send_keys(recipe_name)
    notes_box = driver.find_element(By.XPATH,'//textarea[@class="gwt-TextArea"]')
    notes_box.click()
    notes_box.send_keys(f"Added on {today.strftime('%d.%m.%Y')}")

def change_servings(servings):
    servings_image = driver.find_element(By.XPATH, value="//img[@title='Add Measure']")
    servings_image.click()
    servings_field = driver.find_element(By.XPATH, value='//div[text()="Servings Per Recipe"]/parent::td/parent::tr/parent::tbody/tr[2]/td[3]')
    servings_field.click()
    servings_field = driver.find_element(By.XPATH, value='//div[text()="Servings Per Recipe"]/parent::td/parent::tr/parent::tbody/tr[2]/td[3]/input')
    servings_field.send_keys(servings)

def save_export_recipe(save_name):
    save_button = driver.find_element(By.XPATH, value="//button[text()='Save Changes']")
    save_button.click()
    sleep(1) # Wait for website to save the file
    menu_button = driver.find_element(By.XPATH, value="//div[@class='GO-RHEKCA3']/img")
    menu_button.click()
    export_div = driver.find_element(By.XPATH, value="//div[contains(@class, 'gwt-Label') and text()='Export to CSV File...']")
    export_div.click()
    sleep(2) # wait for file to be downloaded TODO: cleanup
    os.system(f"mv {save_location}/food.csv {save_location}/{save_name}.csv") # move file to be named after recipe



if(__name__ == "__main__"):
    email_login, password_login = get_login_credentials()

    # INPUT FROM PARSER
    global save_location #TODO: should be cleaner if possible
    save_location = "/tmp/nutrition"
    titel="Name des Rezeptes"
    servings = 5

    chrome_options = Options()
    chrome_options.add_argument('--force-device-scale-factor=1.5')
    prefs = {"download.default_directory": save_location,"download.prompt_for_download": False, "download.directory_upgrade": True }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(options=chrome_options)
    login_to_cronometer(email_login, password_login)

    driver.get("https://cronometer.com/#foods")
    add_recipe(titel, servings, [ (2, 'cl', 'Olivenöl'), (2, "mittelgroß", "Apfel"), (3, "TL", "Pfefferminz"), (10, "ml", "Milch"), (200, "ml", "Wasser") ])
