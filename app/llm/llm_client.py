import os
import aiohttp
from typing import Dict, Tuple, Optional, List
from dotenv import load_dotenv

from app.llm.utils import extract_questionary, get_questionary_system_prompt, \
    create_questionary_prompt

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def make_api_call(
    prompt: str,
    system_prompt: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    model_name: str = "gpt-4",
    temperature: float = 1,
    max_tokens: Optional[int] = None,
    structured_flg: bool = False,
    functions: Optional[List[Dict]] = None
) -> Tuple[str, Dict[str, int]]:
    """Make an API call to OpenAI's chat completion endpoint.

    Args:
        prompt: The user's prompt
        system_prompt: Optional system prompt
        model_name: Model to use (default: gpt-4)
        temperature: Sampling temperature (default: 1)
        max_tokens: Max tokens to generate
        structured_flg: Whether to use function calling
        functions: List of function definitions for structured output

    Returns:
        Tuple of (response text, usage statistics)
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    if messages is None:
        messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if structured_flg and functions:
        payload["functions"] = functions
        payload["function_call"] = {"name": functions[0]["name"]}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, json=payload
            ) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    msg = (
                        f"API call failed with status {response.status}: "
                        f"{error_detail}"
                    )
                    raise aiohttp.ClientError(msg)

                result = await response.json()
                usage_dict = {
                    "input_tokens": result.get('usage', {}).get(
                        'prompt_tokens', 0
                    ),
                    "output_tokens": result.get('usage', {}).get(
                        'completion_tokens', 0
                    )
                }

                if structured_flg and functions:
                    function_call = result['choices'][0]['message'].get(
                        'function_call'
                    )
                    if function_call:
                        return function_call['arguments'], usage_dict

                content = result.get('choices', [{}])[0].get(
                    'message', {}).get('content', '')
                return content, usage_dict

    except Exception as e:
        raise Exception(f"Failed to make OpenAI API call: {str(e)}")


async def generate_questionary(
        litwork_text: str,
        temperature: float = 1,
        max_tokens: int | None = None,
        raw_result: bool = False
        ):
    try:
        system_prompt = get_questionary_system_prompt()
        questionary_prompt = create_questionary_prompt(litwork_text)

        text_result, _ = await make_api_call(
            prompt=questionary_prompt,
            system_prompt=system_prompt,
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
        max_tokens: int | None = None) -> str:
    try:
        system_prompt = "You are a brilliant student that study “Drama and Theatre” advanced english course." + \
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

        result = await make_api_call(
            prompt=f"Literary work text:\n{literary_work}",
            system_prompt=system_prompt,
            messages=messages,
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
        max_tokens: int | None = None) -> str:
    try:
        # Prompt in english to create a new non-obvious thought or idea on the certain topic in context of the text of literary work
        idea_prompt = f"""Create a new non-obvious thought or idea on the certain topic in context of the text of literary work.
        Topic: {topic}
        Literary work text: {litwork_text}
        In answer to this prompt you should return only the thought or idea and explain it, without any other text.
        """
        system_prompt = "You are a very creative person, who likes to generate new ideas based on literary works"

        result, _ = await make_api_call(
            prompt=idea_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result or "Failed to generate idea."
    except Exception as e:
        return f"Error generating idea: {str(e)}"
