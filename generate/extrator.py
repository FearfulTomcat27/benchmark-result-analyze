import re
import textwrap

from case_convert import camel_case

from common.logger import get_logger

logger = get_logger()


def __get_entry_point_from_multiple__(task_id: str):
    function_name = re.sub(r"HumanEval_\d+_", "", task_id)
    return camel_case(function_name)


def extract_python_code(text, entry_point):
    code_block_pattern = re.compile(
        rf"```(?:[Pp]ython\n)?.*?def\s+{entry_point}.*?:\n(.*?)\n```", re.DOTALL
    )
    code_block = code_block_pattern.search(text)
    if code_block is None:
        logger.info("Trying to extract the code for the 2nd time...")
        code_block_pattern = re.compile(
            rf"def\s+{entry_point}.*?:\n(.*?)(?:\n(?!\n*(?:  |\t))|$)", re.DOTALL
        )
        code_block = code_block_pattern.search(text)
    if code_block is None:
        logger.info("Trying to extract the code for the 3rd time...")
        code_block_pattern = re.compile(
            r"def.*?:\n(.*?)(?:\n(?!\n*(?:  |\t))|$)", re.DOTALL
        )
        code_block = code_block_pattern.search(text)

    if code_block is None:
        logger.info("Trying to extract the code for the 4th time...")
        code_block_pattern = re.compile(r"```(?:[Pp]ython\n)?(.*?)```", re.DOTALL)
        code_block = code_block_pattern.search(text)

    if code_block is not None:
        result = code_block.group(1)
        return result

    # if no code block is found, assume the LM is simply filling the code
    logger.error(f"Extract code failed,return origin text:{text}")
    return textwrap.indent(text, " " * 4)


# def extract_java_code(text, task_id):
#     entry_point = __get_entry_point_from_multiple__(task_id)
#     logger.info("Trying to extract the code for the 1st time...")
#     code_block_pattern = re.compile(
#         rf"```(?:[Jj]ava\n)?.*?public static.*?{entry_point}.*?{{\n(.*?)\n    }}\n.*?```",
#         re.DOTALL,
#     )
#     code_block = code_block_pattern.search(text)
#     if code_block is None:
#         logger.info("Trying to extract the code for the 2nd time...")
#         code_block_pattern = re.compile(
#             rf"public static.*?{entry_point}.*?{{\n(.*?)\n    }}\n", re.DOTALL
#         )
#         code_block = code_block_pattern.search(text)
#
#     if code_block is None:
#         logger.info("Trying to extract the code for the 3rd time...")
#         code_block_pattern = re.compile(
#             r"public static (?!void main\(String\[] args\) \{\n).*?\{\n(.*?)\n {4}\}\n",
#             re.DOTALL,
#         )
#         code_block = code_block_pattern.search(text)
#
#     if code_block is None:
#         logger.info("Trying to extract the code for the 4th time...")
#         code_block_pattern = re.compile(
#             r"```(?:[Jj]ava\n)?(.*?)(?:    \}\n)?```", re.DOTALL
#         )
#         code_block = code_block_pattern.search(text)
#
#     if code_block is not None:
#         result = code_block.group(1)
#         return result
#
#     logger.error(f"Extract code failed,return origin text:{text}")
#     return textwrap.indent(text, " " * 4)


def __count_function__(text):
    # 去掉 main 函数
    function_pattern = (
        r"\b(public|protected|private|static|\s)\s+.*?\s+.*?\s*\([^)]*\)\s*\{"
    )
    functions = re.findall(function_pattern, text, re.DOTALL)
    return len(functions)


def extract_java_code(text, entry_point):
    entry_point = __get_entry_point_from_multiple__(entry_point)
    main_block_pattern = r"public static void main\(String\[\] args\) {.*?    \}"
    text = re.sub(main_block_pattern, "", text, flags=re.DOTALL)

    function_num = __count_function__(text)

    if function_num == 1:
        code_pattern = re.compile(
            rf"```(?:[Jj]ava\n)?.*?public static.*?{entry_point}.*?{{\n(.*?)\n    }}\n.*?```",
            re.DOTALL,
        )
        code_block = code_pattern.search(text)
    else:
        code_pattern = re.compile(
            rf"```(?:[Jj]ava\n)?.*?public static.*?{entry_point}.*?{{\n(.*)\n    }}\n.*?```",
            re.DOTALL,
        )
        code_block = code_pattern.search(text)

    if code_block is None:
        code_pattern = re.compile(
            r"```[Jj]ava\n(.*?)(\n    }\n|\n    }\n}\n)?```", re.DOTALL
        )
        code_block = code_pattern.search(text)

    if code_block is not None:
        return code_block.group(1)

    return textwrap.indent(text, " " * 4)


def extract_cpp_code(text, entry_point):
    entry_point = re.sub(r"HumanEval_\d+_", "", entry_point)
    code_pattern = re.compile(
        rf"```(?:[Cc]pp\n)?.*?{entry_point}\(.*?\) {{\n(.*?)}}\n```", re.DOTALL
    )
    code_block = code_pattern.search(text)

    if code_block is None:
        code_pattern = re.compile(r"```(?:[Cc]pp\n)?(.*?)\n\}\n```", re.DOTALL)
        code_block = code_pattern.search(text)

    if code_block is not None:
        return code_block.group(1)

    raise ValueError("Code block not found")


switcher = {
    "Python": extract_python_code,
    "python": extract_python_code,
    "Java": extract_java_code,
    "java": extract_java_code,
    "Cpp": extract_cpp_code,
    "cpp": extract_cpp_code,
}


def get_extractor(language):
    return switcher.get(language, extract_python_code)
