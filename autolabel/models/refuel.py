from typing import List, Optional
import requests
import json
from langchain.schema import LLMResult, Generation
from botocore.config import Config

from autolabel.models import BaseModel
from autolabel.configs import ModelConfig


class RefuelLLM(BaseModel):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)
        # populate model name
        # This is unused today, but in the future could
        # be used to decide which refuel model is queried
        self.model_name = config.get_model_name()

        # initialize runtime
        config = Config(retries={"max_attempts": 10, "mode": "standard"})
        self.BASE_API = "https://api.refuel.ai/llm"

    def label(self, prompts: List[str]) -> LLMResult:
        try:
            generations = []
            for prompt in prompts:
                payload = json.dumps(
                    {"model_input": prompt, "task": "generate"}
                ).encode("utf-8")
                response = requests.post(self.BASE_API, data=payload)
                generations.append([Generation(text=response.text.strip('"'))])
            return LLMResult(generations=generations)
        except Exception as e:
            print(f"Error generating from LLM: {e}, returning empty result")
            generations = [[Generation(text="")] for _ in prompts]
            return LLMResult(generations=generations)

    def get_cost(self, prompt: str, label: Optional[str] = "") -> float:
        return 0
