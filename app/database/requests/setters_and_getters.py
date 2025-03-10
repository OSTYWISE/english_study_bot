from app.database.models import async_session
from typing import Type, List
from app.database.models import Student, Organization, LLMRegime, \
    Teacher, PersonalExams, PersonalGraphs, PersonalTopics, PersRegime, \
    Topic, ExamSpecification, ExamsXExams, Exam, ExamsXStudentGroups, \
    StudentGroup, StudentGroupsXSubjects, TeachersXStudentGroups, Task, \
    TasksXStudents, TaskType, Contact, Document, Graph, Subject

from sqlalchemy import select, update


async def set_student(
        tg_id: int, student_group_id: int, name: str,
        age: int, grade: int, phone_number: str, 
        pers_regime: str, topic: str, difficulty: str, task_type: str, regime: str  # These are settings of bot for user. 
        ):
    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            session.add(Student(
                tg_id=tg_id, student_group_id=student_group_id, 
                name=name, age=age, grade=grade, phone_number=phone_number,
                pers_regime=pers_regime, topic=topic, difficulty=difficulty,
                task_type=task_type, regime=regime))
            await session.commit()


async def set_organization(
        invite_code: str, name: str, legal_address: str,
        quote: int | None = None, class_quote: int | None = None) -> None:
    async with async_session() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.name == name))
        if not organization:
            session.add(Organization(
                invite_code=invite_code, name=name, legal_address=legal_address,
                quote=quote, class_quote=class_quote))
            await session.commit()


async def set_teacher(
        tg_id: int, organization_id: int, subject_id: int, name: str,
        age: int, phone_number: str, personal_info: str) -> None:
    async with async_session() as session:
        teacher = await session.scalar(select(Teacher).where(Teacher.tg_id == tg_id))
        if not teacher:
            session.add(Teacher(
                tg_id=tg_id, organization_id=organization_id,
                subject_id=subject_id, name=name, age=age,
                phone_number=phone_number, personal_info=personal_info))
            await session.commit()


async def get_student(tg_id: int) -> Student | None:
    async with async_session() as session:
        student = await session.scalar(
            select(Student).where(Student.tg_id == tg_id))
        return student


async def get_organization(key: int, key_name: str = 'tg_id') -> Organization | None:
    async with async_session() as session:
        if key_name == 'tg_id':
            organization = await session.scalar(select(Organization).where(Organization.tg_id == key))
        else:
            organization = await session.scalar(select(Organization).where(Organization.invite_code == key))
        return organization


async def get_all_organizations() -> Organization | None:
    async with async_session() as session:
        organization = await session.scalars(select(Organization))
        return organization


async def get_llm_regime(name: str) -> LLMRegime | None:
    async with async_session() as session:
        return await session.scalar(select(LLMRegime).where(LLMRegime.name == name))


async def get_pers_regime(name: str) -> PersRegime | None:
    async with async_session() as session:
        return await session.scalar(select(PersRegime).where(PersRegime.name == name))


async def set_contact(data: str, organization_id: int, contact_type_id: int) -> None:
    async with async_session() as session:
        contact = await session.scalar(select(Contact).where(Contact.data == data))
        if not contact:
            session.add(Contact(data=data, organization_id=organization_id, contact_type_id=contact_type_id))
            await session.commit()


async def get_contacts(org_id: int, contact_type_id: int) -> List[Contact] | None:
    async with async_session() as session:
        return await session.scalars(
            select(Contact).where(Contact.organization_id == org_id).where(Contact.contact_type_id == contact_type_id))


async def set_document(data: str, org_id: int, type: str) -> None:
    async with async_session() as session:
        doc = await session.scalar(
            select(Document).where(Document.organization_id == org_id).where(Document.data == data))
        if not doc:
            session.add(Document(data=data, organization_id=org_id, type=type))
            await session.commit()


async def get_documents(org_id: int) -> List[Document | None]:
    async with async_session() as session:
        return await session.scalars(select(Document).where(Document.organization_id == org_id))


async def set_student_group(organization_id: int, teacher_id: int) -> None:
    async with async_session() as session:
        session.add(StudentGroup(organization_id=organization_id, teacher_id=teacher_id))
        await session.commit()


async def get_student_from_group(group_id: int) -> StudentGroup | None:
    async with async_session() as session:
        return await session.scalar(select(StudentGroup).where(StudentGroup.id == group_id))


async def set_subject(name: str) -> None:
    async with async_session() as session:
        subject = await session.scalar(select(Subject).where(Subject.name == name))
        if not subject:
            session.add(Subject(name=name))
            await session.commit()


async def set_exam(name: str, subject_id: int, graph_id: int, max_score: int, generated_flg: bool) -> None:
    async with async_session() as session:
        session.add(Exam(name=name, subject_id=subject_id, graph_id=graph_id, max_score=max_score, generated_flg=generated_flg))
        await session.commit()


async def get_exam(name: str) -> Exam | None:
    async with async_session() as session:
        return await session.scalar(select(Exam).where(Exam.name == name))


async def set_graph(exam_id: int, organization_id: int, subject_id: int) -> None:
    async with async_session() as session:
        session.add(Graph(exam_id=exam_id, organization_id=organization_id, subject_id=subject_id))
        await session.commit()


async def get_graph(graph_id: int) -> Graph | None:
    async with async_session() as session:
        return await session.scalar(select(Graph).where(Graph.id == graph_id))


async def set_topic(name: str, parent_topic_id: str, child_topic_ids: list[int], subject_id: int) -> None:
    async with async_session() as session:
        session.add(Topic(name=name, parent_topic_id=parent_topic_id, child_topic_ids=child_topic_ids, subject_id=subject_id))
        await session.commit()


async def get_topic(name: str) -> Topic | None:
    async with async_session() as session:
        return await session.scalar(select(Topic).where(Topic.name == name))
    

async def get_all_users():
    async with async_session() as session:
        return await session.scalars(select(Student))
