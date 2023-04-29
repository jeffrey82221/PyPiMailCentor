"""
Update JSON representing the latest status of a python package

The package is listed in data/package.menu
"""
import os
import subprocess

SPLIT_PATH = "tmp"



def update_all(update, src_path, index, split_cnt=10):
    """
    Args:
      - update_func: the update function to be callback
      - index: the index to select the splitted target file
      - split_cnt: number of total parallel count
    """
    # Get total package count
    out = subprocess.check_output(["wc", "-l", src_path])
    total = int(out.decode("utf-8").split(src_path)[0])
    print(f"line count of {src_path}: {total}")
    # Create Split Path
    if not os.path.exists(SPLIT_PATH):
        os.mkdir(SPLIT_PATH)
    # Do Split
    pkg_cnt_per_file = int(total / split_cnt)
    subprocess.run(["split", "-l", str(pkg_cnt_per_file), src_path, SPLIT_PATH + "/"])
    files = sorted(os.listdir(SPLIT_PATH))
    print(f"split files: {files}")
    file = files[index]
    print(f"selected file: {file}")
    update(src_path = f"{SPLIT_PATH}/{file}")
