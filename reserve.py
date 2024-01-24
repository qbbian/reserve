from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

dr = webdriver.Chrome();
dr.get('https://www.thprd.org/portal/index.cfm')
username = os.environ.get('THPRD_USERNAME')
password = os.environ.get('THPRD_PASSWORD')

# Login Page
dr.find_element("name", "pID").send_keys(username)
# find password input field and insert password as well
dr.find_element("name", "pw").send_keys(password)
# click login button
dr.find_element("name", "login").click()
time.sleep(1)

dr.get('https://www.thprd.org/portal/classes/reservewizard.cfm')

# Select Tennis
while True:
    try:
        select = Select(dr.find_element(By.NAME, 'activity'))
        select.select_by_visible_text('Tennis')
        next_button = dr.find_element(By.XPATH, "//input[@type='submit'][@value='Next']")
        next_button.click()
    except Exception as e:
        print(f"An error has occurred: {e}");
        time.sleep(0.5)
    else:
        break;

available = False
# Loop here until the desired courts are available (at 8am sharp)
while not available:
    # Select Location
    #select = Select(dr.find_element(By.NAME, 'SelectFacility'))
    #select.select_by_visible_text('Tennis Center')
    while True:
        try:
            next_buttons = dr.find_elements(By.XPATH, "//input[@type='submit'][@value='Next']")
            next_buttons[-1].click()
        except Exception as e:
            print(f"An error has occurred: {e}");
            time.sleep(0.5)
        else:
            break;

    # Select Date
    dt = datetime.now()
    td = timedelta(days=7)
    reserve_date = dt + td
    reserve_date_str = reserve_date.strftime('%m/%d/%Y')
    print(reserve_date_str)
    select = Select(dr.find_element(By.NAME, 'activitydate'))
    try:
        select.select_by_value(reserve_date_str)
        available = True
    except:
        print("Date is not yet available")
        time.sleep(0.5)

# Courts are open!
while True:
    try:
        go_button = dr.find_element(By.XPATH, "//input[@type='submit'][@value='Go']")
        go_button.click()
    except Exception as e:
        print(f"An error has occurred: {e}");
        time.sleep(0.5)
    else:
        break;

# Now add them to the cart!
# We are only interested in 7pm to 8:30pm classes, hey hey
tables = dr.find_elements(By.XPATH, "//table[@width='750']/tbody")
table = tables[1]
slots = table.find_elements(By.TAG_NAME, 'tr')
available = False
for slot in slots:
    info = slot.find_elements(By.TAG_NAME, 'td')
    if len(info) > 2:
        if "6:00pm" in info[1].text and "7:30pm" in info[1].text:
            checkbox_col = info[2]
            checkbox_col.find_element(By.NAME, "enrollments").click()
            # Don't be greedy, once found one let's GTFO
            available = True
            break
            
# Last tr is the enroll row
if available is True:
    last = slots[-1]
    enroll = last.find_element(By.NAME, "enrollclasses")
    if enroll is not None:
        print("Successfully enrolled the class!")
        enroll.click()
    else:
        print("Error: Did not find the enroll class button")
else:
    print("No desired time slots are available")
