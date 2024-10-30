import argparse
import json
import logging.config
import re
import sys
import textwrap

from human_eval.data import read_problems
from openai import OpenAI
from tqdm import tqdm


class Eval:
    def __init__(self, args):
        self.args = args
        self.logger = get_logger()
        self.client = OpenAI(base_url=self.args.api_url, api_key="ollama")
        self.mermaids = self.read_mermaids() if self.args.mermaid_optimize else None
        self.problems = read_problems()

    @staticmethod
    def extract_code_from_completion(text: str, entry_point: str):
        # 正则表达式匹配代码块
        code_block_pattern = re.compile(
            rf"```(?:[Pp]ython\n)?.*?def\s+{entry_point}.*?:\n(.*?)\n```", re.DOTALL
        )
        code_block = code_block_pattern.search(text)
        if code_block is None:
            code_block_pattern = re.compile(
                rf"def\s+{entry_point}.*?:\n(.*?)(?:\n(?!\n*(?:  |\t))|$)", re.DOTALL
            )
            code_block = code_block_pattern.search(text)
        if code_block is None:
            code_block_pattern = re.compile(
                r"def.*?:\n(.*?)(?:\n(?!\n*(?:  |\t))|$)", re.DOTALL
            )
            code_block = code_block_pattern.search(text)

        if code_block is not None:
            return code_block.group(1)

        # if no code block is found, assume the LM is simply filling the code
        return textwrap.indent(text, " " * 4)

    def read_mermaids(self):
        return {task["task_id"]: task for task in self.stream_mermaids()}

    def stream_mermaids(self):
        with open(self.args.mermaid_file, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)

    def generate_completion(self, messages):
        completion = self.client.chat.completions.create(
            model=self.args.model,
            messages=messages,
            temperature=self.args.temperature,
            top_p=self.args.top_p,
        )
        return completion.choices[0].message.content

    def generate_completion_baseline(self, problem):
        messages = [
            {
                "role": "system",
                "content": "You're a very experienced Python programmer.",
            },
            {
                "role": "user",
                "content": "Write code in Python that meets the problem following. Ensure that the code you generate is "
                "accurate and valid and does not come with test cases.Remember, do not need to explain the code you wrote.",
            },
            {"role": "user", "content": problem["prompt"]},
        ]
        return self.generate_completion(messages)

    def generate_completion_optimize(self, problem, mermaid):
        messages = [
            {
                "role": "system",
                "content": "You're a very experienced Python programmer.",
            },
            {
                "role": "user",
                "content": "Write code in Python to solve the following problem and I will give the flowchart syntax "
                "for the following problem. Ensure that the code you generate is accurate and valid and "
                "does not come with test cases.Remember, do not need to explain the code you wrote.",
            },
            {"role": "user", "content": problem["prompt"]},
            {"role": "user", "content": mermaid["mermaid"]},
        ]
        return self.generate_completion(messages)

    def completion(self, task_id):
        if self.args.mermaid_optimize:
            completion = self.generate_completion_optimize(
                self.problems[task_id], self.mermaids[task_id]
            )
        else:
            completion = self.generate_completion_baseline(self.problems[task_id])

        return self.extract_code_from_completion(
            completion, self.problems[task_id]["entry_point"]
        )

    def evaluate(self):
        with open(self.args.output_file, "wb") as fp:
            for task_id in tqdm(self.problems):
                for _ in range(self.args.k):
                    task = dict(
                        task_id=task_id,
                        completion=self.completion(task_id),
                    )
                    self.logger.info(f"processing task {task_id}...")
                    fp.write((json.dumps(task) + "\n").encode("utf-8"))


def get_logger():
    logging.config.fileConfig("config/logging.conf")
    return logging.getLogger("main")


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
        "--k",
        type=int,
        default=1,
        help="Generate k completions for one problem,for calculate pass@k.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="samples.jsonl",
        help="The output file name, jsonl required",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    model = Eval(args)
    model.evaluate()
