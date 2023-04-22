"""
Updating Latest Json Filess from PyPi
"""
import sys
import os
import requests
import random
import subprocess
import pprint
from functools import lru_cache
import time
from src.time_utils import convert_to_datetime
from src.json_tool import json_tool


class Logger:
    def __init__(self, log_path):
        self._log_path = log_path

    def apply(self, func):
        def wrap(*args):
            self.append(*args[1:])
            return func(*args)

        return wrap

    def append(self, *args):
        with open(self._log_path, "a") as f:
            f.write(", ".join(map(str, args)) + "\n")


class UpdateController:
    def __init__(self, download_path="data/latest"):
        self._download_path = download_path

    def update(self, pkg_name):
        if self.already_download(pkg_name):
            if self.get_online_max_release_time(
                pkg_name
            ) > self.get_offline_max_release_time(pkg_name):
                latest = self.download_latest(pkg_name)
                json_tool.dump(f"{self._download_path}/{pkg_name}.json", latest)
        else:
            latest = self.download_latest(pkg_name)
            json_tool.dump(f"{self._download_path}/{pkg_name}.json", latest)

    def assert_update(self, pkg_name):
        assert self.get_online_max_release_time(
            pkg_name
        ) == self.get_offline_max_release_time(pkg_name)

    @staticmethod
    def create_file(path):
        if not os.path.exists(path):
            with open(path, "w") as fp:
                pass

    def get_offline_release_count(self, pkg_name):
        result = json_tool.load(f"{self._download_path}/{pkg_name}.json")
        return UpdateController.extract_max_time(result)

    def get_online_max_release_time(self, pkg_name):
        result = self.download_latest(pkg_name)
        return UpdateController.extract_max_time(result)

    @staticmethod
    def extract_max_time(result):
        assert "releases" in result and len(result["releases"])
        times = []
        for releases_content in result["releases"].values():
            for content in releases_content:
                times.append(convert_to_datetime(content["upload_time_iso_8601"]))
        assert len(times) > 0
        return max(times)

    def get_offline_max_release_time(self, pkg_name):
        result = self.download_latest(pkg_name)
        times = []
        for releases_content in result["releases"].values():
            for content in releases_content:
                times.append(convert_to_datetime(content["upload_time_iso_8601"]))
        return max(times)

    def already_download(self, pkg_name):
        return os.path.exists(f"data/latest/{pkg_name}.json")

    def get_online_release_count(self, pkg_name):
        result = self.download_latest(pkg_name)
        return len(result["releases"].keys())

    def downloadable(self, pkg_name):
        try:
            self.get_online_max_release_time(pkg_name)
            return "releases" in self.download_latest(pkg_name)
        except AssertionError:
            return False

    @lru_cache
    def download_latest(self, pkg_name):
        return self.download_with_retries(pkg_name)

    def download_with_retries(self, pkg_name):
        retry_cnt = 0
        while retry_cnt < 5:
            try:
                url = f"https://pypi.org/pypi/{pkg_name}/json"
                result = requests.get(url).json()
                assert "releases" in result
                break
            except:
                time.sleep(retry_cnt)
                retry_cnt += 1
        return result


def update(pkg_name):
    controller = UpdateController()
    if controller.downloadable(pkg_name):
        controller.update(pkg_name)
        controller.assert_update(pkg_name)
    else:
        print(pkg_name, "not found:")
        pprint.pprint(controller.download_latest(pkg_name))


if __name__ == "__main__":
    update(sys.argv[1])
