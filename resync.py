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
from resources import Collection, MemoryVerseEntry, INDENT_STRING

os.chdir(os.path.dirname(__file__) + "/resources")


def parse_verses(dom: BeautifulSoup, depth: int=0) -> list[MemoryVerseEntry]:
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
        entry = MemoryVerseEntry(address, content, isMemorized=stateOfMemory)

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


def extract_credentials(user: str, cred_dict: dict) -> (str, str):
    email = cred_dict["users"][user]["email"]
    password = cred_dict["users"][user]["password"]

    return email, password

def get_credentials() -> (str, str):
    with open('credentials.json') as f:
        credentials = json.loads(f.read())

    users = list(credentials['users'].keys())

    if len(users) == 1:
        user = users[0]
        return extract_credentials(user, credentials)

        # ans = input(f"Would you like to use the saved credentials for {user}? (Y/N) ").upper()
        # while True:
        #     if ans == "Y":
        #         return extract_credentials(user, credentials)
        #         break
        #     elif ans == "N":
        #         break # TODO implement using a different set of credentials
        #     else:
        #         ans = input("ERROR. Please enter a valid input: ").upper()

    elif len(users) > 1:
        # TODO implement an option to use a new set of credentials
        print("Please select a user.\n")

        for i, user in enumerate(users):
            print(f"{i+1}) {user}")

        while True:
            try:
                ans = int(input("Please enter the number of the user: ", end=''))
                return extract_credentials(users[ans], credentials)
            except (ValueError, IndexError):
                print("ERROR.", end=' ')
    else:
        pass # TODO implement the case for 0 saved users or error case

def login(driver: webdriver.Chrome, email: str, password: str) -> None:
    print("\nGET request to https://biblememory.com/login")
    driver.get("https://biblememory.com/login")

    print(f"{INDENT_STRING}Adding credentials...")
    driver.find_element(By.ID, "txtLoginEmail").send_keys(email)
    driver.find_element(By.ID, "txtLoginPassword").send_keys(password)
    driver.find_element(By.CLASS_NAME, "btnLogin").click()
    
    print(f"{INDENT_STRING}Login sucessful!\n")

def main():
    print("************* Re-synchronizing Local Library *************")
    print()
    print("Starting selenium webdriver instance...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1000,1200")
    driver = webdriver.Chrome(
        options=options,
        service=Service(ChromeDriverManager().install())
        )
    
    email, password = get_credentials()
    login(driver, email, password)

    myVerses = Collection('My Verses')
    parse_page(driver, myVerses)

    # serialize to JSON and save in 'library-log'
    os.chdir(os.path.dirname(__file__) + "/resources/library-logs")
    fileName = f"{str(timestamp()).replace('.', ':').replace(':', '_')}.json"
    with open(fileName, 'w+') as f:
        f.write(json.dumps(myVerses.to_dict(), indent=4))
    os.chdir(os.path.dirname(__file__) + "/resources/")

    print("\nSuccessfully parsed your entire library!")
    print("Shutting down webdriver instance...")
    driver.quit()

if __name__ == "__main__":
    main()
