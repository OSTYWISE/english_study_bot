import os
import uuid
from dotenv import load_dotenv
from typing import Optional
from sqlalchemy import ForeignKey, String, BigInteger, ARRAY
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text


load_dotenv()

engine = create_async_engine(
    url=os.getenv("SQLALCHEMY_URL"))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    litwork_id: Mapped[int] = mapped_column(ForeignKey("litworks.id"))


class Litwork(Base):
    __tablename__ = 'litworks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    path: Mapped[str] = mapped_column(String)


class Topic(Base):
    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String)
    options: Mapped[list[str]] = mapped_column(ARRAY(String))
    correct_answer: Mapped[int] = mapped_column()  # int from 1 to 4
    litwork_id: Mapped[int] = mapped_column(ForeignKey("litworks.id"))


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