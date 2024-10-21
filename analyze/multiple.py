import gzip
import json
import os
import re

from .result import Result


class MultiPLE(Result):
    def __init__(self, batch: int, folder_path: str, output_path: str):
        super().__init__(output_path)
        self.folder_path = folder_path
        self.files = []
        self.batch = batch
        self.__load_data__()

    @staticmethod
    def __is_result_file__(file) -> bool:
        return bool(re.match(r"HumanEval_\d+_.*.results.json.gz", file))

    @staticmethod
    def __get_task_number__(name: str) -> int:
        pattern = re.compile(r"HumanEval_(\d+)_.*")
        task_number = pattern.match(name).group(1)
        return int(task_number)

    def __load_data_from_file__(self, file: str) -> dict:
        with gzip.open(file, "r") as f:
            data = json.load(f)

        return data

    def __load_data__(self):
        self.files = [
            file
            for file in os.listdir(self.folder_path)
            if self.__is_result_file__(file)
        ]
        self.problems = len(self.files)
        self.data = [
            self.__load_data_from_file__(os.path.join(self.folder_path, file))
            for file in self.files
        ]
        example = self.data[0]
        self.params = {
            "batch": self.batch,
            "language": example["language"],
            "temperature:": example["temperature"],
            "top_p": example["top_p"],
            "max_tokens": example["max_tokens"],
        }

    def generate_output(self) -> None:
        result = []
        for item in self.data:
            fail = 0
            failed = []
            for task in item["results"]:
                if task["status"] != "OK":
                    fail += 1
                    failed.append(
                        {
                            "completion": task["program"],
                            "result": task["stderr"],
                        }
                    )

            success = len(item["results"]) - fail
            self.success += success
            self.fail += fail
            if fail != 0:
                result.append(
                    {
                        "task_id": f"HumanEval-{self.params['language']}/{self.__get_task_number__(item['name'])}",
                        "fail": fail,
                        "failed": failed,
                    }
                )

        self.passk = {"pass@1": self.success / (self.success + self.fail)}
        self.formatted_data = result
        self.write_output()
