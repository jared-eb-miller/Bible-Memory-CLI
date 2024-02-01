import os
import platform
from resources import userChoice

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
"""[1:])
    
def wait():
    input("Press enter to continue...")

def resync():
    clear()
    import resync
    resync.main()

def viewStats():
    clear()
    import viewStats
    viewStats.main()
    wait()

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
    displayMenu()
    everything_is_not_good_in_the_hood = True
    while everything_is_not_good_in_the_hood:
        try:
            switcher[userChoice()]()
            everything_is_not_good_in_the_hood = False
        except (KeyError, ValueError):
            print("ERROR.")
    clear()
