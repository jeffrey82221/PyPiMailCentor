"""
Extract info of packages and save into a Json file

source: data/latest
target: data/package_info.json

Refactor: 
- [X] Build Registered Pipeline
    - [X] Unit: extract method + transform method + target_field_name
    - [X] Ordering: start: get_data >> filter: has_info >> map: [unit1, unit2, unit3] >> map: [unit4, unit5, unit6] >> filter: xxx
- Fix: rate limit. When using GITHUB_TOKEN , the rate limit is 1,000 requests per hour per repository.
- [X] Think about how to debug the pipeline on each node. 
- [X] Refactor: 
    - [X] Save latest json file names into latest.menu
    - [X] Move the following segment in update_all.py to update_all.py and update_latest.py
        as do_etl
        ```
        # Do update
        with open(f"{SPLIT_PATH}/{file}", "r") as f:
            pkgs = list(map(lambda x: x.strip(), f))
            for pkg in tqdm.tqdm(pkgs, desc=f"{pkgs[0]}~{pkgs[-1]}"):
                update(pkg)
        ```
    - [X] Enable update_all.py to take SRC_PATH as input
    - [X] Move extract_package_info.py to src/ and rename as update_info.py
    - [X] Apply update_all.py to `update` of update_info.py
- [X] Feature: Run crawling using multiple github action jobs (for speed up.)
- [X] Check if the github url is the true github repo
"""
import os
import pprint
import binascii
import re
import requests
import typing
from toolz import curry
from toolz import curried
from toolz.functoolz import pipe
import pypistats
import json
from functools import partial
from httpx import HTTPStatusError
import time
from src.json_tool import json_tool

TARGET_PATH = "/tmp/info.jsonl"


def take_github_urls(project_urls):
    if isinstance(project_urls, dict):
        result = []
        for url in project_urls.values():
            if re.match(r"https?:\/\/github\.com\/[\w-]+\/[\w-]+(?:\.git)?\/?", url):
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

def remove_invalid(github_urls):
    results_200 = []
    for url in github_urls:
        if requests.get(url).status_code == 200:
            results_200.append(url)
    results = []
    if len(results_200) > 1:
        # only take the github repo with valid owner and repo name. 
        for url in results_200:
            owner = url.split('/')[-2]
            repo = url.split('/')[-1]
            if requests.get(f"https://api.github.com/repos/{owner}/{repo}").status_code == 200:
                results.append(url)
    else:
        results = results_200
    assert len(results) <= 1, "There should be only at least one url left"
    return results

def get_star_count(github_urls):
    star_count_list = []
    for url in github_urls:
        owner = url.split("/")[3]
        repo = url.split("/")[4]
        data = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/stargazers"
        ).json()
        if isinstance(data, list):
            star_count_list.append(len(data))
        else:
            print(data)
    if star_count_list:
        return sum(star_count_list)
    else:
        return None


def load_data(src_path, fn):
    try:
        return (fn, json_tool.load(f"{src_path}/{fn}"))
    except binascii.Error:
        print("skip", fn)
        return None


def field_wise_transformation(
    transforms: typing.Dict[str, typing.Callable], data: dict
):
    result = dict()
    for field, func in transforms.items():
        result[field] = func(data)
    return result


def field_wise_enrichment(transforms: typing.Dict[str, typing.Callable], data: dict):
    for field, func in transforms.items():
        data[field] = func(data)
    return data


def verbose(pipe):
    for i, data in enumerate(pipe):
        print(i)
        pprint.pprint(data)
        yield data


def get_180days_download_count(pkg_name, max_try=10):
    result = None
    for i in range(max_try):
        try:
            json_str = pypistats.overall(pkg_name, format="json")
            wm_data, wom_data = json.loads(json_str)["data"]
            result = wm_data["downloads"] + wom_data["downloads"]
            break
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                break
            elif e.response.status_code == 429:
                time.sleep(i * 5)
                if i < max_try:
                    continue
                else:
                    raise e
            else:
                raise e
    return result


def append_line(data):
    json_str = json.dumps(data, ensure_ascii=True)
    with open(TARGET_PATH, "a") as f:
        f.write(json_str + "\n")


def update(src_path):
    if os.path.exists(TARGET_PATH):
        os.remove(TARGET_PATH)
    pipe(
        open(src_path, "r"),
        curried.map(lambda x: x.replace("\n", "")),
        curried.filter(lambda x: ".json" in x),
        curried.map(curry(load_data)("data/latest")),
        curried.filter(lambda x: x[1] is not None and "info" in x[1] and x[0] == f'{x[1]["info"]["name"]}.json'),
        curried.map(lambda x: x[1]),
        curried.map(
            curry(field_wise_transformation)(
                {
                    "name": lambda x: x["info"]["name"],
                    "license": lambda x: x["info"]["license"],
                    "github_urls": lambda x: remove_invalid(take_github_urls(
                        x["info"]["project_urls"]
                    )),
                }
            ),
        ),
        curried.filter(lambda x: len(x["github_urls"]) == 1),
        curried.map(
            curry(field_wise_enrichment)(
                {
                    "downloads_in_180days": lambda x: partial(
                        get_180days_download_count, max_try=3
                    )(x["name"]),
                    "owner": lambda x: x["github_urls"][0].split('/')[-2],
                    "repo": lambda x: x["github_urls"][0].split('/')[-1],
                }
            )
        ),
        curried.filter(lambda x: x["downloads"] is not None),
        verbose,
        curried.map(append_line),
        list,
    )

if __name__ == "__main__":
    SRC_PATH = "data/latest.menu"
    update(SRC_PATH)
