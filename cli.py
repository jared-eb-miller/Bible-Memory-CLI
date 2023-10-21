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
    import scraper

def viewStats():
    print("starting view stats")

def reviewVerses():
    print("starting review")

choices = [resync, viewStats, reviewVerses, exit]
switcher = {}
for i, choice in enumerate(choices, 1):
    switcher.update({
        i: choice
    })

while True:
    switcher[userChoice()]()
