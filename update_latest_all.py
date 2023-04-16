"""
Update JSON representing the latest status of a python package

The package is listed in data/package_names.txt

Source: data/package_names.txt
Output: data/latest/*.json
"""
import sys
import os
from src.update_all import update_all
from src.update_latest import update

if __name__ == "__main__":
    if not os.path.exists("data/latest"):
        os.mkdir("data/latest")
    update_all(update, index=int(sys.argv[1]), split_cnt=int(sys.argv[2]))
