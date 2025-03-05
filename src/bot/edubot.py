class EduBot:
    def __init__(self):
        self.global_settings = {
            "topic": None,
            "subtopic": None,
            "task_type": None,
            "difficulty": None,
            "explanation_regime": None,
        }
        self.local_settings = {
            "topic": None,
            "subtopic": None,
            "task_type": None,
            "difficulty": None,
            "explanation_regime": None,
        }
        self.model_name = ""
        self.prompter = ""

    def create_question(self,
            topic: str|None = None,
            subtopic: str|None = None,
            task_type: str|None = None,
            dificulty: str|None = None,
            ) -> tuple:
        return "generated response"
    
    def change_setting(self, field_name: str, new_val: str, global_settings_flg: bool = True):
        if global_settings_flg:
            self.global_settings[field_name] = new_val
        else:
            self.local_settings[field_name] = new_val

    def create_base_prompt(self) -> str:
        prompt = "some_prompt"
        return prompt