"""
Update JSON representing the latest status of a python package

The package is listed in data/package_names.txt

Source: data/latest.menu
Tmp:  /tmp/info.jsonl
Output: emailing_content.jsonl
"""
import sys
from src.update_all import update_all
from src.update_info import update

if __name__ == "__main__":
    update_all(update, src_path=sys.argv[1], index=int(sys.argv[2]), split_cnt=int(sys.argv[3]))
