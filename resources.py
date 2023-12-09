from __future__ import annotations

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
    
    def to_dict(self) -> dict:
        return {
            str(self.address): {
                "content": self.content,
                "stateOfMemory": "memorized" if self.isMemorized else "notMemorized"
            }
        }

    def __str__(self) -> str:
        return f'MemoryVerseEntry object (\n\tAddress: {str(self.address)}\n\tContent: "{self.content}"\n)'
    
INDENT_WIDTH = 2
INDENT_STRING = ''.join([' ']*INDENT_WIDTH)

class Collection:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.verses: list[MemoryVerseEntry] = []
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
    
    def to_dict(self) -> dict:
        verse_dict = {}
        for verse in self.verses:
            verse_dict.update(verse.to_dict())

        collection_dict = {}
        for collection in self.subcollections:
            collection_dict.update(collection.to_dict())

        contents = {
            "verses": verse_dict,
            "subcolections": collection_dict
        }

        return {self.name: contents}

    def pretify(self) -> str:
        output = self.name + ":\n"

        for verse in self.verses:
            output += "|- " + str(verse.address) + "\n"

        for collection in self.subcollections:
            output += "|- " + collection.name + ":\n"
            
            for verse in collection.verses:
                output += "|   |- " + str(verse.address) + "\n"

            for subcollection in collection.subcollections:
                output += "|   |- " + subcollection.name + ":\n"

                for verse in subcollection.verses:
                    output += "|   |   |- " + str(verse.address) + "\n"
        
        return output
    
class CollectionFromDict(Collection):
    def __init__(self, log_dict: dict, parent=None):
        name = list(log_dict.keys())[0]
        super().__init__(name, parent)

        verse_dict = log_dict[name]["verses"]
        for v_addr in verse_dict.keys():
            self.verses.append(MemoryVerseEntry(
                v_addr,
                verse_dict[v_addr]["content"],
                True if verse_dict[v_addr]["stateOfMemory"] == "memorized" else False
                ))
            
        subcollection_dict = log_dict[name]["subcolections"]
        for sc_name in subcollection_dict.keys():
            self.add_subcollection(
                CollectionFromDict({
                    sc_name: subcollection_dict[sc_name]
                })
            )