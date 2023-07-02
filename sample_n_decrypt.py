"""
Sample and Decrypt the Latest Json Files before Infering the Schema
"""
import sys
import random
import os
import tqdm
from src.json_tool import json_tool, JsonTool


def run(src_path, target_path, sample_size):
    files = [os.path.join(root, file) for root, dirs, files in os.walk(src_path) for file in files if file.endswith('.json')]
    print("Number of src json files:", len(files))
    sampled_files = random.sample(files, sample_size)
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    for file in tqdm.tqdm(sampled_files):
        json_obj = json_tool.load(f"{file}")
        json_file = file.split("/")[-1]
        JsonTool._dump_original(f"{target_path}/{json_file}", json_obj)


if __name__ == "__main__":
    run(src_path=sys.argv[1], target_path=sys.argv[2], sample_size=int(sys.argv[3]))
