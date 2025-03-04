class EduBot:
    def __init__(self):
        self.global_settings = {
            "topic": None,
            "subtopic": None,
            "difficulty": None,
            "explanation_regime": None,
        }
        self.local = None
        self.model_name = ""