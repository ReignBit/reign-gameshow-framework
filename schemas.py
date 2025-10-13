from pydantic import BaseModel

class QuestionBase(BaseModel):
    title: str
    ans_a: str
    ans_b: str
    ans_c: str
    ans_d: str
    factoid: str = ""
    correct_ans: int = -1
    seen: bool = False

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int

    class Config:
        orm_mode = True
