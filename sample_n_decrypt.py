"""
Sample and Decrypt the Latest Json Files before Infering the Schema
"""
import sys
import json
import random
import os
import tqdm
from src.json_tool import json_tool, JsonTool


def run(src_path, target_path, sample_size):
    files = os.listdir(src_path)
    sampled_files = random.sample(files, sample_size)
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    for file in tqdm.tqdm(sampled_files):
        json_obj = json_tool.load(f"{src_path}/{file}")
        JsonTool._dump_original(f"{target_path}/{file}", json_obj)


if __name__ == "__main__":
    run(src_path=sys.argv[1], target_path=sys.argv[2], sample_size=int(sys.argv[3]))
