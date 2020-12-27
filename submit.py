import os
import sys
import selenium
from selenium import webdriver
from datetime import datetime
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait  
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process
import threading
import signal
from functools import partial


#======================= change log ============================
# version 1.0 
#======================= configs ================================


fileName='conf.txt'
with open(os.path.join(sys.path[0], fileName), 'r') as f:
    data = f.read().splitlines()
try:
    username = data[0]
    password = data[1]
except:
    print("Please put your username and password in the conf.txt file.\nUsername must be in the first line and the password must be in the second line.\nExiting now...")
    exit()
time_now = JalaliDateTime.now().strftime('%H:%M')
date_now = JalaliDateTime.now().strftime('%Y/%m/%d')
print("=============================================================\n================== PTS Sucks. Python rules! =================\n=============================================================\n================== PTS Automation by Amin Sharifi ===========\n=============================================================\n\n\n")

print("Please wait...\n\n")
#========================== user inputs =========================
def user_inputs():
    print(f"type the date (example: 990922) or press enter to set date to now ({date_now}):")
    input0 = input() 
   
    if input0=="":
        
        date = date_now.replace("/","")
        print (f"setting date as {date_now}")
    else:
        input0.replace("/","")
        date = date = "13" + input0
        print (f"setting date as {date}")
    print(f"type the time (example: 0815) or press enter to set time to now ({time_now}):")
    input1 = input() 
    
    if input1=="":
        
        time = time_now.replace(":","")
        print (f"setting time as {time}")
    else:
        input1.replace(" ","")
        time = input1
        print (f"setting time as {time}")

    print ("For enter prees I and for exit press O")
    input2 = input()
    if input2 =="i" or input2 =="ه":
        type = "enter"
    elif input2 == 'o' or input2 == 'خ':
        type = "exit"
    else:
        print("Error: Wrong input!")

    if ( len(time) != 4):
        print ('inputs are incorrect. time should be 4 digits like 0914. the second input accepts only i or o')
        return("error")
    return(time,type,date)



#========================== action functions =================================
def init():
    #print ('Please wait...')
    options = Options()
    options.headless = True
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    return(driver)

def site_login(driver, username, password):
    print("logging in...")
    driver.get ("http://192.168.84.109/Webkart/eosLogin.aspx")
    driver.find_element_by_id("txtUserName").send_keys(username)
    driver.find_element_by_id ("txtPassword").send_keys(password)
    driver.find_element_by_id("btnSubmit").click()
    try:
        login_res = WebDriverWait(driver, 2).until(lambda x: x.find_element_by_class_name("rpText"))
        driver.find_element_by_class_name("rpText")
        state = "logged_in"
        print('logged in successfuly!')
    except:
        print('wrong user/pass')
        #driver.delete_all_cookies()

    
    



def submit_time(driver,date,time,type):
    print("Submiting request...")
    driver.get("http://192.168.84.109/Webkart/eosWinkartWeb/addIoInfo.aspx")
    try:
        date_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtbeginDate")
    except:
        print("Need to login again")
        site_login(driver=driver,username=username,password=password)

    date_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtbeginDate")
    date_element.send_keys(date)
    driver.find_element_by_id("ctl00_Image2").click()



    time_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtBeginTime")

    time_element.click()
    time_element.send_keys(Keys.ARROW_LEFT, Keys.ARROW_LEFT,Keys.ARROW_LEFT,Keys.ARROW_LEFT,Keys.ARROW_LEFT)
    time_element.send_keys(time)



    if type == "enter":
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_rdbIO_0").click()
    elif type == "exit":
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_rdbIO_1").click()
    else:
        print ("error")

    driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSubmit").click()
    
    #reading the result

    res = WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("ctl00_ContentPlaceHolder1_lblError").text != "") 
    res = driver.find_element_by_id("ctl00_ContentPlaceHolder1_lblError")
    #print (res.text)
    if res.text == "درخواست مورد نظر با موفقیت ثبت شد":
        print("Time submited successfuly")
        return('OK')
    else:
        print("Error: This request has been submited before")
        return("ERROR")

#========================== actions ==========================================
def signal_handler(driver, signal, frame):
    print('You pressed Ctrl+C!')
    
    driver.quit()
    driver.stop_client()
    sys.exit(0)





end = False

driver = init()
signal.signal(signal.SIGINT, partial(signal_handler, driver))
while end == False:
    [time ,type,date] = user_inputs()
    site_login(driver=driver, username=username, password=password)
    submit_time(driver=driver,date=date,time=time,type=type)
    print ("Do you want to submit another request? (No: Enter / Yes: Y)")
    input3 = input() 
    if input3 == "":
        end = True
    else:
        end = False
driver.close()
exit()
sys.exit(0)