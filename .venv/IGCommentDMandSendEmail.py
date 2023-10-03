from requests import get
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from configparser import ConfigParser
import win32clipboard
import pandas as pd
import pickle

def CopyToClipboard(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(u''.join(text), win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

def check_cookies(driver):
    #login to instagram and save cookies
    driver.get('http://instagram.com/')
    try:
        cookies = pickle.load(open("cookies_ig.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get('http://instagram.com/')
    except:
        pass
    k = input("\nPress enter if you already logged in to IG...")
    pickle.dump(driver.get_cookies() , open("cookies_ig.pkl","wb"))

    #login to gmail and save cookies
    driver.get('https://mail.google.com/mail/u/0/#inbox')
    # try:
    #     cookies = pickle.load(open("cookies_gmail.pkl", "rb"))
    #     for cookie in cookies:
    #         driver.add_cookie(cookie)
    #     driver.get('https://mail.google.com/mail/u/0/#inbox')
    # except:
    #     pass
    k = input("\nPress enter if you already logged in to GMAIL...")
    pickle.dump(driver.get_cookies() , open("cookies_gmail.pkl","wb"))

def IGCommentDM(driver, username, ig_comment, ig_dm):
    try:
        driver.get('http://instagram.com/' + username)
        sleep(7)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[role="link"][href*="/p/"]'))).click()
        sleep(3)

        try:
            CopyToClipboard(ig_comment)
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Add a comment']"))))
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Add a comment']"))).send_keys(Keys.CONTROL, 'v')
            except:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Add a comment']"))).send_keys(Keys.CONTROL, 'v')
            sleep(3)
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Post')][@role='button']"))))
            sleep(10)
        except:
            return 'FAILED SEND IG COMMENT'
            
        
        try:
            driver.get('http://instagram.com/' + username)
            sleep(7)
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Message')][@role='button']"))))
            sleep(10)

            CopyToClipboard(ig_dm)
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))))
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))).send_keys(Keys.CONTROL, 'v')
            except:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))).send_keys(Keys.CONTROL, 'v')
            sleep(3)        
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Send')]"))))
            sleep(10)
        except:
            return 'FAILED SEND IG DM'

        return 'SUCCESS PROCESS IG'

    except Exception as e:
        return 'ERROR ON IG PART '

def sendMail(driver, mailto, mail_title, mail_body):
    try:
        driver.get('https://mail.google.com/mail')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body"))).send_keys(Keys.CONTROL, Keys.F5)
        driver.get('https://mail.google.com/mail/u/0/#inbox?compose=new')
        sleep(7)

        CopyToClipboard(mailto)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-autocomplete='list'][aria-haspopup='listbox'][role='combobox']"))).send_keys(Keys.CONTROL, 'v')
        CopyToClipboard(mail_title)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='subjectbox']"))).send_keys(Keys.CONTROL, 'v')
        CopyToClipboard(mail_body)
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Message Body']"))))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Message Body']"))).send_keys(Keys.CONTROL, 'v')
        sleep(3)

        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Send')][@role='button']"))))

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Message sent')]")))
            sleep(10)
            return 'SUCCESS SEND MAIL'
        except:
            return 'FAILED SEND MAIL'        
    
    except Exception as e:
        return 'ERROR ON MAIL PART '

def main():
    config_object = ConfigParser()
    try:
        config_object.read("config.ini")
        system_cof = config_object["SYSTEM"]
        datasource = system_cof["datasource"]
        start_line = int(system_cof["start_line"])
        end_line = int(system_cof["end_line"])
        delay_sec = int(system_cof["delay_sec"])     

        df = pd.read_csv(datasource, header=0, on_bad_lines='skip')

        message_conf = config_object["MESSAGE"]
        ig_comment = message_conf["ig_comment"]
        ig_dm = message_conf["ig_dm"]
        mail_title = message_conf["mail_title"]
        mail_body = message_conf["mail_body"]

    except Exception as e:
        print('ERROR. NO CONFIG FILE ' + str(e))
        return ''        

    #open browser
    driver = undetected_chromedriver.Chrome()
    check_cookies(driver)    

    for index in range(start_line, end_line):
        print('PROCESSING LINE : ' + str(index))
        if pd.isna(df['Username'][index]) or df['Username'][index] == '':
            print('IG USERNAME IS EMPTY')
            pass
        else:
            print(IGCommentDM(driver, df['Username'][index], ig_comment, ig_dm))

        if pd.isna(df['Email'][index]) or df['Email'][index] == '':
            print('EMAIL IS EMPTY')
            pass
        else:
            print(sendMail(driver, df['Email'][index], mail_title, mail_body))
        
        print("WAITING " + str(delay_sec) + " TO CONTINUE TO NEXT ROW")
        sleep(delay_sec)
    
    driver.quit()

if __name__ == '__main__':
    main()
    k = input("\nPress enter to exit...")