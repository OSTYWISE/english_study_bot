from sqlalchemy import select, delete
from typing import Type, List

from app.database.models import async_session
from app.database.models import Student, Litwork
from app.database.models import Base


async def get_all(model: Type[Base]) -> List[Type[Base]] | None:
    """Getter all objects of given model (type)"""
    async with async_session() as session:
        all_objects = await session.scalars(select(model))
        if all_objects:
            return all_objects.all()
        return None


async def get_student(id: int) -> Student | None:
    async with async_session() as session:
        student = await session.scalar(
            select(Student).where(Student.tg_id == id))
        return student


async def get_all_students():
    async with async_session() as session:
        return await session.scalars(select(Student))


async def set_or_update_student(tg_id: int, new_litwork_id: int) -> None:
    """Function only for registration step to update data on user"""
    async with async_session() as session:
        student = await session.scalar(
            select(Student).where(Student.tg_id == tg_id))

        if student:
            student.litwork_id = new_litwork_id
            await session.commit()
        else:
            student = Student(tg_id=tg_id, litwork_id=new_litwork_id)
            session.add(student)
            await session.commit()


async def delete_student(tg_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(Student).where(Student.tg_id == tg_id))
        await session.commit()


async def get_litwork_by_name(name: str) -> Litwork | None:
    async with async_session() as session:
        return await session.scalar(select(Litwork).where(Litwork.title == name))


async def get_litwork_by_id(id: int) -> Litwork | None:
    async with async_session() as session:
        return await session.scalar(select(Litwork).where(Litwork.id == int(id)))


async def get_value_by_id(model: Type[Base], id: int | None) -> Type[Base] | None:
    """Getter by name"""
    async with async_session() as session:
        return await session.scalar(select(model).where(model.id == id))


async def set_litwork(title: str, author: str, path: str) -> None:
    async with async_session() as session:
        litwork = Litwork(title=title, author=author, path=path)
        session.add(litwork)
        await session.commit()
