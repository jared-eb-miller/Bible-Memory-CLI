from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from datetime import datetime
timestamp = datetime.now

import resources

os.chdir(os.path.dirname(__file__) + "/resources")

def get_credentials(user: str):
    email = credentials["users"][user]["email"]
    password = credentials["users"][user]["password"]

    return email, password

with open('credentials.json') as f:
    credentials = json.loads(f.read())

users = list(credentials['users'].keys())
user = "DEFAULT"
email = "DEFAULT"
password = "DEFAULT"

if len(users) == 1:
    user = users[0]
    #ans = input(f"Would you like to use the saved credentials for {user}? (Y/N) ").upper()
    ans = "Y"
    while True:
        if ans == "Y":
            email, password = get_credentials(user)
            break
        elif ans == "N":
            break # TODO implement using a different set of credentials
        else:
            ans = input("ERROR. Please enter a valid input: ").upper()
elif len(users) > 1:
    # TODO implement an option to use a new set of credentials
    print("Please select a user.\n")

    for i, user in enumerate(users):
        print(f"{i+1}) {user}")

    while True:
        try:
            ans = int(input("Please enter the number of the user: ", end=''))
            email, password = get_credentials(users[ans])
            break
        except (ValueError, IndexError):
            print("ERROR.", end=' ')
else:
    pass # TODO implement the case for 0 saved users or error case



# login
print("Starting webdriver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
print("GET request to https://biblememory.com/login")
driver.get("https://biblememory.com/login")
print("\tAdding credentials...")
driver.find_element(By.ID, "txtLoginEmail").send_keys(email)
driver.find_element(By.ID, "txtLoginPassword").send_keys(password)
driver.find_element(By.CLASS_NAME, "btnLogin").click()
print("\tLogin sucessful!")
class Collection:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.verses = []
        self.subcollections = []
        self.url_name = ''
        self.parent = parent

    def add_subcollection(self, collection) -> None:
        self.subcollections.append(collection)
        collection.set_parent(self)

    def add_subcollections(self, collections: list) -> None:
        for collection in collections:
            self.add_subcollection(collection)

    def remove_subcollection(self, collection) -> None:
        self.subcollections.remove(collection)

    def set_parent(self, parent) -> None:
        if self.parent is not None:
            if self.parent == parent:
                return
            self.parent.remove_subcollection(self)
        
        self.parent = parent

    def ancestry(self) -> str:
        ancestors = [self]
        generation = self
        while generation.parent is not None:
            generation = generation.parent
            ancestors.append(generation)
        
        return ' -> '.join([e.name for e in ancestors[::-1]])

        

def parse_verses(dom: BeautifulSoup) -> list[resources.MemoryVerseEntry]:
    listItems = dom.find_all('div', {'class': "MemoryVerseListItem"})

    numListItems = len(listItems)
    print(f"Collected {numListItems} memory verse entries")

    verseList = []

    for parent in listItems:
        # navagate HTML tree
        verseInfoItem = parent.contents[7]
        address = verseInfoItem.contents[1].text[2:].strip()
        content = verseInfoItem.contents[3].text.strip()

        statusInfoItem = parent.contents[-2]

        stateOfMemory = statusInfoItem.text.strip() != "Not Yet Memorized"
        entry = resources.MemoryVerseEntry(address, content, isMemorized=stateOfMemory)

        verseList.append(entry)
    
    return verseList

def parse_subcollections(dom: BeautifulSoup) -> list[Collection]:
    listItems = dom.find_all('div', {'class': "CategoryListItem"})

    numListItems = len(listItems)
    print(f"Collected {numListItems} subcollections")

    collectionList = []
    collectionNameList = []

    for elem in listItems:
        # navagate HTML tree
        human_name = elem.contents[3].text.strip().split('\xa0')[0]
        if human_name in collectionNameList:
            continue
        url_name = elem['name']

        col = Collection(human_name)
        col.url_name = url_name
        collectionList.append(col)
        collectionNameList.append(human_name)
    
    return collectionList

def parse_page(driver: webdriver.Chrome,  into_collection: Collection):
    # wait for content to load
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "ctl00_MainContent_pnlMyVerses")) 
    )

    # parse page
    dom = BeautifulSoup(driver.page_source, 'html.parser')
    into_collection.verses = parse_verses(dom)
    into_collection.add_subcollections(parse_subcollections(dom))


    # explore subcollections
    for subcollection in into_collection.subcollections:
        driver.get(f"https://biblememory.com/collection/{subcollection.url_name}/")
        parse_page(driver, subcollection)
    
    print(f"Parsed {into_collection.ancestry()} sucessfully.")

myVerses = Collection('My Verses')
parse_page(driver, myVerses)

print("My Verses")
for collection in myVerses.subcollections[:-1]:
    print("\t" + collection.name + ":")
    for verse in collection.verses:
        print("\t\t" + str(verse.address))
    for subcollection in collection.subcollections:
        print("\t\t" + subcollection.name + ":")
        for verse in subcollection.verses:
            print("\t\t\t" + str(verse.address))


# print("Waiting...")
# time.sleep(30)
