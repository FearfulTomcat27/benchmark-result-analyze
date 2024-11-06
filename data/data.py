import json


def read_mermaids(file_path):
    return {task["task_id"]: task for task in stream_mermaids(file_path)}


def stream_mermaids(file_path):
    with open(file_path, "r") as fp:
        for line in fp:
            if any(not x.isspace() for x in line):
                yield json.loads(line)
