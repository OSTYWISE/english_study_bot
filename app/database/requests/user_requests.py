from app.database.models import async_session
from app.database.models import Student
from sqlalchemy import select, update, delete, desc


async def set_student(tg_id: int):
    """
    Add student to database if he is not registered yet.

    Args:
        tg_id (BigInteger): telegram student id
    """
    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            session.add(Student(tg_id=tg_id))
            await session.commit()
