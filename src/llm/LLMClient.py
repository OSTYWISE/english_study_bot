import together
import json
import re

class TogetherAIClient:
    def __init__(self, api_key: str):
        self.client = together.Together(api_key=api_key)

    def generate_txt_response(self, prompt: str, model_name: str, max_tokens: int = 500) -> str:
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def generate_json_output(self, prompt: str, model_name: str, json_format_class, debug_mode: bool = False) -> tuple:
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
        except:
            json_output = json.loads('{"error":"some_error"}')
        return full_response, json_output
    