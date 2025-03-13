import together
import json
import re
import aiohttp
import os
from dotenv import load_dotenv
from app.llm.LLMFormater import TaskOutput

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
CATALOGUE_ID =  os.getenv("YC_CATALOGUE_ID")
IAM_TOKEN = os.getenv("IAM_TOKEN")


# class TogetherAIClient:
#     def __init__(self, api_key: str):
#         self.client = together.Together(api_key=api_key)


 # prompt should be given from config, that takes it from file
async def generate_task_with_together_ai(
        user_data, url="https://api.together.xyz/v1/chat/completions", 
        model_name="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        temperature=1, max_tokens=None) -> tuple[str]:
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
        }
    if 'prev_task' in user_data: 
        middle_prompt = f"""До этого ученик решал задачу: '{user_data.get('prev_task')}'.\n
            Сейчас нужно сгенерировать {user_data.get('change_difficulty')} по сложности задачу.\n
            """
    else:
        middle_prompt = f"У задачи должна быть {user_data['difficulty']} сложность. "
    task_prompt = f"Сгенерируй для ученика {user_data['task_type']} задачу на тему {user_data['topic']}. " + middle_prompt + \
        f"""Формат ответа должен быть следующим: {user_data['llm_regime']}.\n
        Ответ дай в формате:\n<задача>\nСгенерированная задача\n</задача>\n
        <ответ>\nОтвет на эту задачу\n</ответ>\n
        <объяснение>\nОбъяснение как решать эту задачу\n</объяснение>\n
        То есть ты должен сгенерировать контект вместо текста между псевдо html тегами"""
    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": task_prompt
            }],
        'temperature': temperature,
        'max_tokens': max_tokens
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "Failed to generate a task.")
            result = result.split("</think>")[-1].strip()
            task = result.split('<задача>')[-1].split('</задача>')[0].strip()
            answer = result.split('<ответ>')[-1].split('</ответ>')[0].strip()
            explanation = result.split('<объяснение>')[-1].split('</объяснение>')[0].strip()
            return task, answer, explanation


async def generate_task(
        user_data, temperature=0.3, max_tokens=None,
        model_specification="yandexgpt-32k/latest") -> tuple[str]:
    if 'prev_task' in user_data: 
        middle_prompt = f"""До этого ученик решал задачу: '{user_data.get('prev_task')}'.\n
            Сейчас нужно сгенерировать {user_data.get('change_difficulty')} по сложности задачу.\n
            """
    else:
        middle_prompt = f"У задачи должна быть {user_data['difficulty']} сложность. "
    task_prompt = f"Сгенерируй для ученика {user_data['task_type']} задачу на тему {user_data['topic']}. " + middle_prompt + \
        f"""Формат ответа должен быть следующим: {user_data['llm_regime']}.\n
        Ответ дай в формате:\n<задача>\nСгенерированная задача\n</задача>\n
        <ответ>\nОтвет на эту задачу\n</ответ>\n
        <объяснение>\nОбъяснение как решать эту задачу\n</объяснение>\n
        То есть ты должен сгенерировать контект вместо текста между псевдо html тегами"""
    
    messages = [
        {"role": "system", "text": "Ты профессиональный репетитор по математике, который помогает 11-класникам подготовиться к экзамену."},
        {"role": "user", "text": f"{task_prompt}"},
        ]

    payload = {
        "modelUri": f"gpt://{CATALOGUE_ID}/{model_specification}",
        "completionOptions": {
            "temperature": temperature,
            "maxTokens": max_tokens
            },
        "messages": messages
        }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {IAM_TOKEN}"
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=headers, json=payload) as response:
            result = await response.json()
            # tokens_info = result['result']['usage']  # todo() - track how many tokens was generated to calculate costs
            result = result['result']['alternatives'][0]['message']['text']
            task = result.split('<задача>')[-1].split('</задача>')[0].strip()
            answer = result.split('<ответ>')[-1].split('</ответ>')[0].strip()
            explanation = result.split('<объяснение>')[-1].split('</объяснение>')[0].strip()
            return task, answer, explanation  # rokens_info


async def generate_explanation(
        user_data, url="https://api.together.xyz/v1/chat/completions", 
        model_name="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        temperature=1, max_tokens=None) -> str:
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
        }
    explain_prompt = f"""Ты профессиональный репетитор по {user_data['topic']}.\n"
        ученик решает задачи по {user_data['topic']}. 
        Нижу я приведу задачу с решением, правильный ответ и ответ ученика. 
        Также, если уже были какие-то объяснения я их тоже приведу. 
        Твоая задача: объяснить ученику, как решить эту проблему так чтобы он понял. 
        Не повторяйся с предыдущими объяснениями.\n
        ЗАДАЧА:\n{user_data['task']}\n\n
        РЕШЕНИЕ:\n{user_data['explanations'][0]}\n\n
        ПРАВИЛЬНЫЙ ОТВЕТ: {user_data['answer']}\nОТВЕТ УЧЕНИКА: {user_data['student_answer']}\n\n
        ОБЪЯСНЕНИЯ:\n{'\n'.join([f"{i+1}: {text}" for i, text in enumerate(user_data['explanations'][1:])])}
        ТВОЕ НОВОЕ ОБЪЯСНЕНИЕ:\n"""
    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": explain_prompt
            }],
        'temperature': temperature,
        'max_tokens': max_tokens
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "Failed to generate a task.")
            result = result.split("</think>")[-1].strip()
            return result


async def generate_thoery(
        user_data, url="https://api.together.xyz/v1/chat/completions", 
        model_name="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        temperature=0.7, max_tokens=None) -> str:
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
        }
    if 'thoery' in user_data: 
        prev_theory_block = f"ПРОШЛЫЙ РАЗБОР ТЕМЫ:\n{user_data['theory']}\n\n"
    else:
        prev_theory_block = ""

    thoery_prompt = f"""Ты профессиональный репетитор по {user_data['topic']}.\n
        Ученик решает задачи по {user_data['topic']}. 
        Нижу я приведу задачу с решением. 
        Также ученик возможно уже получал разбор этой темы. Я его тоже приведу. 
        Не повторяйся с тем, что было рассказано раньше, либо старайся объяснить это подругому.\n
        Твоя задача: объяснить ученику как решаются задачи такого типа. 
        Не бойся приводить примеры для лучшего понимания этой темы учеником.\n
        ЗАДАЧА:\n{user_data['task']}\n\n
        РЕШЕНИЕ:\n{user_data['explanations'][0]}\n\n + {prev_theory_block}
        ТВОЕ ОБЪЯСНЕНИЕ ТЕМЫ:\n"""
    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": thoery_prompt
            }],
        'temperature': temperature,
        'max_tokens': max_tokens
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "Failed to generate a task.")
            result = result.split("</think>")[-1].strip()
            return result


def generate_json_output(
        self, prompt: str, model_name: str, json_format_class: TaskOutput,
        debug_mode: bool = False) -> tuple:
    """WARNING: This is not asynconious function yet"""
    extract = self.client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "The following is user's request. Only answer in JSON.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        model=model_name,
        response_format={
            "type": "json_object",
            "schema": json_format_class.model_json_schema(),
        },
    )
    if debug_mode:
        return extract, json.loads('{"empty_field":""}')

    full_response = extract.choices[0].message.content
    try:
        clean_response = re.sub(r"<think>.*?</think>\s*", "", full_response, flags=re.DOTALL)
        json_output = json.loads(clean_response)
    except Exception:
        json_output = json.loads('{"error":"some_error"}')
    return full_response, json_output
    