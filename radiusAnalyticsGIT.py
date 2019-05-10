# -*- coding: utf-8 -*-
"""
Created on Thu May 10 2:14 PM 2019
@author: Hugo
"""
#Imports
import time
import os
from itertools import islice
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import date, datetime
import datetime
from pathlib import Path
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


#Variables
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
chromedriver = desktop + '/chromedriver'
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('log-level=3')
url = 'https://www.marijuanadoctors.com/user/login'
url2 = 'https://www.marijuanadoctors.com/user/admin/user/practice/index'
ana = 'https://www.marijuanadoctors.com/user/practice/analytics'
logout = 'https://www.marijuanadoctors.com/user/logout'
doctors = 'https://www.marijuanadoctors.com/medical-marijuana-doctors/'


print('\n\nFind analytics for a given radius from a zipcode\n')
print('__radiusAnalytics 1.0__\n\n')
def chunk(it, size):
    """
    Chunk list to N chunks
    """
    it = iter(it)
    return iter(lambda: list(islice(it, size)), [])

def mainFunction():
    """
    The purpose of this new application is to find the perfect location for your new clients.
    The program will ask you 4 things.

    1) Enter a Zip Code
    2) Enter a Radius
    3) Analytics for past (For example if you enter 22 it will get analytics for the past 22 days)
    4) Email

    The program will find all the listings that fell within your radius, it will then get the analytics for each one of the listings.

    Once it has all the data the program will show you the results and also email you the results to the given email.
    """
    #initialize chrome driver
    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    #user input variables
    userZip = input('Enter a Zip Code >>>>>>>>>>>>>>>>>>>>>>> ')
    userRadius = input('\nEnter a radius   >>>>>>>>>>>>>>>>>>>>>>> ')
    days = input('\nAnalytics for the past >>>>>>>>>>>>>>>>> ')
    email = input('Enter email >>>>>>>>>> ')
    #error handler to not let program run if letters are inputed to zip and radius
    if userZip.isdigit() == False or userRadius.isdigit() == False or days.isdigit() == False:
        print('You are reading this if an error occured')
        print('\nPlease close the application and try again')
        time.sleep(10)
    else: 
        print('\nRunning Program...\n')
        #Query to website doctors section    
        driver.get(doctors + '?zip=' + str(userZip) + '&specialty=Any')
        try:
            driver.find_element_by_id('is21').click()
            driver.find_element_by_id('submitAgeGate').click()
        except NoSuchElementException as exception:
            print('')

        #This block finds doctor listings that fall in the radius range
        xDis = driver.find_elements_by_css_selector('body > section.doctors_office > div.container > div > div.col-sm-9 > div.doctor_listing > div > div > div.listing.clearfix > div.listing_right > ul.list_doctor > li:nth-child(2)')
        distances = [x.text.split(' ') for x in xDis]
        #Counter to keep track of which indices matched the radius range       
        counter = 0
        match = []
        for distance in distances:
            if float(distance[1]) <= int(userRadius):
                match.append(counter)
            counter += 1

        #This block finds the listings ID to query website database to find analytics
        xLoc = driver.find_elements_by_css_selector('body > section.doctors_office > div.container > div > div.col-sm-9 > div.doctor_listing > div > div > div.allentown_title.clearfix > a')
        locations = [x.get_attribute('href').split('_') for x in xLoc]
        matchLocations = []
        mIds = []
        print('\n\n')
        time.sleep(3)
        for i in match:
            matchLocations.append(locations[i])
        for i in matchLocations:
            mIds.append(i[1])
        
        #Output block
        print('Found ' + str(len(mIds)) + ' listings within ' + str(userRadius) + ' miles of Zip Code ' + str(userZip))
        print('\n\n')
        time.sleep(5)            
        print('Logging in to each practice to find their analytics for the past ' + str(days) + '\n')
        time.sleep(5)
        print('\nThis may take a while...\n\n')
        time.sleep(5)
        print('There will be a count down so you know when the program is about to finish\n')
        print('Program is done when counter reaches ' + str(len(mIds)))
        print('\n\n')
        time.sleep(4)
        #counter to let users know when loop is done
        counter = 1
        #Output message for email
        outPutMessage = []

        #Loop through IDs
        for i in mIds:
            print(counter)
            #Outout to let user know loop is almost done
            if str(counter) == str(len(mIds)):
                print('\nAlmost Done!\n\n')
            driver.get(url)
            #Log in try block
            try:
                driver.find_element_by_id('qf_login_full__fields__email').send_keys('')
                driver.find_element_by_id('qf_login_full__fields__password').send_keys('')
                driver.find_element_by_id('qf_login_full__submit').click()
            except NoSuchElementException as exception:
                print('')  
            driver.get(url2)
            driver.find_element_by_id('gs_id').send_keys(i, Keys.ENTER)#driver.find_element_by_id('gs_id').send_keys(mIds[0], Keys.ENTER)      
            time.sleep(2)
            #Keep location before singing in as practice
            location = driver.find_element_by_css_selector('#datagrid > tbody > tr > td:nth-child(4)').text
            driver.find_element_by_css_selector('#icons > li > span').click()
            driver.find_element_by_css_selector('#node-user_admin_user_practice-edit > div > p:nth-child(7) > a').click()
            #Analytics section
            driver.get(ana)
            #Find days ago
            start_date = datetime.datetime.now() + datetime.timedelta(-int(days))
            #Clear placeholder and input new date
            driver.find_element_by_id('date_start').clear()
            driver.find_element_by_id('date_start').send_keys(str(start_date.month) + '/' + str(start_date.day) + '/' + str(start_date.year)) 
            driver.find_element_by_css_selector('#change_date > fieldset > div.qf-button-wrapper > button').click()
            #Data holds practice analytics
            data = []
            elemData = driver.find_elements_by_css_selector('#practices > tbody > tr > td')
            for i in elemData:
                data.append(i.text)
            #Chunk list to list of lists holding 5 elements each
            cData = list(chunk(data, 5))
            #Loop through chunkedData    
            for i in range(len(cData)):
                #If location matches requested location append the analytics to outPutMessage
                if cData[i][0] == location:
                    analytics = [
                        ('Location: ' + cData[i][0]),
                        ('State: ' + cData[i][1]),
                        ('Hits: ' + cData[i][2]),
                        ('Requested: ' + cData[i][3]),
                        ('Booked: ' + cData[i][4])
                    ]
                    outPutMessage.append(analytics)
            driver.get(logout)
            counter += 1
            print('')
        driver.quit()
        #Output outPutMessage to user in shell
        for i in outPutMessage:
            for x in i:
                print(x)
            print('')

        #Block that emails list to user
        print('\n\n')
        print('Emailing above list to you...')
        msg = MIMEMultipart()
        msg['From'] = 'hugo@marijuanadoctors.com'
        msg['To'] = email
        msg['Subject'] = 'Found ' + str(len(mIds)) + ' listings within ' + str(userRadius) + ' miles of Zip Code ' + str(userZip)
        bodyMessage = []
        bLen = 0
        for i in outPutMessage:
            bodyMessage.append('<div>' + ' '.join(i) + '<div>\n</br></br>\n')
        body = ' '.join(bodyMessage)
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login('hugo@marijuanadoctors.com', '')
        #send the email
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        #close the server
        server.quit()
        print('Email sent to ' + email) 
        print('\n\n')       

#Run main function
mainFunction()

#Keep program alive when done unless quit
tryAgain = input('All Done\nEnter 1 to run again or any other key to exit')

if tryAgain == '1':
    mainFunction()
else:
    quit()
                               





    