import sys
import copy
from src.update_releases import ReleaseUpdator
from src.inspect_utils import inspect

if __name__ == "__main__":
    pkg_name = sys.argv[1]
    version = sys.argv[2]
    latest = ReleaseUpdator.download_json(pkg_name, version)
    assert len(sys.argv) >= 3, "must provide at least package name"
    if len(sys.argv[-1]) == 3:
        query_items = []
    elif sys.argv[-1] == "keys":
        query_items = copy.copy(sys.argv[3:-1])
    else:
        query_items = copy.copy(sys.argv[3:])
    inspect(latest, query_items, show_keys_only=sys.argv[-1] == "keys")
