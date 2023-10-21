from bs4 import BeautifulSoup
import requests
import json
import os
from datetime import datetime
timestamp = datetime.now

os.chdir(os.path.dirname(__file__) + "/resources")


class MemoryVerseEntry:
    class Address:
        def __init__(
                self, 
                book: int, 
                chapter: int, 
                verse_start: int, 
                verse_end=None
                ):
            self.book = book
            self.chapter = chapter
            if verse_end and (verse_end != verse_start):
                self.verse_start = verse_start
                self.verse_end = verse_end
                self.verses = tuple(range(verse_start, verse_end + 1))
                self.isSingleVerse = False
            else:
                self.verses = tuple([verse_start])
                self.verse = verse_start
                self.isSingleVerse = True            
        
        def __str__(self):
            if hasattr(self, 'isSingleVerse'):
                if not self.isSingleVerse:
                    return f"{self.book} {self.chapter}:{self.verse_start}-{self.verse_end}"
            return f"{self.book} {self.chapter}:{self.verse}"

    class SingleVerse(Address):
        def __init__(self, book: int, chapter: int, verse: int):
            super().__init__(book, chapter, verse)
            del self.isSingleVerse

        def __eq__(self, __value: object) -> bool:
            if isinstance(__value, type(self)): 
                return (
                    __value.book == self.book \
                    and __value.chapter == self.chapter \
                    and __value.verse == self.verse
                )

    def __init__(self, address: str, content: str, isMemorized: bool):
        self.address = self._parse_address(address)
        self.content = content
        self.isMemorized = isMemorized
        self.numVerses = 1 if self.address.isSingleVerse else len(self.address.verses)
        self.versesContained = tuple([
            MemoryVerseEntry.SingleVerse(
                self.address.book,
                self.address.chapter,
                v
            ) for v in self.address.verses
        ])

    def _parse_address(self, address: str) -> Address:
        # example address 'Psalm 1:1-6'
        verses_str = address[address.rfind(':') + 1:]
        if '-' in verses_str:
            verse_start, verse_end = [int(s) for s in verses_str.split('-')]
        else:
            verse_start = int(verses_str)
            verse_end = None

        chapter_str = address[address.rfind(' ') + 1:address.rfind(':')]
        chapter = int(chapter_str)

        book_str = address[:address.rfind(' ')]

        return MemoryVerseEntry.Address(
            book_str,
            chapter,
            verse_start,
            verse_end
        )

    def __str__(self):
        return f'MemoryVerseEntry object (\n\tAddress: {str(self.address)}\n\tContent: "{self.content}"\n)'

with open("payloads.json") as f:
    payloads = json.loads(f.read())

payload1 = payloads['payload1']
payload2 = payloads['payload2']

with open('credentials.json') as f:
    credentials = json.loads(f.read())

payload1["email"] = credentials["email"]
payload1["password"] = credentials["password"]

with requests.Session() as s:
    print("\nPOST request #1 (login) to https://biblememory.com/login.aspx")
    resp = s.post('https://biblememory.com/login.aspx', data=payload1).text

    auth = json.loads(resp)['auth']
    if auth == 'failed':
        print("\tERROR. Unable to login\n")
        quit()
    else:
        print("\tLogin successful")

    print("POST request #2 (payload) to https://biblememory.com/login.aspx")
    s.post('https://biblememory.com/login.aspx', data=payload2)

    print("GET request to https://biblememory.com/collection/master/")
    masterHTML = s.get('https://biblememory.com/collection/master/').text

html = BeautifulSoup(masterHTML, 'html.parser')

listItems = html.find_all('div', {'class': "MemoryVerseListItem"})

numListItems = len(listItems)
print(f"Collected {numListItems} memory verse entries")

memorizedList = []
notMemorizedList = []
entryDict = {
    "memorized": {},
    "notMemorized": {}
}

for parent in listItems:
    # navagate HTML tree
    verseInfoItem = parent.contents[7]
    address = verseInfoItem.contents[1].text[2:].strip()
    content = verseInfoItem.contents[3].text.strip()

    statusInfoItem = parent.contents[-2]

    if statusInfoItem.text.strip() == "Not Yet Memorized":
        entryDict['notMemorized'].update({
            address: content
        })
        entry = MemoryVerseEntry(address, content, isMemorized=False)
        notMemorizedList.append(entry)
    else:
        entryDict['memorized'].update({
            address: content
        })
        entry = MemoryVerseEntry(address, content, isMemorized=True)
        memorizedList.append(entry)

print(f"Parsed all {numListItems} memory verse entries")

os.chdir(os.path.dirname(__file__) + "/resources/library-logs")
fileName = f"{str(timestamp()).replace('.', ':').replace(':', '_')}.json"
print(fileName)
with open(fileName, 'w+') as f:
    f.write(json.dumps(entryDict, indent=4))

print() # beautify the CLI
