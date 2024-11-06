import re

import datasets

humaneval_size = 164
humaneval = [i for i in range(164)]

languages = ["cpp", "cs", "go", "java", "js"]


def get_task_number(task_name: str) -> int:
    pattern = re.compile(r"HumanEval_(\d+)_.*")
    task_number = pattern.match(task_name).group(1)
    return int(task_number)


def humaneval_diff(language: str) -> tuple:
    dataset = datasets.load_dataset(
        "nuprl/MultiPL-E", f"humaneval-{language}", split="test"
    )
    size = dataset.num_rows
    result = list(
        set(humaneval) - set([get_task_number(item["name"]) for item in dataset])
    )
    result.sort()
    return size, result


def main():
    for language in languages:
        print("Language:", language)
        print(humaneval_diff(language))


if __name__ == "__main__":
    main()
