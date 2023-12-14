import os
import platform
import time
if platform.system() == "Windows":
    clear = lambda: os.system("cls")
else:
    clear = lambda: os.system("clear")

def displayMenu():
    print("""
******************** Bible Memory CLI ********************

    1) Re-synchronize local library
    2) View statistics
    3) Review / study verses
    4) Exit

**********************************************************
""")

def userChoice() -> int:
    displayMenu()
    return int(input(
        "Enter your choice: "
    ))

def resync():
    import resync
    print("\nRe-synchronizing local library...")
    resync.main()

def viewStats():
    import viewStats
    viewStats.main()
    time.sleep(5)

def reviewVerses():
    print("starting review")

# build hashmap of function objects
choices = [resync, viewStats, reviewVerses, exit]
switcher = {}
for i, choice in enumerate(choices, 1):
    switcher.update({
        i: choice
    })

clear()
while True:
    try:
        switcher[userChoice()]()
        clear()
    except (KeyError, ValueError):
        clear()
        print("ERROR.")