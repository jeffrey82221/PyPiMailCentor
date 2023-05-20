"""
Extract info of packages and save into a Json file

source: data/latest
target: data/package_info.json

Enhance Efficiency: 
- [X] Do github repo checking every week only 
- [X] No need to show downloads_in_180days and license
- [X] Add filter to ignore package having owner/repo extracted 

Feature: 
- [ ] Extract download at another job. 

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
- [X] Add access token to Github API call

"""
import os
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
from src.github_api import (
    forks_api_getter, 
    stars_api_getter, 
    watcher_api_getter, 
    repo_api_getter
)
from src.etl_utils import NotExistingException, TOSException

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


def remove_invalid_github_url(urls):
    results = []
    for url in urls:
        status_code = requests.get(url).status_code
        if status_code == 200:
            results.append(url)
        elif status_code == 404:
            # Non-existing Page
            pass
        elif status_code == 451:
            # Take-Down Page
            pass
        else:
            raise ValueError(
                f"repo page call response with status scode: {status_code}. {url}"
            )
    return results

def remove_non_repo_github_url(urls):
    results = []
    for url in urls:
        owner, repo = url.split("/")[-2:]
        try:
            _ = repo_api_getter.get(f'{owner}/{repo}')
            results.append(url)
            print('repo found')
        except NotExistingException:
            print('no existing repo found (404)')
        except TOSException:
            print('tos but do have repo (403)')
            results.append(url)
        except BaseException as e:
            print('unknown situation')
            raise e
    return results


def select_most_popular_repo_url(urls):
    if len(urls) > 1:
        max_popularity = -1
        max_url = None
        for url in urls:
            owner, repo = url.split("/")[-2:]
            key = f'{owner}/{repo}'
            n_watchers = len(watcher_api_getter.get(key))
            n_stars = len(stars_api_getter.get(key))
            n_forks = len(forks_api_getter.get(key))
            popularity = n_watchers + n_stars + n_forks
            if popularity > max_popularity:
                max_url = url
        result = max_url
    elif len(urls) == 1:
        result = urls[0]
    else:
        result = None
    return result


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

def field_wise_delete(ignore_fields: typing.List[str], data: dict):
    for field in ignore_fields:
        del data[field]
    return data

def verbose(pipe):
    for i, data in enumerate(pipe):
        print(i, data)
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
            elif e.response.status_code == 429 or e.response.status_code == 503:
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
        curried.filter(
            lambda x: x[1] is not None
            and "info" in x[1]
            and x[0] == f'{x[1]["info"]["name"]}.json'
        ),
        curried.map(lambda x: x[1]),
        curried.map(
            curry(field_wise_transformation)(
                {
                    "name": lambda x: x["info"]["name"],
                    # "license": lambda x: x["info"]["license"],
                    "github_url": lambda x: pipe(
                        x["info"]["project_urls"],
                        take_github_urls,
                        remove_invalid_github_url,
                        remove_non_repo_github_url,
                        select_most_popular_repo_url,
                    ),
                }
            ),
        ),
        curried.filter(lambda x: isinstance(x["github_url"], str)),
        curried.map(
            curry(field_wise_enrichment)(
                {
                    "downloads_in_180days": lambda x: partial(
                        get_180days_download_count, max_try=3
                    )(x["name"]),
                    "owner": lambda x: x["github_url"].split("/")[-2],
                    "repo": lambda x: x["github_url"].split("/")[-1],
                }
            )
        ),
        curried.filter(lambda x: x["downloads_in_180days"] is not None),
        curried.map(
            curry(field_wise_delete)(
                ['downloads_in_180days', 'github_url']
            )
        ),
        verbose,
        curried.map(append_line),
        list,
    )


if __name__ == "__main__":
    SRC_PATH = "data/latest.menu"
    update(SRC_PATH)
