import json
import os.path

from human_eval.data import read_problems
from tqdm import tqdm

from generate.eval import Eval


class HE(Eval):
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

        self.problems = read_problems()

    def process_baseline(self):
        with open(os.path.join(self.output_folder, "samples.jsonl"), "wb") as fp:
            for task_id in tqdm(self.problems):
                for _ in range(self.k):
                    origin_code = self.generator(
                        self.client,
                        self.problems[task_id],
                        self.language,
                        self.model,
                        self.temperature,
                        self.top_p,
                    )
                    filtered_code = self.extractor(
                        origin_code,
                        self.problems[task_id]["entry_point"],
                    )
                    self.diff.append(
                        dict(
                            task_id=task_id,
                            origin=origin_code,
                            completion=filtered_code,
                        )
                    )

                    task = dict(
                        task_id=task_id,
                        completion=filtered_code,
                    )
                    self.logger.info("Processing task: {}", task_id)
                    fp.write((json.dumps(task) + "\n").encode("utf-8"))

        self.record_origin_extracted()

    def process_mermaid(self):
        with open(os.path.join(self.output_folder, "samples.jsonl"), "wb") as fp:
            for task_id in tqdm(self.problems):
                for _ in range(self.k):
                    origin_code = self.generator(
                        self.client,
                        self.problems[task_id],
                        self.language,
                        self.mermaids[task_id],
                        self.model,
                        self.temperature,
                        self.top_p,
                    )
                    filtered_code = self.extractor(
                        origin_code,
                        self.problems[task_id]["entry_point"],
                    )
                    self.diff.append(
                        dict(
                            task_id=task_id,
                            origin=origin_code,
                            completion=filtered_code,
                        )
                    )
                    task = dict(
                        task_id=task_id,
                        completion=filtered_code,
                    )
                    self.logger.info("Processing task: {}", task_id)
                    fp.write((json.dumps(task) + "\n").encode("utf-8"))

        self.record_origin_extracted()
