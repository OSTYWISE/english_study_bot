import warnings

import hydra
# from hydra.utils import instantiate
# from omegaconf import DictConfig, OmegaConf

from src.graphs import StudentKnowledgeGraph, TopicGraph
from src.bot import EduBot
from src.recommender import BaseRecoommender

from src.llm.LLMClient import TogetherAIClient
from src.llm.LLMFormater import TaskOutput
from src.llm.prompter import Prompter
import os

# from yandex_cloud_ml_sdk.auth import APIKeyAuth

warnings.filterwarnings("ignore", category=UserWarning)

@hydra.main(version_base=None, config_path="src/configs", config_name="baseline")
def main(config):
    """
    Main script for launching bot
    Args:
        config (DictConfig): hydra experiment config.
    """
    together_client = TogetherAIClient(api_key=os.environ.get('TOGETHER_AI_API_KEY', 'No key'))
    model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
    prompter = Prompter()

    settings = {
        "topic": "Производные",
        "subtopic": "Производные от многочленов",
        "task_type": "Закрытый ответ",
        "difficulty": "Сложный",
    }
    task_prompt = prompter.task_generation_prompt("data/prompts/base_create_question.txt", *settings)
    # Generate new node for the DAG
    full_response_node, _ = together_client.generate_json_output(task_prompt, model_name, TaskOutput, debug_mode=False)
    print(full_response_node)
    return 1


if __name__ == "__main__":
    main()
