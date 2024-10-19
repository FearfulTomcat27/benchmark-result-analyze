import argparse
import gzip
import json
import os
import re
import time


def filter_result_json(file_name: str):
    pattern = re.compile(r"HumanEval_\d+_(?:.*).results.json.gz")

    file_name = pattern.match(file_name)

    if file_name:
        return True
    else:
        return False


def get_task_number(name: str) -> int:
    pattern = re.compile(r"HumanEval_(\d+)_.*")
    task_number = pattern.match(name).group(1)
    return int(task_number)


class Result:
    def __init__(self, folder_path: str, details: bool = False):
        self.result = None
        self.folder_path = folder_path

        self.files = [
            file for file in os.listdir(self.folder_path) if filter_result_json(file)
        ]
        self.origin_length = len(self.files)
        self.details = details

    @staticmethod
    def sort_result(result: list) -> list:
        result = sorted(result, key=lambda x: get_task_number(x["name"]))
        return result

    def get_length(self) -> int:
        return self.origin_length

    def read_one_file(self, file: str):
        with gzip.open(os.path.join(self.folder_path, file), "r") as f:
            data = json.load(f)
            return self.check_file_failed(data)

    def check_file_failed(self, data: dict) -> dict:
        success = 0
        fail = 0
        failed = []
        for item in data["results"]:
            if item["status"] == "OK":
                success += 1
            else:
                fail += 1
                failed.append(
                    {
                        "stderr": item["exit_code"],
                        "exit_code": item["exit_code"],
                        "status": item["status"],
                    }
                )
        return (
            {
                "name": data["name"],
                "status": fail == 0,
                "success_number": success,
                "fail_number": fail,
                "failed": failed,
            }
            if fail != 0
            else None
        )

    def get_real_folder_path(self) -> str:
        return os.path.split(self.folder_path)[-1]

    def write_result(self, result: list):
        file = f"{self.get_real_folder_path()}_{str(time.time_ns())}"
        output_path = os.path.join(
            "../output",
            file,
        )
        with open(f"{output_path}.json", "w+") as f:
            f.write(json.dumps(result, indent=2))

    def analyze_result(self) -> None:
        result = self.sort_result(
            [
                self.read_one_file(file)
                for file in self.files
                if self.read_one_file(file)
            ]
        )
        self.write_result(result)
        self.result = result

        if self.details:
            self.get_all_fail_number()
            self.get_all_details()

    def get_all_fail_number(self) -> None:
        all_fail_result = [
            get_task_number(item["name"])
            for item in self.result
            if item["success_number"] == 0
        ]

        print(f"其中有{len(all_fail_result)}个问题在20次中没有一次通过测试测试。")
        print(f"对应的task number为：{all_fail_result}")

    def get_all_details(self) -> None:
        for item in self.result:
            print(item)

    def get_result(self):
        return self.result


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("--folder-path", type=str, required=True)
    parse.add_argument("--details", type=bool, required=False)

    args = parse.parse_args()

    result = Result(args.folder_path)

    result.analyze_result()


if __name__ == "__main__":
    main()
