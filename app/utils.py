from app.database.requests import get_student


async def has_litwork(tg_id: int) -> bool:
    student = await get_student(tg_id)
    if not student:
        return False
    return True


def question_to_text(question: dict) -> str:
    return f"{question['question']}\n{show_answer_options(question['options'])}"


def show_answer_options(answer_options: list[str]) -> str:
    """
    Shows the answer options in a readable format.
    """
    return '\n'.join(
        [f"{i+1}. {option}" for i, option in enumerate(answer_options)]
        )


def answer_format_check(answer: str, task_type: str) -> bool:
    """
    Checks if the answer is formatted correctly for the given task type.
    """
    answer = answer.strip()
    if task_type == 'да/нет':
        return answer in ['да', 'нет']
    elif task_type == 'выбор единственного ответа':
        return (answer.isdigit() and len(answer) == 1)
    elif task_type == 'выбор нескольких верных ответов':
        answers = answer.split(', ')
        for ans in answers:
            if not (ans.isdigit() and len(ans) == 1):
                return False
        return True
    return True


def preprocess_generated_task(text_result: str, task: str, answer_options: str, answer: str, solution: str) -> tuple[str, str, str, str]:
    """
    Preprocesses the generated task to database correct format.
    """
    return task, answer_options, answer, solution
