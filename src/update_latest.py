import sys
import requests
import os
from src.json_tool import json_tool


def update(pkg_name):
    result = get_data(pkg_name)
    if "releases" in result:
        if download_new(pkg_name, result):
            remove_old(pkg_name, result)
        else:
            pass
    else:
        pass


def get_data(pkg_name):
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    result = requests.get(url).json()
    return result


def download_new(pkg_name, result):
    rc = len(result["releases"].keys())
    save_path = f"data/latest/{pkg_name}.rc{rc}.json"
    if not os.path.exists(save_path):
        json_tool.dump(save_path, result)
        return True
    else:
        return False


def remove_old(pkg_name, result):
    rc = len(result["releases"].keys()) - 1
    while rc > 0:
        old_json_path = f"data/latest/{pkg_name}.rc{rc}.json"
        if os.path.exists(old_json_path):
            os.remove(old_json_path)
            break
        else:
            pass
        rc -= 1


if __name__ == "__main__":
    update(sys.argv[1])
