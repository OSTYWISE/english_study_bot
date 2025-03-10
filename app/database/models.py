import os
from dotenv import load_dotenv
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger, Boolean, Float, ARRAY, Integer, UUID
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text
import uuid


load_dotenv()
engine = create_async_engine(
    url=os.getenv("SQLALCHEMY_URL"), echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(primary_key=True)
    invite_code: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False
    )
    tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    legal_address: Mapped[str] = mapped_column(String)
    quote: Mapped[Optional[int]] = mapped_column(nullable=True)  # limit on num of classes
    class_quote: Mapped[Optional[int]] = mapped_column(nullable=True)  # limit on class size


class Teacher(Base):
    __tablename__ = 'teachers'

    id: Mapped[int] = mapped_column(primary_key=True)
    invite_code: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False
    )
    tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column()
    phone_number: Mapped[str] = mapped_column(String(12))
    personal_info: Mapped[str] = mapped_column(String)


class Student(Base):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(primary_key=True)
    invite_code: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False
    )
    tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    student_group_id: Mapped[int] = mapped_column(ForeignKey("student_groups.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'))
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(nullable=True)
    grade: Mapped[int] = mapped_column()  # 1-11 - нужна проверка при создании 
    phone_number: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    pers_regime_id: Mapped[Optional[int]] = mapped_column(ForeignKey('pers_regimes.id'), nullable=True)
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey('topics.id'), nullable=True)
    difficulty_id: Mapped[Optional[int]] = mapped_column(ForeignKey('difficulties.id'), nullable=True)
    task_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey('task_types.id'), nullable=True)
    regime_id: Mapped[Optional[int]] = mapped_column(ForeignKey('llm_regimes.id'), nullable=True)


class LLMRegime(Base):
    __tablename__ = 'llm_regimes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class PersRegime(Base):
    __tablename__ = 'pers_regimes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))  # in ["Персонализированное обучение", "Выбор темы"]


class Contact(Base):
    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column(String(80))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    contact_type: Mapped[str] = mapped_column(String(20))  # in ["почта", "телеграм", "телефон"]


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    type: Mapped[str] = mapped_column(String(20))
    storage_link: Mapped[str] = mapped_column(String)


class StudentGroup(Base):
    __tablename__ = 'student_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))


class TeachersXStudentGroups(Base):
    __tablename__ = 'teachers_x_student_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    student_group_id: Mapped[int] = mapped_column(ForeignKey("student_groups.id"))


class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class StudentGroupsXSubjects(Base):
    __tablename__ = 'student_groups_x_subjects'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_group_id: Mapped[int] = mapped_column(ForeignKey("student_groups.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))


class Exam(Base):
    __tablename__ = 'exams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    graph_id: Mapped[int] = mapped_column(Integer, ForeignKey('graphs.id'), nullable=True, unique=True)
    max_score: Mapped[int] = mapped_column()
    generated_flg: Mapped[bool] = mapped_column(Boolean)
    graph = relationship("Graph", back_populates="exam", uselist=False)


class Graph(Base):
    __tablename__ = 'graphs'

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    exam = relationship("Exam", back_populates="graph", uselist=False)


class Topic(Base):
    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    parent_topic_id: Mapped[str] = mapped_column(String(50))
    child_topic_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))


class ExamsXStudentGroups(Base):
    __tablename__ = 'exams_x_student_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    student_group_id: Mapped[int] = mapped_column(ForeignKey("student_groups.id"))


class TaskType(Base):
    __tablename__ = 'task_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))  # in ['Yes/No','Single choice ','Multiple choice','Strict format text answer','*Free text','Random from']


class Difficulty(Base):
    __tablename__ = 'difficulties'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class ExamSpecification(Base):
    __tablename__ = 'exam_specifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    difficulty_id: Mapped[int] = mapped_column(ForeignKey("difficulties.id"))
    task_type_id: Mapped[int] = mapped_column(ForeignKey("task_types.id"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    exam_specification_id: Mapped[int] = mapped_column(ForeignKey("exam_specifications.id"))
    statement_text: Mapped[str] = mapped_column(String)
    answer_options: Mapped[List[str]] = mapped_column(ARRAY(String))
    answer: Mapped[str] = mapped_column(String)
    generated_flg: Mapped[bool] = mapped_column(Boolean)
    source_text: Mapped[str] = mapped_column(String)


class PersonalGraphs(Base):
    __tablename__ = 'personal_graphs'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    graph_id: Mapped[int] = mapped_column(ForeignKey("graphs.id"))
    personal_exam_id: Mapped[int] = mapped_column(ForeignKey("personal_exams.id"))


class PersonalTopics(Base):
    __tablename__ = 'personal_topics'

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    personal_graph_id: Mapped[int] = mapped_column(ForeignKey("personal_graphs.id"))
    understood_score: Mapped[int] = mapped_column()
    priority: Mapped[int] = mapped_column()


class PersonalExams(Base):
    __tablename__ = 'personal_exams'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    personal_graph_id: Mapped[int] = mapped_column(ForeignKey("personal_graphs.id"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    score: Mapped[float] = mapped_column(Float)


class TasksXStudents(Base):
    __tablename__ = 'tasks_x_students'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    result: Mapped[float] = mapped_column(Float)  # from 0 to 1


class ExamsXExams(Base):
    __tablename__ = 'tasks_x_exams'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    result: Mapped[float] = mapped_column(Float)  # from 0 to 1


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))

        result = await conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public';
        """))
        tables = result.scalars().all()

        for table in tables:
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

        await conn.execute(text("SET session_replication_role = 'origin';"))
        print("All tables dropped successfully.")