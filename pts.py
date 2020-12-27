import os
import sys
import selenium
from selenium import webdriver
from datetime import datetime
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from multiprocessing import Process
import threading
import signal
from functools import partial
from time import sleep as sleep
import unicodedata
import sqlite3
import requests
import time

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


connection = sqlite3.connect("pts.db")
db = connection.cursor()
try:
    db.execute("CREATE TABLE days (day INTEGER, month INTEGER, day_type TEXT, in_time TEXT, out_time TEXT, off INTEGER)")
except:
    print ('flushing tables')
    db.execute("DROP TABLE days")
    db.execute("CREATE TABLE days (day INTEGER, month INTEGER, day_type TEXT, in_time TEXT, out_time TEXT, off INTEGER)")


print("=============================================================\n================== PTS Sucks. Python rules! =================\n=============================================================\n================== PTS Automation by Amin Sharifi ===========\n=============================================================")
print("=============================================================\n================== PTS CLI ================\n=============================================================")


#========================== user inputs =========================
def user_inputs_main():
    print(f"Select the work period that you want to analyze:\n")
    print("[1] - Submit Time\n[2] - Check Submitted Times")
    while (1):
        res = input() 
    
        if res=="":
            print("Please only insert a number from 1 to 2")
            print (f"Try Again:")
            continue
            
        try:    
            res = int(res)
        except:
            print("Please only insert a number from 1 to 10")
            print (f"Try Again:")
            continue
            

        if res > 2:
            print("Please only insert a number from 1 to 10")
            print (f"Try Again:")
            continue
        else:
            return(res)

    return(0)
def user_inputs():
    print(f"Select the work period that you want to analyze:\n")
    print("[1] - Esfand/Farvardin\n[2] - Farvardin/Ordibehesht\n[3] - Ordibehesht/Khordad\n[4] - Khordad/Tir\n[5] - Tir/Mordad\n[6] - Mordad/Shahrivar\n[7] - Shahrivar/Mehr\n[8] - Mehr/Aban\n[9] - Aban/Azar\n[10] - Azar/Dey\n[11] - Dey/Bahman\n[12] - Bahman/Esfand")
    while (1):
        period = input() 
    
        if period=="":
            print("Please only insert a number from 1 to 10")
            print (f"Try Again:")
            continue
            
        try:    
            period = int(period)
        except:
            print("Please only insert a number from 1 to 10")
            print (f"Try Again:")
            continue
            

        if period > 12:
            print("Please only insert a number from 1 to 10")
            print (f"Try Again:")
            continue
        else:


            period = [period - 1, period]   

            return(period)

    return(0)



#========================== action functions =================================
def init():
    #print ('Please wait...')
    options = Options()
    options.headless = False
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    return(driver)

def site_login(driver, username, password):
    loop = True
    while loop:
        print("logging into PTS...")
        driver.get ("http://192.168.84.109/Webkart/eosLogin.aspx")
        driver.find_element_by_id("txtUserName").send_keys(username)
        driver.find_element_by_id ("txtPassword").send_keys(password)
        driver.find_element_by_id("btnSubmit").click()
        try:
            login_res = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_class_name("rpText"))
            driver.find_element_by_class_name("rpText")
            state = "logged_in"
            print('logged in successfuly!')
            loop = False
        except:
            
            print('Cant login!')
            driver.delete_all_cookies()

def is_off(date):
    url = f'https://pholiday.herokuapp.com/date/{date}'
    r = requests.get(url)
    data = r.json()
    if data['isHoliday'] == True:
        return (1)
    else:
        return (0)

    
def create_time_table(period):
    print("Creating the time table...")
    print('Progress: 0%\r', end='\r')
    from_day = 15
    to_day = 32
    in_time = '0'
    out_time ='0'
    day_off = 0
    months = period
    prog = 0
    year = int(JalaliDateTime.now().strftime('%Y'))

    for month in months:
        if month == 0:
            year = year - 1
        while from_day <= to_day:
            try:
                day = JalaliDate(year, month, from_day)
                day_type = day.strftime('%A')
                day_month = day.strftime("%m")
                day_date = day.strftime('%d')
                prog = prog + 1
                from_day = from_day + 1
                print (f"\rProgress: {round(100*(prog/31))}%", end='\r')
                if day_type != "Panjshanbeh" and day_type != "Jomeh":
                    date = day.strftime('%Y-%m-%d')
                    
                    day_off = is_off(date)
                else:
                    day_off = 1

                db.execute("INSERT INTO days VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(day_date, day_month, day_type,in_time , out_time, day_off))
            except:
                from_day = 1
                to_day = 15
                break
    print (f"Time table created........")            
    connection.commit()    



   
def wait_for_ajax(driver):
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        print (f'ERROR in wait_for_ajax() > {e}')
        pass 




def conv(unicode_arabic_date):
    new_date = ''
    for d in unicode_arabic_date:
        if d != ':' and d !='/':
            new_date+=str(unicodedata.decimal(d))
        elif d == ':':
            new_date+=':'
        elif d =='/':
            new_date+='/'
    return new_date

def get_time(driver, period):
    f_d = str(period[0]).zfill(2)
    t_d = str(period[1]).zfill(2)
    
    from_date = f'1399{f_d}15'
    to_date = f'1399{t_d}15'



    print("Getting PTS data please wait...")
    print('Progress: 0%\r', end='\r')
    driver.get("http://192.168.84.109/Webkart/eosWinkartWeb/ioList.aspx")
    x = WebDriverWait(driver, 15).until(lambda x: x.find_element_by_id('ctl00_ContentPlaceHolder1_imgKarkarddetail'))
    sleep(0.5)
    try:
        from_element  = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtbeginDate")
    except:
        print("Need to login again")
        site_login(driver=driver,username=username,password=password)

    # 1
    from_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtbeginDate")
    from_element.send_keys(Keys.CONTROL, 'a')
    sleep(0.5)
    from_element.send_keys(from_date)
    driver.find_element_by_id("ctl00_Image2").click()
    # 2
    to_element  = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtEndDate")
    to_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtEndDate")
    to_element.send_keys(Keys.CONTROL, 'a')
    sleep(0.5)
    to_element.send_keys(to_date)
    driver.find_element_by_id("ctl00_Image2").click()
    # 3

    select = Select(driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlSerachKind'))
    select.select_by_value('5')

    # 4 
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearchRequest").click()
    wait_for_ajax(driver)
    #WebDriverWait(driver, 7).until(lambda x: x.find_element_by_id("ctl00_ContentPlaceHolder1_lblError").text != "")
    
    # 5
    try:
        x = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id('ctl00_ContentPlaceHolder1_grdIOrequest_ctl00_ctl03_ctl01_PageSizeComboBox_Input')) 
        total_res = driver.find_element_by_id("ctl00_ContentPlaceHolder1_grdIOrequest_ctl00_ctl03_ctl01_PageSizeComboBox_Input").click()
        x = WebDriverWait(driver, 3).until(lambda x: x.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00_ctl03_ctl01_PageSizeComboBox_DropDown"]/div/ul/li[3]'))
        sleep(2)
        num = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00_ctl03_ctl01_PageSizeComboBox_DropDown"]/div/ul/li[3]')
        #num.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        num.click()
        table = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00"]/tbody')
        x = len(table.find_elements_by_tag_name("tr"))
        # wait for table to load
        while 1:
            sleep(0.5)
            table = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00"]/tbody')
            y = len(table.find_elements_by_tag_name("tr"))
            if y > x:
                break
    except:
        print('WARNING: There are less than 20 results')


    # 6 extract table

    row = 0
    
    table = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00"]/tbody')
    total_rows = len(table.find_elements_by_tag_name("tr")) - 1
    if total_rows == 0:
        print("No data was found")
        return (0)
    while row <= total_rows:
        print (f"\rProgress: {round(100*(row/total_rows))}%", end='\r')
        time_path = f'//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00__{row}"]/td[10]'
        date_path = f'//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00__{row}"]/td[11]'
        type_path = f'//*[@id="ctl00_ContentPlaceHolder1_grdIOrequest_ctl00__{row}"]/td[9]'

        time = driver.find_element_by_xpath(time_path)
        time = time.text
        time = conv(time)
        
        date = driver.find_element_by_xpath(date_path)
        date = date.text
        date = conv(date)
        date = date.split('/')
        date_day = date[2]
        date_month = date[1]
        type = driver.find_element_by_xpath(type_path)
        if type.text == "ورود":
            type = 'in_time'
        elif type.text == "خروج":
            type = 'out_time'
        else:
            print ("ERROR: Cant find type element")



        #print (f'{time} - {date} - {type}')
        #sleep(0.5)
        db.execute(f'UPDATE days SET {type} = ? WHERE day = ? AND month = ?', (time, date_day, date_month))
        connection.commit() 

        row = row + 1
    


def check_time():
    today = JalaliDateTime.now().strftime('%m-%d')
    today = time.strptime(today, '%m-%d')
    a = '0'
    b = '0'
    c = 0
    missings = db.execute('SELECT day, month FROM days WHERE in_time = ? AND off = ?', (a, c)).fetchall()
    print ("you have missing time entris in these days:")
    for missing in missings:
        m_d = str(missing[0]).zfill(2)
        m_m = str(missing[1]).zfill(2)
        day = f'{m_m}-{m_d}'

        day = time.strptime(day, '%m-%d')

        if today < day:
            break
        else:
            print (f'{m_m}-{m_d}  Has no ENTER time')
        
    missings = db.execute('SELECT day, month FROM days WHERE out_time = ? AND off = ?', (b, c)).fetchall()
    print ("-------------------------------")
    for missing in missings:
        m_d = str(missing[0]).zfill(2)
        m_m = str(missing[1]).zfill(2)
        day = f'{m_m}-{m_d}'
        day = time.strptime(day, '%m-%d')

        if today < day:
            break
        else:
            print (f'{m_m}-{m_d}  Has no EXIT time')
def submit_missings(driver):
    try:
        db.execute("CREATE TABLE missings (date TEXT, type TEXT, time TEXT)")
    except:
        print ('flushing tables')
        db.execute("DROP TABLE missings")
        db.execute("CREATE TABLE missings (date TEXT, type TEXT, time TEXT)")

    today = JalaliDateTime.now().strftime('%m-%d')
    today = time.strptime(today, '%m-%d')
    year = JalaliDateTime.now().strftime('%Y')
    a = '0'
    b = '0'
    c = 0
    missings = db.execute('SELECT day, month FROM days WHERE in_time = ? AND off = ?', (a, c)).fetchall()
    
    for missing in missings:
        
        m_d = str(missing[0]).zfill(2)
        m_m = str(missing[1]).zfill(2)
        day_s = f'{m_m}-{m_d}'
        day = time.strptime(day_s, '%m-%d')
        if today < day:
            break
        else:
            pass        
        
        print (f"input ENTER time for {day_s}:")
        user_time = input()
        type = 'enter'
        date = f'{year}{m_m}{m_d}'
        db.execute("INSERT INTO missings VALUES ('{}', '{}', '{}')".format(date, type, user_time))

                   
        connection.commit() 

        
    missings = db.execute('SELECT day, month FROM days WHERE out_time = ? AND off = ?', (b, c)).fetchall()
    print ("-------------------------------")
    for missing in missings:
        m_d = str(missing[0]).zfill(2)
        m_m = str(missing[1]).zfill(2)
        day_s = f'{m_m}-{m_d}'
        day = time.strptime(day_s, '%m-%d')
        if today < day:
            break
        else:
            pass        
        
        print (f"input EXIT time for {day_s}:")
        user_time = input()
        type = 'exit'
        date = f'{year}{m_m}{m_d}'
        db.execute("INSERT INTO missings VALUES ('{}', '{}', '{}')".format(date, type, user_time))

                   
        connection.commit()



    missings = db.execute('SELECT date, type, time FROM missings').fetchall()
    for missing in missings:
        submit_time(driver=driver, date=missing[0],time=missing[2],type=missing[1])

def user_inputs_2 ():
    while 1: # user input loop
        print("Select an option:")
        print('[1] - Submit missing times\n[2] - Check again\n[3] - Submit custom time\n[4] - Exit ')
        input_5 = input()
        try:
            ui = int(input_5)
        except:
            print("Please only insert a number from 1 to 3")
            print (f"Try Again:")
            continue

        if ui == 1:
            return ("submit")
        if ui == 2:
            return ("recheck")
        if ui == 3:
            return ("submit_custom")
        elif ui == 4:
            return ('exit')

def user_inputs_submit():
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

#========================== main loops ========================================
def main_1():
    end = False
    while end == False:
        [time ,type,date] = user_inputs_submit()
        submit_time(driver=driver,date=date,time=time,type=type)
        print ("Do you want to submit another request? (No: Enter / Yes: Y)")
        input3 = input() 
        if input3 == "":
            end = True
            return ('done')
        else:
            end = False
            
def main_2(driver):
    period = user_inputs()
    create_time_table(period)
    loop_1 = True
    while loop_1:
        get_time(driver,period)
        check_time()
        loop_2 = True
        while loop_2:
            res = user_inputs_2()
            if res == "exit":
                driver.close()
                exit()
            elif res == 'recheck':
                loop_2 = False
            elif res == 'submit':
                submit_missings(driver)
            elif res == 'submit_custom':
                end = False
                while end == False:
                    [time ,type,date] = user_inputs_submit()
                    submit_time(driver=driver,date=date,time=time,type=type)
                    print ("Do you want to submit another request? (No: Enter / Yes: Y (Or any other input))")
                    input3 = input() 
                    if input3 == "":
                        end = True
                    else:
                        end = False
                        
#========================== actions ==========================================
res = user_inputs_main()
driver = init()
site_login(driver=driver, username=username, password=password)
loop = True
while loop:
    if res == 1:
        x = main_1()
        if x == 'done':
            res = user_inputs_main()

    elif res == 2:
        main_2(driver=driver)
        user_inputs_2()





#driver.close()
#done dont show results for days after today
#done todo ask for recheck
#done todo fix sleep and use webdrivewait instead
#done todo ask user to get missing times and submit
#todo integrate submit and check scripts
#todo fix the bug with the periods 1 when the year changes

