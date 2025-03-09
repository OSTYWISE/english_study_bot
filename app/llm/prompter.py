from typing import List, Optional


class Prompter:
    def __init__(self):
        self.system_prompt = ""

    def update_system_prompt(self, system_prompt_path: str) -> str:
        with open(system_prompt_path, 'r') as file:
            self.system_prompt = file.read()

    def task_generation_prompt(self,
            task_generation_prompt_path: str,
            topic: str,
            subtopic: str, 
            task_type: str, 
            difficulty: str,
            shots: Optional[List[str]] = None) -> str:
        with open(task_generation_prompt_path, 'r') as file:
            node_prompt = file.read().format(
                topic=topic, subtopic=subtopic,
                task_type=task_type, difficulty=difficulty
                )
        if shots:
            node_prompt += '\nCorrect examples:'
            for i, shot in enumerate(shots):
                node_prompt += '\n' + shot
        return self.system_prompt + '\n' + node_prompt

