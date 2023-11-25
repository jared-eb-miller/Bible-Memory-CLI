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