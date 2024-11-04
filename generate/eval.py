import json
import os
import time

from openai import OpenAI

from common.logger import get_logger
from data.data import read_mermaids
from generate.completion import (
    generate_completion_mermaid,
    generate_completion_baseline,
)
from generate.extrator import get_extractor


class Eval(object):
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

        self.api_url = api_url
        self.model = model
        self.language = language
        self.mermaid_optimize = mermaid_optimize
        self.mermaid_file = mermaid_file
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.k = k
        self.output_folder = output_folder
        self.mermaids = (
            read_mermaids(self.mermaid_file) if self.mermaid_optimize else None
        )
        self.client = OpenAI(base_url=self.api_url, api_key="ollama")
        self.generator = (
            generate_completion_mermaid
            if self.mermaid_optimize
            else generate_completion_baseline
        )
        self.logger = get_logger()
        self.extractor = get_extractor(self.language)
        self.time = time.time_ns()
        os.makedirs(self.output_folder, exist_ok=True)

    def process_baseline(self):
        pass

    def process_mermaid(self):
        pass

    def record_origin_extracted(self, data):
        with open(
            os.path.join(self.output_folder, f"diff_{self.time}.jsonl"), "ab"
        ) as fp:
            fp.write((json.dumps(data) + "\n").encode("utf-8"))

    def evaluate(self):
        if self.mermaid_optimize:
            self.process_mermaid()
        else:
            self.process_baseline()
