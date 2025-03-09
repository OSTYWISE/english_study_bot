from pydantic import BaseModel, Field


class TaskOutput(BaseModel):
    question_or_task: str = Field(description="Вопрос или задача, которую должен решить ученик")
    format: str = Field(description="Формат, в котором ученик должен ответить")
    correct_answer: str = Field(description="Правильно ответ на вопрос или задачу")

# class EdgeOutput(BaseModel):
#     causality_fact_list: list[int] = Field(
#         description="A list of 0s and 1s, where 1 means that A has causal impact on B and 0 otherwise"
#     )

# class DagOutput(BaseModel):
#     target: str = Field(description="The list of variables that are dependent of target variable")
#     treatment: str = Field(description="The list of variable that are dependent of treatment variable")
#     variables: dict[str, list] = Field(
#         description="Dictionary with varaibles names in the keys and the list of other varaibles that are causally dependent from the current one as values"
#     )