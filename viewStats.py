import os
import json
from datetime import datetime
from resources import CollectionFromDict, Collection, CollectionStats, INDENT_STRING

os.chdir(os.path.dirname(__file__) + "/resources/library-logs/")


def print_stats(c: Collection):
    stats = CollectionStats(c)

    print("'" + c.name + "' stats:")
    print(f"{INDENT_STRING*2}Number of verse entries:                 ", stats.num_verse_entries)
    print(f"{INDENT_STRING*2}Number of unique verse entries:          ", stats.num_unique_verse_entries)
    print(f"{INDENT_STRING*2}Number of verses in unique verse entries:", stats.num_component_verses)
    print(f"{INDENT_STRING*2}Number of verses:                        ", stats.num_verses)
    print(f"{INDENT_STRING*2}Number of verses memorized:              ", stats.num_verses_memorized)
    print(f"{INDENT_STRING*2}Number of verses not memorized:          ", stats.num_verses_not_memorized)

def main():
    # load library
    log_files = os.listdir()
    latest_log_file = log_files[-1]

    with open(latest_log_file, 'r') as f:
        log_dict = json.load(f)

    col = CollectionFromDict(log_dict)

    # diaplay
    print("******************* Display Statistics *******************")
    print()
    print_stats(col)
    print()
    # os.chdir(os.path.dirname(__file__) + "/resources/")
    # with open("outFile.txt", 'w') as f:
    #     f.write(col.pretify())

if __name__ == '__main__':
    main()