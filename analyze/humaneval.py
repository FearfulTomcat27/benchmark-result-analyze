import json

from .result import Result


class HumanEval(Result):
    def __init__(self, batch: int, file_path: str, output_path: str):
        super().__init__(output_path)
        self.file_path = file_path
        self.batch = batch
        self.__load_data__()

    @staticmethod
    def filter_duplicates(data):
        seen = {}
        filtered_data = []
        for item in data:
            task_id = item["task_id"]
            if task_id not in seen:
                seen[task_id] = True
                filtered_data.append(item)
        return filtered_data

    def __load_data__(self) -> None:
        data = [json.loads(line) for line in open(self.file_path, "r")]
        self.problems = len(self.filter_duplicates(data))
        self.data = [item for item in data if item["passed"] is False]
        self.fail = len(self.data)
        self.params = {"batch": self.batch, "language": "python"}
        self.success = self.problems * self.batch - self.fail
        self.passk = {"pass@1": self.success / (self.success + self.fail)}

    def generate_output(self) -> None:
        task_id_record = self.data[0]["task_id"]
        result = []
        task = {"task_id": task_id_record, "fail_number": 0, "failed": []}

        for item in self.data:
            if item["task_id"] != task_id_record:
                task["fail_number"] = len(task["failed"])
                result.append(task)
                task_id_record = item["task_id"]
                task = {"task_id": task_id_record, "fail_number": 0, "failed": []}

            del item["task_id"]
            del item["passed"]
            if item not in task["failed"]:
                task["failed"].append(item)

        self.formatted_data = result

        self.write_output()
