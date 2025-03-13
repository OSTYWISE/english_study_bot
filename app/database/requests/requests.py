from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound
from typing import Type, List

from app.database.models import async_session
from app.database.models import Student, Organization, LLMRegime, \
    Teacher, PersonalExams, PersonalGraphs, PersonalTopics, PersRegime, \
    Topic, ExamSpecification, ExamsXExams, Exam, ExamsXStudentGroups, \
    StudentGroup, StudentGroupsXSubjects, TeachersXStudentGroups, Task, \
    TasksXStudents, TaskType, Contact, Document, Graph, Subject, Difficulty
from app.database.models import Base


async def set_const_value(model: Type[Base], name: str) -> None:
    """Setter for dict tables: [LLMRegime, PersRegime, Subject, TaskType, Difficulty]"""
    async with async_session() as session:
        instance = await session.scalar(select(model).where(model.name == name))
        if not instance:
            session.add(model(name=name))
            await session.commit()


async def get_const_value(model: Type[Base], name: str) -> Type[Base] | None:
    """Getter by name"""
    async with async_session() as session:
        return await session.scalar(select(model).where(model.name == name))


async def get_value_by_id(model: Type[Base], id: int | None) -> Type[Base] | None:
    """Getter by name"""
    async with async_session() as session:
        return await session.scalar(select(model).where(model.id == id))
    

async def get_all(model: Type[Base]) -> List[Type[Base]] | None:
    """Getter all objects of given model (type)"""
    async with async_session() as session:
        all_objects = await session.scalars(select(model))
        if all_objects:
            return all_objects.all()
        return None


async def set_student(
        invite_code: str, student_group_id: int, name: str,
        grade: int, organization_id: int
        ):
    async with async_session() as session:
        session.add(Student(
            invite_code=invite_code, student_group_id=student_group_id,
            name=name, grade=grade, organization_id=organization_id))
        await session.commit()


async def set_organization(
        invite_code: str, name: str, legal_address: str,
        quote: int | None = None, class_quote: int | None = None) -> None:
    async with async_session() as session:
        organization = await session.scalar(select(Organization).where(Organization.invite_code == invite_code))
        if not organization:
            session.add(Organization(
                invite_code=invite_code, name=name, legal_address=legal_address,
                quote=quote, class_quote=class_quote))
            await session.commit()


async def set_teacher(
        invite_code: str, organization_id: int, subject_id: int, name: str
        ) -> None:
    async with async_session() as session:
        teacher = await session.scalar(select(Teacher).where(Teacher.invite_code == invite_code))
        if not teacher:
            session.add(Teacher(
                invite_code=invite_code, organization_id=organization_id,
                subject_id=subject_id, name=name))
            await session.commit()


async def get_student(id: int, registration_flg: bool = False) -> Student | None:
    async with async_session() as session:
        if registration_flg:
            student = await session.scalar(
                select(Student).where(Student.invite_code == id))
        else:
            student = await session.scalar(
                select(Student).where(Student.tg_id == id))
        return student
    

async def get_teacher(id: int, registration_flg: bool = False) -> Teacher | None:
    async with async_session() as session:
        if registration_flg:
            teacher = await session.scalar(
                select(Teacher).where(Teacher.invite_code == id))
        else:
            teacher = await session.scalar(
                select(Teacher).where(Teacher.tg_id == id))
        return teacher


async def get_organization(id: int, registration_flg: bool = False) -> Organization | None:
    async with async_session() as session:
        if registration_flg:
            organization = await session.scalar(
                select(Organization).where(Organization.invite_code == id))
        else:
            organization = await session.scalar(
                select(Organization).where(Organization.tg_id == id))
        return organization


async def get_all_organizations() -> Organization | None:
    async with async_session() as session:
        organizations = await session.scalars(select(Organization))
        return organizations


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


async def set_student_group(name: str, organization_id: int, teacher_id: int) -> None:
    async with async_session() as session:
        session.add(StudentGroup(
            organization_id=organization_id, teacher_id=teacher_id,
            name=name))
        await session.commit()


async def get_student_from_group(group_id: int) -> StudentGroup | None:
    async with async_session() as session:
        return await session.scalar(select(StudentGroup).where(StudentGroup.id == group_id))


async def set_exam(name: str, subject_id: int, graph_id: int, max_score: int, generated_flg: bool) -> None:
    async with async_session() as session:
        session.add(Exam(name=name, subject_id=subject_id, graph_id=graph_id, max_score=max_score, generated_flg=generated_flg))
        await session.commit()


async def set_graph(exam_id: int, organization_id: int, subject_id: int) -> None:
    async with async_session() as session:
        session.add(Graph(exam_id=exam_id, organization_id=organization_id, subject_id=subject_id))
        await session.commit()


async def get_graph(graph_id: int) -> Graph | None:
    async with async_session() as session:
        return await session.scalar(select(Graph).where(Graph.id == graph_id))


async def set_topic(name: str, subject_id: int, parent_id: int | None = None) -> None:
    async with async_session() as session:
        session.add(Topic(name=name, parent_id=parent_id, subject_id=subject_id))
        await session.commit()


async def get_all_users():
    async with async_session() as session:
        return await session.scalars(select(Student))


async def get_all_leaves():
    async with async_session() as session:
        topic_leaves = await session.scalars(Topic).filter(~Topic.children.any()).all()
        return topic_leaves


async def is_topic_leaf(topic_id: int) -> bool:
    async with async_session() as session:
        topic = await session.scalar(Topic).filter_by(id=topic_id).first()
        return len(topic.children) == 0 if topic else False


async def get_children_topics(session, topic_id: int):
    async with async_session() as session:
        topics = session.scalars(Topic).filter_by(parent_id=topic_id).all()
        return topics


async def update_teacher(invite_code, **kwargs) -> None:
    async with async_session() as session:
        session.update("teachers").where(Teacher.invite_code == invite_code).values(**kwargs)
        await session.commit()


async def update_org(
    tg_id: int, registration_flg: bool = True,
    invite_code: str | None = None,
):
    async with async_session() as session:
        if registration_flg:
            if invite_code is None:
                raise ValueError("Invite code is required at this stage of registration.")
            else:
                organization = await session.scalar(
                    select(Organization).where(Organization.invite_code == invite_code))

        if organization is None:
            raise NoResultFound("Organization with this invite_code not found.")

        if registration_flg:
            organization.tg_id = tg_id

        await session.commit()


async def update_teacher(
    tg_id: int, user_data: dict,
    registration_flg: bool = True,
    invite_code: str | None = None,
):
    async with async_session() as session:
        if registration_flg:
            if invite_code is None:
                raise ValueError("Invite code is required at this stage of registration.")
            else:
                teacher = await session.scalar(
                    select(Teacher).where(Teacher.invite_code == invite_code))
        else:
            teacher = await session.scalar(
                select(Teacher).where(Teacher.tg_id == tg_id))

        if teacher is None:
            raise NoResultFound("teacher with this tg_id not found.")

        if registration_flg:
            teacher.phone_number = user_data.get('phone')
            teacher.birth_date = user_data.get('birth_date')
            teacher.tg_id = tg_id
        
        teacher.personal_info = user_data.get('personal_info')
        await session.commit()


async def update_student(tg_id: int, user_data: dict, invite_code: str) -> None:
    """Function only for registration step to update data on user"""
    async with async_session() as session:
        if invite_code is None:
            raise ValueError("Invite code is required at this stage of registration.")
        else:
            student = await session.scalar(
                select(Student).where(Student.invite_code == invite_code))

        student.phone_number = user_data.get('phone')
        student.birth_date = user_data.get('birth_date')
        student.tg_id = tg_id
        await session.commit()


async def delete_student(tg_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(Student).where(Student.tg_id == tg_id))
        await session.commit()


async def delete_org(tg_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(Organization).where(Organization.tg_id == tg_id))
        await session.commit()


async def update_bot_settings(tg_id: int, user_data: dict) -> None:
    async with async_session() as session:
        student = await session.scalar(
            select(Student).where(Student.tg_id == tg_id))

        if student is None:
            raise NoResultFound("Student with this tg_id not found.")

        student.pers_regime_id = user_data.get('pers_regime_id')
        student.topic_id = user_data.get('topic_id')
        student.difficulty_id = user_data.get('difficulty_id')
        student.task_type_id = user_data.get('task_type_id')
        student.regime_id = user_data.get('llm_regime_id')
        await session.commit()
