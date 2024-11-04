import re
import textwrap

from case_convert import camel_case

from common.logger import get_logger

logger = get_logger()


def __get_entry_point_from_multiple__(task_id: str):
    function_name = re.sub(r"HumanEval_\d+", "", task_id)
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

    if code_block is not None:
        result = code_block.group(1)
        return result

    # if no code block is found, assume the LM is simply filling the code
    logger.error(f"Extract code failed,return origin text:{text}")
    return textwrap.indent(text, " " * 4)


def extract_java_code(text, task_id):
    entry_point = __get_entry_point_from_multiple__(task_id)
    logger.info("Trying to extract the code for the 1st time...")
    code_block_pattern = re.compile(
        rf"```(?:[Jj]ava\n)?.*?public static.*?{entry_point}.*?{{\n(.*?)\n    }}\n.*?```",
        re.DOTALL,
    )
    code_block = code_block_pattern.search(text)
    if code_block is None:
        logger.info("Trying to extract the code for the 2nd time...")
        code_block_pattern = re.compile(
            rf"public static.*?{entry_point}.*?{{\n(.*?)\n    }}\n", re.DOTALL
        )
        code_block = code_block_pattern.search(text)

    if code_block is None:
        logger.info("Trying to extract the code for the 3rd time...")
        code_block_pattern = re.compile(
            r"public static (?!void main\(String\[] args\) \{\n).*?\{\n(.*?)\n {4}\}\n",
            re.DOTALL,
        )
        code_block = code_block_pattern.search(text)

    if code_block is None:
        logger.info("Trying to extract the code for the 4th time...")
        code_block_pattern = re.compile(
            r"```(?:[Jj]ava\n)?(.*?)(?:    \}\n)?```", re.DOTALL
        )
        code_block = code_block_pattern.search(text)

    if code_block is not None:
        result = code_block.group(1)
        return result

    logger.error(f"Extract code failed,return origin text:{text}")
    return textwrap.indent(text, " " * 4)


def extract_cpp_code(text, entry_point):
    return text


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
