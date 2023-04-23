"""
Extract info of packages and save into a Json file

source: data/latest
target: data/package_info.json

Refactor: 
- [ ] Build Registered Pipeline
    - [ ] Unit: extract method + transform method + target_field_name
    - [ ] Ordering: start: get_data >> filter: has_info >> map: [unit1, unit2, unit3] >> map: [unit4, unit5, unit6] >> filter: xxx
- [ ] Run pipeline using multi-thread map
"""
import os
import tqdm
import pprint
import binascii
import re
import requests
from src.json_tool import json_tool


regex = r"https?:\/\/github\.com\/[\w-]+\/[\w-]+(?:\.git)?\/?"


def take_github_urls(project_urls):
    if isinstance(project_urls, dict):
        result = []
        for url in project_urls.values():
            if re.match(regex, url):
                if url.count("/") > 4:
                    url = "/".join(url.split("/")[:5])
                url = url.replace("http://github.com", "https://github.com")
                url = url.replace(".git", "")
                if "#" in url:
                    url = url.split("#")[0]
                url = url.lower()
                result.append(url)
            else:
                pass
        return list(set(result))
    else:
        return []

def get_star_count(github_urls):
    star_count_list = []
    for url in github_urls:
        owner = url.split('/')[3]
        repo = url.split('/')[4]
        data = requests.get(f'https://api.github.com/repos/{owner}/{repo}/stargazers').json()
        if isinstance(data, list):
            star_count_list.append(len(data))
    if star_count_list:
        return sum(star_count_list)
    else:
        return None

def do_etl(src_path, target_path):
    src_files = sorted(filter(lambda x: ".json" in x, os.listdir(src_path)))

    results = []
    for fn in tqdm.tqdm(src_files):
        result = dict()
        try:
            data = json_tool.load(f"{src_path}/{fn}")
            result["name"] = data["info"]["name"]
            result["author"] = data["info"]["author"]
            result["author_email"] = data["info"]["author_email"]
            result["maintainer"] = data["info"]["maintainer"]
            result["maintainer_email"] = data["info"]["maintainer_email"]
            result["github_urls"] = take_github_urls(data["info"]["project_urls"])
            result["stars"] = get_star_count(result['github_urls'])
            results.append(result)
        except binascii.Error:
            print("skip", fn)
        except KeyError:
            print("skip", fn, "due to invalid data fields:")
            print(data.keys())
    json_tool.dump(target_path, results)


if __name__ == "__main__":
    SRC_PATH = "data/latest"
    TARGET_PATH = "data/package_info.json"
    do_etl(SRC_PATH, TARGET_PATH)
    results = json_tool.load(TARGET_PATH)
    pprint.pprint(list(filter(lambda x: isinstance(x["stars"], int), results)))
