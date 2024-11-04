import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    return parser.parse_args()


def stream_read_jsonl(file_path):
    with open(file_path, "r") as fp:
        for line in fp:
            if any(not x.isspace() for x in line):
                yield json.loads(line)


def main(args):
    data = list(stream_read_jsonl(args.input))
    with open(args.output, "wb") as fp:
        fp.write(json.dumps(data).encode("utf-8"))


if __name__ == "__main__":
    args = parse_args()
    main(args)
