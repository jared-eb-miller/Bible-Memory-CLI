import os
import json
from datetime import datetime
from resources import CollectionFromDict

os.chdir(os.path.dirname(__file__) + "/resources/library-logs/")

def main():
    log_files = os.listdir()
    latest_log_file = log_files[-1]

    with open(latest_log_file, 'r') as f:
        log_dict = json.load(f)

    col = CollectionFromDict(log_dict)

    os.chdir(os.path.dirname(__file__) + "/resources/")
    with open("outFile.txt", 'w') as f:
        f.write(col.pretify())

if __name__ == '__main__':
    main()