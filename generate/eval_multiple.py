import gzip
import json
import os.path

import datasets
from tqdm import tqdm

from generate.eval import Eval

DATASET_REVISION = "8a4cb75204eb3d5855a81778db6b95bfc80c9136"


class ME(Eval):
    def __init__(
        self,
        api_url,
        model,
        language,
        mermaid_optimize,
        mermaid_file,
        temperature,
        top_p,
        max_tokens,
        k,
        output_folder,
    ):
        super().__init__(
            api_url,
            model,
            language,
            mermaid_optimize,
            mermaid_file,
            temperature,
            top_p,
            max_tokens,
            k,
            output_folder,
        )
        if mermaid_optimize:
            self.folder_path = os.path.join(
                self.output_folder,
                f"MultiPL-E_{self.language}_mermaid_optimize_{self.time}",
            )
        else:
            self.folder_path = os.path.join(
                self.output_folder, f"MultiPL-E_{self.language}_{self.time}"
            )
        os.makedirs(self.folder_path, exist_ok=True)
        self.problems = self.load_problems()

    def load_problems(self):
        multiple_language_switcher = {"Java": "java", "Cpp": "cpp"}
        dataset_language = multiple_language_switcher.get(self.language, self.language)
        problems = datasets.load_dataset(
            "nuprl/MultiPL-E",
            f"humaneval-{dataset_language}",
            revision=DATASET_REVISION,
            split="test",
        )
        return problems

    @staticmethod
    def parse_task_id(name: str):
        task_number = name.split("_")[1]
        return f"HumanEval/{task_number}"

    def process_baseline(self):
        for problem in tqdm(self.problems):
            with gzip.open(
                os.path.join(self.folder_path, f"{problem['name']}.json.gz"), "wb"
            ) as fp:
                completions = []
                for _ in range(self.k):
                    origin_code = self.generator(
                        self.client,
                        problem,
                        self.language,
                        self.model,
                        self.temperature,
                        self.top_p,
                    )
                    filtered_code = self.extractor(origin_code, problem["name"])
                    completions.append(filtered_code)
                    self.record_origin_extracted(
                        dict(
                            task_id=problem["name"],
                            origin=origin_code,
                            completion=filtered_code,
                        )
                    )
                task = dict(
                    name=problem["name"],
                    language=problem["language"],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    prompt=problem["prompt"],
                    tests=problem["tests"],
                    completions=completions,
                    stop_tokens=problem["stop_tokens"],
                )
                self.logger.info("Processing task: {}", problem["name"])
                fp.write((json.dumps(task) + "\n").encode("utf-8"))

    def process_mermaid(self):
        for problem in tqdm(self.problems):
            with gzip.open(
                os.path.join(self.folder_path, f"{problem['name']}.json.gz"), "wb"
            ) as fp:
                completions = []
                for _ in range(self.k):
                    origin_code = self.generator(
                        self.client,
                        problem,
                        self.language,
                        self.mermaids[self.parse_task_id(problem["name"])],
                        self.model,
                        self.temperature,
                        self.top_p,
                    )
                    filtered_code = self.extractor(origin_code, problem["name"])
                    completions.append(filtered_code)
                    self.record_origin_extracted(
                        dict(
                            task_id=problem["name"],
                            origin=origin_code,
                            completion=filtered_code,
                        )
                    )

                task = dict(
                    name=problem["name"],
                    language=problem["language"],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    prompt=problem["prompt"],
                    tests=problem["tests"],
                    completions=completions,
                    stop_tokens=problem["stop_tokens"],
                )
                self.logger.info("Processing task: {}", problem["name"])
                fp.write((json.dumps(task) + "\n").encode("utf-8"))
