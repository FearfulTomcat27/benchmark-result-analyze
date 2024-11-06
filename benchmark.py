import argparse
import sys

from generate.eval_human import HE
from generate.eval_multiple import ME

benchmark_switcher = {
    "HumanEval": HE,
    "humaneval": HE,
    "MultiPL-E": ME,
    "multipl-e": ME,
    "default": HE,
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-url",
        type=str,
        required=True,
        help="Model api address, Recommended Http.",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name, reference model name in ollama.",
    )
    parser.add_argument(
        "--benchmark", type=str, default="HumanEval", help="BenchMark's name."
    )
    parser.add_argument(
        "--language", type=str, default="Python", help="BenchMark's language."
    )
    parser.add_argument(
        "--mermaid-optimize",
        type=bool,
        required=False,
        help="Whether use mermaid to optimize prompt",
    )
    parser.add_argument(
        "--mermaid-file",
        type=str,
        required="--mermaid-optimize" in sys.argv,
        help="The mermaid jsonl file path.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Model params for temperature.",
    )
    parser.add_argument(
        "--top-p", type=float, default=0.95, help="Model params for top_p."
    )
    parser.add_argument(
        "--max-tokens", type=int, default=1024, help="Max tokens number."
    )
    parser.add_argument(
        "--k",
        type=int,
        default=1,
        help="Generate k completions for one problem,for calculate pass@k.",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default="tutorial",
        help="The output folder path",
    )
    args = parser.parse_args()
    validate_args(args)
    return args


def validate_args(args):
    if args.benchmark == "HumanEval":
        assert (
            args.language == "Python"
        ), "HumanEval benchmark's language must be Python."
        assert args.output_file.endswith(
            ".jsonl"
        ), "The output file name must be ends with .jsonl."
    elif args.benchmark == "MultiPL-E":
        assert (
            args.language != "Python"
        ), "MultiPL-E benchmark's language can not be Python, you can use Java or Cpp only."


def get_benchmark_instance(benchmark, params):
    del params["benchmark"]
    cn = benchmark_switcher.get(benchmark, benchmark_switcher["default"])
    ci = cn(**params)
    return ci


if __name__ == "__main__":
    args = parse_args()
    params = vars(args)

    benchmark = get_benchmark_instance(args.benchmark, params)

    benchmark.evaluate()
