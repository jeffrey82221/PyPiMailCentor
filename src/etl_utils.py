import os
import tqdm
import json
import abc
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from requests.exceptions import ConnectionError, ConnectionResetError
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

class TOSException(Exception):
    pass

class NotExistingException(Exception):
    pass

class AlreadyExistException(Exception):
    pass

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
            raise NotExistingException
        elif etag is None:
            header, body = self.call_api(key)
            self.update_cache(key, header['ETag'], body)
        else:
            try:
                header, body = self.call_api(key, etag=etag)
                self.update_cache(key, header['ETag'], body)
            except AlreadyExistException:
                body = json_tool.load(f'{self.cache_path}/{key}.json')
            except (ConnectionError, ConnectionResetError):
                time.sleep(15)
                return self.get(key)
            except BaseException as e:
                raise e
        return body
    
    def update_cache(self, key, etag, body):
        self.etag_store.update(key, etag)
        make_folder(self.cache_path, key)
        json_tool.dump(f"{self.cache_path}/{key}.json", body)

