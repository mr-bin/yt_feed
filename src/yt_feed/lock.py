import os


def get_lock_value(lock_name):
    lock_file_path = os.path.join(os.environ['LOCK_PATH'], lock_name)

    last_ts = 0
    if os.path.exists(lock_file_path):
        with open(lock_file_path) as f:
            last_ts = f.read()
        if last_ts:
            last_ts = int(last_ts)

    return last_ts


def set_lock_value(lock_name, value):
    lock_file_path = os.path.join(os.environ['LOCK_PATH'], lock_name)
    with open(lock_file_path, 'w') as f:
        f.write(str(value))
