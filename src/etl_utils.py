import os
import tqdm
import json
import abc
from pathlib import Path
from typing import Dict, Optional, Tuple
from src.json_tool import json_tool

def loop_over(func):
    def do_etl(src_path):
        with open(src_path, "r") as f:
            pkgs = list(map(lambda x: x.strip(), f))
            for pkg in tqdm.tqdm(pkgs, desc=f"{pkgs[0]}~{pkgs[-1]}"):
                func(pkg)

    return do_etl

def make_folder(folder_path, key):
    if '/' in key:
        directory = '/'.join(key.split('/')[:-1])
        whole_path = f'{folder_path}/{directory}'
        if not os.path.exists(whole_path):
            Path(whole_path).mkdir(parents=True)

class ETagStorage:
    def __init__(self, path):
        self._path = path

    def get(self, key):
        if os.path.exists(f"{self._path}/{key}.json"):
            return json.load(open(f"{self._path}/{key}.json", "r"))
        else:
            return None

    def update(self, key, etag):
        make_folder(self._path, key)
        json.dump(etag, open(f"{self._path}/{key}.json", "w"))

class APIGetter:
    def __init__(self, etag_path, cache_path):
        self.etag_store = ETagStorage(etag_path)
        self.cache_path = cache_path
    
    @abc.abstractmethod
    def call_api(self, key: str, etag='') -> Tuple[int, Dict, Optional[Dict]]:
        raise NotImplemented
    
    def get(self, key):
        etag = self.etag_store.get(key)
        if etag == 404:
            body = dict()
        elif etag is None:
            status_code, header, body = self.call_api(key)
            if status_code == 200:
                self.update_cache(key, header['ETag'], body)
            elif status_code == 404:
                self.update_cache(key, 404, body)
            else:
                raise ValueError('status code is not 404/200')
        else:
            status_code, header, body = self.call_api(key, etag=etag)
            if status_code == 304:
                body = json_tool.load(f'{self.cache_path}/{key}.json')
            elif status_code == 200:
                self.update_cache(key, header['ETag'], body)
            else:
                raise ValueError('status code is not 304/200')
        return body
    
    def update_cache(self, key, etag, body):
        self.etag_store.update(key, etag)
        make_folder(self.cache_path, key)
        json_tool.dump(f"{self.cache_path}/{key}.json", body)

