"""
Sample and Download the Release Json Files before Infering the Schema
"""
import sys
import json
import random
import os
import tqdm
from src.json_tool import json_tool, JsonTool
from src.update_releases import ReleaseUpdator


def run(src_path, target_path, sample_size):
    with open(src_path, "r") as f:
        pkgs = list(map(lambda x: x.strip(), f))
    sampled_pkgs = random.sample(pkgs, sample_size)
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    updator = ReleaseUpdator(target_path, encrypt_save=False)
    for pkg in tqdm.tqdm(sampled_pkgs):
        updator.update(pkg)


if __name__ == "__main__":
    run(src_path=sys.argv[1], target_path=sys.argv[2], sample_size=int(sys.argv[3]))
