import json
import os
import time


class Result:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.data = []
        self.formatted_data = []
        self.problems = 0
        self.success = 0
        self.fail = 0
        self.params = {}
        self.passk = {}

    def __load_data__(self) -> None:
        pass

    def get_result(self) -> list:
        return self.data

    def get_problem_numbers(self) -> int:
        return self.problems

    def generate_output(self) -> None:
        pass

    def write_output(self) -> None:
        result = {
            "name": f"HumanEval-{self.params['language']}",
            "problems": self.problems,
            "success": self.success,
            "fail": self.fail,
            "passk": self.passk,
            "params": self.params,
            "failed": self.formatted_data,
        }
        output_file = os.path.join(
            self.output_path, f"{result['name']}_{time.time_ns()}.json"
        )
        with open(output_file, "w+") as f:
            f.write(json.dumps(result, indent=2))
            print("文件已保存至", output_file)
