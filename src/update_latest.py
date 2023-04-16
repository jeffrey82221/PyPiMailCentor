"""
- [X] Build latest json updating control table:
    - [X] 1) Get release count 
    grep "^tensorflow," test.txt
    - [X] 2) Remove line from file and save to new file
    sed '/tensorflow, 34/d' test.txt >> new_test.txt; rm test.txt; mv new_test.txt test.txt
    - [X] 3) Add package with new release count to the new file 
    echo 'jskiner, 12312312' >> new_text.txt
- [X] Build online release count getter 
"""
import sys
import os
import requests
import random
import subprocess
import pprint
from functools import lru_cache
from src.json_tool import json_tool

class UpdateController:
    def __init__(self, control_table_path = 'controller.csv', download_path = 'data/latest'):
        UpdateController.create_file(control_table_path)
        self._path = control_table_path
        self._download_path = download_path

    def update(self, pkg_name):
        if self.already_download(pkg_name):
            if self.get_offline_release_count(pkg_name) < self.get_online_release_count(pkg_name):
                latest = self.download_latest(pkg_name)
                json_tool.dump(f'{self._download_path}/{pkg_name}.json', latest)
                release_cnt = self.get_online_release_count(pkg_name)
                self.update_release_count(pkg_name, release_cnt)
        else:
            latest = self.download_latest(pkg_name)
            json_tool.dump(f'{self._download_path}/{pkg_name}.json', latest)
            release_cnt = self.get_online_release_count(pkg_name)
            self.update_release_count(pkg_name, release_cnt)
    
    def assert_update(self, pkg_name):
        assert self.get_offline_release_count(pkg_name) == self.get_online_release_count(pkg_name), f'{pkg_name} not updated'
        latest = json_tool.load(f'{self._download_path}/{pkg_name}.json')
        assert latest == self.download_latest(pkg_name), f'{pkg_name} not identical'

    @staticmethod
    def create_file(path):
        if not os.path.exists(path):
            with open(path, 'w') as fp:
                pass
        
    def get_offline_release_count(self, pkg_name):
        if self.already_download(pkg_name):
            output = self._get_control_search_result(pkg_name)
            return int(output.split(b',')[-1].strip())
        else:
            return 0

    def already_download(self, pkg_name):
        output = self._get_control_search_result(pkg_name)
        return len(output) > 0

    def get_online_release_count(self, pkg_name):
        result = self.download_latest(pkg_name)
        return len(result["releases"].keys())
        

    def update_release_count(self, pkg_name, count):
        if self.already_download(pkg_name):
            line_str = self._get_control_search_result(pkg_name)
            random_tmp_file = f'/tmp/{str(random.randint(0,10**30))}.csv'
            # sed '/tensorflow, 34/d' test.txt >> new_test.txt; rm test.txt; mv new_test.txt test.txt
            UpdateController.create_file(random_tmp_file)
            assert os.path.exists(random_tmp_file)
            subprocess.run(['sed', f"'/{line_str}/d'", self._path, '>>', random_tmp_file])
            os.remove(self._path)
            os.rename(random_tmp_file, self._path)
            
        with open(self._path, 'a') as f:
            f.write(f'{pkg_name}, {count}\n')

    def _get_control_search_result(self, pkg_name):
        output = subprocess.run(['grep', f'^{pkg_name},', self._path], capture_output=True).stdout
        return output

    @lru_cache
    def download_latest(self, pkg_name):
        url = f"https://pypi.org/pypi/{pkg_name}/json"
        result = requests.get(url).json()
        try:
            assert 'releases' in result
        except AssertionError:
            print(f'latest result not found for {pkg_name}:')
            pprint.pprint(result)
            raise KeyError
        return result    

def update(pkg_name):
    try:
        controller = UpdateController('data/latest.control')
        controller.update(pkg_name)
        controller.assert_update(pkg_name)
    except KeyError:
        pass

if __name__ == "__main__":
    update(sys.argv[1])
