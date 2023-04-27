import tqdm

def loop_over(func):
    def do_etl(src_path):
        with open(src_path, "r") as f:
            pkgs = list(map(lambda x: x.strip(), f))
            for pkg in tqdm.tqdm(pkgs, desc=f"{pkgs[0]}~{pkgs[-1]}"):
                func(pkg)
    return do_etl