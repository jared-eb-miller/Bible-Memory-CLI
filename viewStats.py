import os
import json
from datetime import datetime
from resources import CollectionFromDict, Collection, CollectionStats

os.chdir(os.path.dirname(__file__) + "/resources/library-logs/")


def print_stats(c: Collection):
    stats = CollectionStats(c)

    print("Number of verse entries:       ", stats.num_verse_entries)
    print("Number of unique verse entries:", stats.num_unique_verse_entries)


def main():
    log_files = os.listdir()
    latest_log_file = log_files[-1]

    with open(latest_log_file, 'r') as f:
        log_dict = json.load(f)

    col = CollectionFromDict(log_dict)

    print_stats(col)

    # os.chdir(os.path.dirname(__file__) + "/resources/")
    # with open("outFile.txt", 'w') as f:
    #     f.write(col.pretify())

if __name__ == '__main__':
    main()