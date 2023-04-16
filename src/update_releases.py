"""
Update releases json in data/releases folder
"""
import json
import glob
import requests
import re
import os
from src.ignore import ignore_filter
from src.json_tool import json_tool, JsonTool


class ReleaseUpdator:
    def __init__(self, target_path="data/releases", encrypt_save=True):
        self._target_path = target_path
        self._encrypt_save = encrypt_save

    def save_path(self, pkg_name, ver):
        return f"{self._target_path}/{pkg_name}-{ver}.json"

    def update(self, pkg_name):
        releases = list(ReleaseUpdator.get_release_versions(pkg_name))
        n_all_releases = len(releases)
        releases = ignore_filter.connect(releases)
        releases = filter(
            lambda ver: not os.path.exists(self.save_path(pkg_name, ver)),
            releases,
        )
        releases = list(releases)
        n_filtered_releases = len(releases)
        print(f"# of releases for {pkg_name} (filtered/all): {n_filtered_releases}/{n_all_releases}")
        if releases:
            jsons = map(
                lambda release: (
                    pkg_name,
                    release,
                    ReleaseUpdator.download_json(pkg_name, release),
                ),
                releases,
            )
            saved_json = map(lambda x: self.save_json(*x), jsons)
            _ = list(saved_json)

    @staticmethod
    def get_release_versions(pkg_name):
        json_path = glob.glob(f"data/latest/{pkg_name}.rc*.json")
        if json_path:
            result = json_tool.load(json_path[0])
            return list(result["releases"].keys())
        else:
            return []

    @staticmethod
    def download_json(pkg_name, version):
        url = f"https://pypi.org/pypi/{pkg_name}/{version}/json"
        result = requests.get(url).json()
        return result

    def save_json(self, pkg_name, ver, json_obj):
        save_path = self.save_path(pkg_name, ver)
        if self._encrypt_save:
            json_tool.dump(save_path, json_obj)
        else:
            JsonTool._dump_original(save_path, json_obj)
        print('\t\t', save_path, 'saved')


update = ReleaseUpdator().update
