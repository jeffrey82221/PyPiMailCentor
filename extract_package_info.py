"""
Extract info of packages and save into a Json file

source: data/latest
target: data/package_info.json

Refactor: 
- [X] Build Registered Pipeline
    - [X] Unit: extract method + transform method + target_field_name
    - [X] Ordering: start: get_data >> filter: has_info >> map: [unit1, unit2, unit3] >> map: [unit4, unit5, unit6] >> filter: xxx
- Fix: rate limit. When using GITHUB_TOKEN , the rate limit is 1,000 requests per hour per repository.
- [ ] Think about how to debug the pipeline on each node. 
- [-] Run pipeline using multi-thread map
"""
import os
import tqdm
import pprint
import binascii
import re
import requests
import typing
from toolz import curry
from toolz import curried
from toolz.functoolz import pipe
from multiprocessing.dummy import Pool
from src.json_tool import json_tool


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


def generate_file_names(src_path):
    src_files = sorted(filter(lambda x: ".json" in x, os.listdir(src_path)))
    return tqdm.tqdm(src_files)


def load_data(src_path, fn):
    try:
        return json_tool.load(f"{src_path}/{fn}")
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


def do_etl(src_path, target_path):
    p = Pool(3)
    results = pipe(
        generate_file_names(src_path),
        curried.map(curry(load_data)(src_path)),
        curried.filter(lambda x: x is not None and "info" in x),
        curried.map(
            curry(field_wise_transformation)(
                {
                    "name": lambda x: x["info"]["name"],
                    "author": lambda x: x["info"]["author"],
                    "author_email": lambda x: x["info"]["author_email"],
                    "maintainer": lambda x: x["info"]["maintainer"],
                    "maintainer_email": lambda x: x["info"]["maintainer_email"],
                    "github_urls": lambda x: take_github_urls(
                        x["info"]["project_urls"]
                    ),
                }
            ),
        ),
        # verbose,
        list,
    )
    json_tool.dump(target_path, results)


if __name__ == "__main__":
    SRC_PATH = "data/latest"
    TARGET_PATH = "data/package_info.json"
    do_etl(SRC_PATH, TARGET_PATH)
    results = json_tool.load(TARGET_PATH)
