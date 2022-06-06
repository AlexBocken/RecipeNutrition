#!/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import subprocess

def get_login_credentials():
    user = os.getlogin()
    email_login = password_login = ''
    if ( user == 'alex' ):
        email_login = 'alexander@bocken.org'
        out = subprocess.check_output(['pass', 'show', 'Fitness/cronometer'])
        password_login = out.decode("utf-8").partition('\n')[0] # only read first line of pass file
    elif ( user == 'till'):
        email_login = '<email>' #TODO
        out = subprocess.check_output(['pass', 'show', 'Fitness/cronometer'])
        password_login = out.decode("utf-8")
    else:
        email_login = os.environ['RN_EMAIL']
        password_login = os.environ['RN_PW']

    assert email_login, "could not find email for this user. Implement method first or use env vars"
    assert password_login, "could not find password for this user. Implement method first or use env vars"

    return email_login, password_login

def login_to_cronometer(email_login, password_login):
    driver.get("https://cronometer.com")
    login_link = driver.find_element(by=By.CSS_SELECTOR, value="a.link__hero-login")
    login_link.click()
    email_input = driver.find_element(by=By.CSS_SELECTOR, value="input#usernameBox.textbox--1.login-fields")
    password_input = driver.find_element(by=By.CSS_SELECTOR, value="input#password.textbox--1.login-fields")
    email_input.send_keys(email_login)
    password_input.send_keys(password_login)
    button = driver.find_element(by=By.CSS_SELECTOR, value="button#login-button.submit--1.login-fields")
    button.click()

email_login, password_login = get_login_credentials()
driver = webdriver.Chrome()
login_to_cronometer(email_login, password_login)

foods_link = driver.find_element(by=By.LINK_TEXT, value="Foods")
foods_link.click()
add_recipe = driver.find_element(by=By.NAME, value="+ Add Recipe")
#print(test)
