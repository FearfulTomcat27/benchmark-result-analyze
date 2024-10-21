import argparse
import os

from analyze.humaneval import HumanEval
from analyze.multiple import MultiPLE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--batch", type=int, required=True, help="Batch size")

    parser.add_argument(
        "--benchmark", type=str, required=True, help="Benchmark, humaneval or multiple"
    )

    parser.add_argument("--input", type=str, required=True, help="Input file of folder")

    parser.add_argument("--output-dir", type=str, help="Output dir", default="output")

    args = parser.parse_args()

    valid_args(args)

    return args


def valid_args(args):
    assert args.batch > 0, "Batch size should be greater than 0"

    assert (
        args.benchmark == "humaneval" or args.benchmark == "multiple"
    ), "Benchmark should be humaneval or multiple"

    if args.benchmark == "humaneval":
        assert args.input.endswith(".jsonl") or args.input.endswith(
            ".jsonl_results.jsonl"
        ), "Input file should be a jsonl file"
    else:
        assert os.path.isdir(args.input), "Input should be a folder"

    assert os.path.isdir(args.output_dir), "Output dir should be a folder"


def main():

    args = parse_args()

    result = (
        HumanEval(args.batch, args.input, args.output_dir)
        if args.benchmark == "humaneval"
        else MultiPLE(args.batch, args.input, args.output_dir)
    )

    result.generate_output()


if __name__ == "__main__":
    main()
