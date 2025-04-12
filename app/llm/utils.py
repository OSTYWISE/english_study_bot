import re
import json


def extract_questionary(text_result: str) -> dict:
    text_result = text_result.replace("```", "")
    def parse_options(options_str: str) -> list[str]:
        options = re.split(r'\n[a-d]\) ', options_str.strip())
        return [opt.strip() for opt in options if opt]

    questionary = json.loads(text_result)
    answer_mapping = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    option_replace_mapping = {"a) ": "", "a)": "", 'b) ': "", "b)": "", 'c) ': "", "c)": "", 'd) ': "", "d)": ""}
    questionary_list = []
    for key, value in questionary.items():
        value['options'] = parse_options(value['options'])
        value['correct_answer'] = answer_mapping[value['correct_answer']]
        for i, val in enumerate(value['options']):
            for pair in option_replace_mapping:
                val = val.replace(pair, "")
            value['options'][i] = val
        questionary_list.append(value)
    return questionary_list


def get_questionary_system_prompt() -> str:
    system_prompt = f"You are the teacher of English course in university. " + \
        "You have literary text below. Your task is to check students knowledge of this literature. " + \
        "In order to do this you create questionaries with multiple choice with 4 options to choose."
    return system_prompt


def create_questionary_prompt(litwork_text: str) -> str:
    options_template = "a) Option 1\nb) Option 2\nc) Option 3\nd) Option 4\n"
    questionary_prompt = f"""Create a 5-question test with multiple choice with 4 options to choose.
The test should check the knowledge of the literary work's plot.
The test should be in English.
Literary work text: {litwork_text}

In answer to this prompt you should return only 5 questions with choice options and correct answers and nothing else.
Format of answer as JSON-string:
{{
    "question1": {{
        "question": "Question 1",
        "options": {options_template},
        "correct_answer": "a"
    }},
    "question2": {{
        "question": "Question 2",
        "options": {options_template},
        "correct_answer": "b"
    }},
    "question3": {{
        "question": "   Question 3",
        "options": {options_template},
        "correct_answer": "c"
    }},
    "question4": {{
        "question": "Question 4",
        "options": {options_template},
        "correct_answer": "a"
    }},
    "question5": {{
        "question": "Question 5",
        "options": {options_template},
        "correct_answer": "d"
    }}
}}
"""
    return questionary_prompt
