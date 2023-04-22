"""
inspect saved latest json

Example: 

- 1) inspecting source code urls: 

python inspect_latest.py pandas info project_urls

- 2) inspecting maintainer emails: 

- 3) inpsecting license:

python inspect_latest.py tensorflow info license

(need to summary license for long string license)

"""
import sys
import copy
from src.json_tool import json_tool
from src.inspect_utils import inspect

if __name__ == "__main__":
    pkg_name = sys.argv[1]
    latest = json_tool.load(f"data/latest/{pkg_name}.json")
    assert len(sys.argv) >= 2, "must provide at least package name"
    if len(sys.argv[-1]) == 2:
        query_items = []
    elif sys.argv[-1] == "keys":
        query_items = copy.copy(sys.argv[2:-1])
    else:
        query_items = copy.copy(sys.argv[2:])
    inspect(latest, query_items, show_keys_only=sys.argv[-1] == "keys")
