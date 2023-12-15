import os
import json
from datetime import datetime
from resources import CollectionFromDict, Collection, CollectionStats, INDENT_STRING

os.chdir(os.path.dirname(__file__) + "/resources/library-logs/")


def print_collection_stats(stats: CollectionStats) -> None:
    print("'" + stats.uc.name + "' stats:")
    print(f"{INDENT_STRING*2}Number of verse entries:                 ", stats.num_verse_entries)
    print(f"{INDENT_STRING*2}Number of unique verse entries:          ", stats.num_unique_verse_entries)
    print(f"{INDENT_STRING*2}Number of verses in unique verse entries:", stats.num_component_verses)
    print(f"{INDENT_STRING*2}Number of verses:                        ", stats.num_verses)
    print(f"{INDENT_STRING*2}Number of verses memorized:              ", stats.num_verses_memorized)
    print(f"{INDENT_STRING*2}Number of verses not memorized:          ", stats.num_verses_not_memorized)

def print_collection_book_breakdown(col: CollectionStats) -> None:
    print("Breakdown:")
    for book in col.books:
        print(f"{INDENT_STRING*2}{book.name} - ({book.num_verses_memorized}/{book.num_verses})")
        for c in book.chapters:
            print(f"{INDENT_STRING*4}Chapter {c.number} - {c.num_verses_memorized}/{c.num_verses}")

def main():
    # load library
    log_files = os.listdir()
    latest_log_file = log_files[-1]

    with open(latest_log_file, 'r') as f:
        log_dict = json.load(f)

    col = CollectionFromDict(log_dict)
    stats = CollectionStats(col)

    # diaplay
    print("******************* Display Statistics *******************")
    print()
    print_collection_stats(stats)
    print()
    print_collection_book_breakdown(stats)
    # os.chdir(os.path.dirname(__file__) + "/resources/")
    # with open("outFile.txt", 'w') as f:
    #     f.write(col.pretify())

if __name__ == '__main__':
    main()