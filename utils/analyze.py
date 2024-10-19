import json
import time


class Analyzer:
    def __init__(self, path: str):
        self.path = path
        self.data = json.load(open(path, "r"))
        self.origin_length = len(self.data)


if __name__ == "__main__":
    print(time.time() * 1000)
