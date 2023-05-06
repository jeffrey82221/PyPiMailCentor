import os
import tqdm
import json

def loop_over(func):
    def do_etl(src_path):
        with open(src_path, "r") as f:
            pkgs = list(map(lambda x: x.strip(), f))
            for pkg in tqdm.tqdm(pkgs, desc=f"{pkgs[0]}~{pkgs[-1]}"):
                func(pkg)

    return do_etl


class ETagStorage:
    def __init__(self, path):
        self._path = path        
    
    def get(self, key):
        if os.path.exists(f'{self._path}/{key}.json'):
            return json.load(open(f'{self._path}/{key}.json', 'r'))
        else:
            return None

    def update(self, key, etag):
        json.dump(etag, open(f'{self._path}/{key}.json', 'w'))