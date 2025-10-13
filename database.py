from sqlalchemy import create_engine, Column, Integer, String, Boolean, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (CheckConstraint("correct_ans BETWEEN 0 AND 3"),)


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    ans_a = Column(String)
    ans_b = Column(String)
    ans_c = Column(String)
    ans_d = Column(String)
    factoid = Column(String, default="")
    category = Column(String)
    correct_ans = Column(Integer, default=-1)
    seen = Column(Boolean, default=False)

    def correct_answer_text(self):
        return ([self.ans_a, self.ans_b, self.ans_c, self.ans_d],self.correct_ans)

    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title}', correct={self.correct_ans})>"
