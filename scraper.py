from __future__ import annotations
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
timestamp = datetime.now
import resources

INDENT_WIDTH = 2
INDENT_STRING = ''.join([' ']*INDENT_WIDTH)

os.chdir(os.path.dirname(__file__) + "/resources")


class Collection:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.verses: list[resources.MemoryVerseEntry] = []
        self.subcollections: list[Collection] = []
        self.url_name = ''
        self.parent = parent

    def add_subcollection(self, collection: Collection) -> None:
        self.subcollections.append(collection)
        collection.set_parent(self)

    def add_subcollections(self, collections: list[Collection]) -> None:
        for collection in collections:
            self.add_subcollection(collection)

    def remove_subcollection(self, collection: Collection) -> None:
        self.subcollections.remove(collection)

    def set_parent(self, parent: Collection) -> None:
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
        
        return '/'.join([e.name for e in ancestors[::-1]])

def parse_verses(dom: BeautifulSoup, depth: int=0) -> list[resources.MemoryVerseEntry]:
    listItems = dom.find_all('div', {'class': "MemoryVerseListItem"})

    numListItems = len(listItems)
    if numListItems > 0:
        indent = ''.join([INDENT_STRING]*depth)
        print(f"{indent}Collected {numListItems} memory verse entries")

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

def parse_subcollections(dom: BeautifulSoup, depth: int=0) -> list[Collection]:
    listItems = dom.find_all('div', {'class': "CategoryListItem"})

    numListItems = len(listItems)
    if numListItems > 0:
        indent = ''.join([INDENT_STRING]*depth)
        print(f"{indent}Collected {numListItems} subcollections")

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

def parse_page(driver: webdriver.Chrome,  into_collection: Collection, depth: int=0):
    # wait for content to load
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "ctl00_MainContent_pnlMyVerses")) 
    )

    # parse page
    indent = ''.join(['  ']*depth)
    print(f"{indent}Parsing {into_collection.ancestry()}...")

    dom = BeautifulSoup(driver.page_source, 'html.parser')
    into_collection.verses = parse_verses(dom, depth+1)
    into_collection.add_subcollections(parse_subcollections(dom, depth+1))


    # recursively explore subcollections
    for subcollection in into_collection.subcollections:
        driver.get(f"https://biblememory.com/collection/{subcollection.url_name}/")
        parse_page(driver, subcollection, depth=depth+1)

def format_output(myVerses: Collection) -> str:
    output = "My Verses\n"

    for collection in myVerses.subcollections:
        output += "|- " + collection.name + ":\n"
        
        for verse in collection.verses:
            output += "|   |- " + str(verse.address) + "\n"

        for subcollection in collection.subcollections:
            output += "|   |- " + subcollection.name + ":\n"

            for verse in subcollection.verses:
                output += "|   |   |- " + str(verse.address) + "\n"
    
    return output

def get_credentials(user: str, cred_dict: dict):
    email = cred_dict["users"][user]["email"]
    password = cred_dict["users"][user]["password"]

    return email, password

def main():
    print("Starting selenium webdriver instance...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1000,1200")
    driver = webdriver.Chrome(
        options=options,
        service=Service(ChromeDriverManager().install())
        )
    
    with open('credentials.json') as f:
        credentials = json.loads(f.read())

    users = list(credentials['users'].keys())
    user = "DEFAULT"
    email = "DEFAULT"
    password = "DEFAULT"

    if len(users) == 1:
        user = users[0]
        ans = input(f"Would you like to use the saved credentials for {user}? (Y/N) ").upper()
        while True:
            if ans == "Y":
                email, password = get_credentials(user, credentials)
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
                email, password = get_credentials(users[ans], credentials)
                break
            except (ValueError, IndexError):
                print("ERROR.", end=' ')
    else:
        pass # TODO implement the case for 0 saved users or error case

    # login
    print("\nGET request to https://biblememory.com/login")
    driver.get("https://biblememory.com/login")
    print(f"{INDENT_STRING}Adding credentials...")
    driver.find_element(By.ID, "txtLoginEmail").send_keys(email)
    driver.find_element(By.ID, "txtLoginPassword").send_keys(password)
    driver.find_element(By.CLASS_NAME, "btnLogin").click()
    print(f"{INDENT_STRING}Login sucessful!\n")


    myVerses = Collection('My Verses')
    parse_page(driver, myVerses)

    with open("outFile.txt", "w") as outFile:
        outFile.write(format_output(myVerses))


    print("\nSuccessfully parsed your entire library!")
    print("Shutting down webdriver instance...")
    driver.quit()
    print("Done.")

if __name__ == "__main__":
    main()
