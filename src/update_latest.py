"""
Updating Latest Json Filess from PyPi

- [X] Revise the crawling logic
    - [X] A etag storage object 
        - [X] get_etag('package_name') -> Optional[str]
        - [X] update_etag('package_name', 'etag')
    - [X] New Update Flow:
"""
import sys
import requests
from src.json_tool import json_tool
from src.etl_utils import loop_over, ETagStorage

etag_storage = ETagStorage('etag/latest')

@loop_over
def update(pkg_name):
    """
    if etag exists:
        if etag is outdated:
            -> get result
            -> retries if no 'releases' key
        else:
            pass
    else:
        -> get result
        -> retries if no 'releases' key
    """
    etag = etag_storage.get(pkg_name)
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    if etag is None:
        res = requests.get(url)
        if res.status_code == 200:
            result = res.json()
            assert 'releases' in result, f'release is not in response, only {result.keys()}'
            json_tool.dump(f"data/latest/{pkg_name}.json", result)
            etag_storage.update(pkg_name, res.headers['ETag'])
        elif res.status_code == 404:
            pass
        else:
            raise ValueError(f'status_code is not 200/404 but {res.status_code}')
    else:
        res = requests.get(url, headers={'If-None-Match': etag})
        if res.status_code == 304:
            pass
        elif res.status_code == 404:
            pass
        elif res.status_code == 200:
            result = res.json()
            assert 'releases' in result, f'release is not in response, only {result.keys()}'
            json_tool.dump(f"data/latest/{pkg_name}.json", result)
            etag_storage.update(pkg_name, res.headers['ETag'])
        else:
            raise ValueError(f'status_code is not 200/304/404 but {res.status_code}')


if __name__ == "__main__":
    update(sys.argv[1])
