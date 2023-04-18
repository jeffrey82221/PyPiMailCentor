import sys
import os
from src.update_latest import UpdateController

def yeild_append(total, src_path, target_path):
    for i in range(total):
        fn = f'{src_path}/append_{i}/append.log'
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                for pkg in f:
                    yield f.strip()
        else:
            print(fn, 'does not exist')

def yeild_delete(total, src_path, target_path):
    for i in range(total):
        fn = f'{src_path}/delete_{i}/delete.log'
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                for pkg in f:
                    yield f.strip()
        else:
            print(fn, 'does not exist')

def update(total, src_path, target_path):
    controller = UpdateController(target_path)
    for pkg in yeild_delete(total, src_path):
        controller._delete_line(pkg)
        print('delete', pkg)
    print('Done Delete')
    for line in yeild_append(total, src_path):
        controller._append_line(line)
        print('append', pkg)
    print('Done Append')

if __name__ == '__main__':
    update(index=int(sys.argv[1]), src_path=str(sys.argv[2]), target_path=str(sys.argv[3]))
