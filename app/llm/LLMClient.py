import os
import re
import aiohttp
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

from app.llm.utils import extract_questionary, get_questionary_system_prompt, create_questionary_prompt


load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
CATALOGUE_ID = os.getenv("YC_CATALOGUE_ID")
IAM_TOKEN = os.getenv("IAM_TOKEN")


# class TogetherAIClient:
#     def __init__(self, api_key: str):
#         self.client = together.Together(api_key=api_key)


 # prompts should be given from config, that takes it from file
model_specifications_to_use = [
    # YandexGPT Lite
    'yandexgpt-lite/deprecated', 'yandexgpt-lite/latest', 'yandexgpt-lite/rc',
    # YandexGPT Pro
    'yandexgpt/deprecated', 'yandexgpt/latest', 'yandexgpt/rc',  # gpt 5 
    # YandexGPT Pro 32k
    'yandexgpt-32k/deprecated', 'yandexgpt-32k/latest', 'yandexgpt/rc'  # gpt 5
]


async def make_yandex_api_call(
    messages: list[Dict[str, str]],
    model_specification: str = "yandexgpt/rc",
    temperature: float = 1,
    max_tokens: int | None = None
) -> str:
    """Helper function to make Yandex API calls with proper error handling."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {IAM_TOKEN}"
    }
    
    payload = {
        "modelUri": f"gpt://{CATALOGUE_ID}/{model_specification}",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": messages
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"API call failed with status {response.status}")
                result = await response.json()
                return result.get('result', {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
    except Exception as e:
        raise Exception(f"Failed to make API call: {str(e)}")


async def generate_questionary(
        litwork_text: str,
        temperature: float = 1,
        max_tokens: int | None = None,
        model_specification: str = "yandexgpt/rc",
        raw_result: bool = False
        ):
    try:
        system_prompt = get_questionary_system_prompt()
        questionary_prompt = create_questionary_prompt(litwork_text)

        messages = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": questionary_prompt},
        ]

        text_result = await make_yandex_api_call(
            messages=messages,
            model_specification=model_specification,
            temperature=temperature,
            max_tokens=max_tokens
        )
        print(f"Generated text: {text_result}")

        if raw_result:
            return text_result

        questionary = extract_questionary(text_result)
        print(questionary)
        return questionary
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"


async def discuss_litwork(
        discussion_messages: list[dict[str, str]],
        literary_work: str,
        temperature: float = 0.5,
        max_tokens: int | None = None,
        model_specification: str = "yandexgpt/rc") -> str:
    try:
        system_prompt = "You are a brilliant student that study “Fantastic in World Literature” advanced english course." + \
            "You discuss the text of the literary work, that is provided below, with your classmate. " + \
            "You want to help him to analyze the text, the realize the real meaning author put to his work. " + \
            "You may use your background knowledge about the work and literary work and provided author if needed. " + \
            "Continue to communicate with him for help both understand the text better." + \
            "Be short and concise in your answers. Your answer should be in average 1-2 sentences. If needed you can use up to 4 sentences."
        messages = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": f"Literary work text:\n{literary_work}"}
        ]
        messages.extend(discussion_messages)

        result = await make_yandex_api_call(
            messages=messages,
            model_specification=model_specification,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result
    except Exception as e:
        return f"Error generating new message to discussion: {str(e)}"


async def generate_idea(
        topic: str,
        litwork_text: str,
        temperature: float = 0.5,
        max_tokens: int | None = None,
        model_specification: str = "yandexgpt/rc") -> str:
    try:
        # Prompt in english to create a new non-obvious thought or idea on the certain topic in context of the text of literary work
        idea_prompt = f"""Create a new non-obvious thought or idea on the certain topic in context of the text of literary work.
        Topic: {topic}
        Literary work text: {litwork_text}
        In answer to this prompt you should return only the thought or idea and explain it, without any other text.
        """
        messages = [
            {"role": "system", "text": f"You are a very creative person, who likes to generate new ideas based on literary works"},
            {"role": "user", "text": idea_prompt}
        ]

        result = await make_yandex_api_call(
            messages=messages,
            model_specification=model_specification,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result or "Failed to generate idea."
    except Exception as e:
        return f"Error generating idea: {str(e)}"
