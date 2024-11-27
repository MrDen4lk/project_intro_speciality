from datetime import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, JSON, ARRAY, select
import json
from database.config import database_url_asyncpg

# создаем движок нашей БД, c данными из .env (echo - выводит всё)
engine = create_async_engine(url=database_url_asyncpg(), echo=True)
# создаем менеджер асинх сессий (сессия, хаха, сессия...)
new_session = async_sessionmaker(engine, expire_on_commit=False)

# базовый класс для таблички
class Base(DeclarativeBase):
    pass

# класс описывающий структуру таблицы пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # имя пользователя
    answer_for_req = Column(JSON, nullable=False)  # JSON с ответом на запрос
    page_now = Column(Integer, nullable=False, default=0)  # номер показываемой вакансии из списка
    total_page = Column(Integer, nullable=False, default=0)  # всего доступно вакансий по запросу
    history_req = Column(ARRAY(String), default=list)  # история запросов
    history_ans = Column(ARRAY(String), default=list)  # история ответов


# создаем таблицу с исп. PostgreSQL
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# сносим таблицу с исп. PostgreSQL
async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


''' ИНТЕРФЕЙС ВЗАИМОДЕЙТСВИЯ '''

# добавляем пользователя в таблицу
async def add_user(name, answer_for_req, page_now, total_page, history_req, history_ans):
    async with new_session() as session:
        async with session.begin():
            new_user = User(
                name=name,
                answer_for_req=answer_for_req,
                page_now=page_now,
                total_page=total_page,
                history_req=history_req,
                history_ans=history_ans
            )
            session.add(new_user)
    return new_user


# возвращаем JSON с данными о всех пользователях
async def get_all_users_json():
    async with new_session as session:
        async with session.begin():
            users = session.query(User).all()

            results = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'answer_for_req': user.answer_for_req,
                    'page_now': user.page_now,
                    'total_page': user.total_page,
                    'history_req': user.history_req,
                    'history_ans': user.history_ans
                }
                results.append(user_data)

            # Возвращаем результат в формате JSON
            return json.dumps(results, ensure_ascii=False)

# возвращаем JSON с данными о пользователе по айдишнику
async def get_user_by_id_json(user_id: int):
    async with new_session() as session:
        # Выполняем запрос к базе данных
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:

            # Преобразуем объект пользователя в JSON
            user_dict = {
                "id": user.id,
                "name": user.name,
                "answer_for_req": user.answer_for_req,
                "page_now": user.page_now,
                "total_page": user.total_page,
                "history_req": user.history_req,
                "history_ans": user.history_ans
            }

            return json.dumps(user_dict)
        else:

            return json.dumps({"error": "User not found"})

# функция для получения пользователя по айдишнику
async def get_user(user_id: int):
    async with new_session() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar_one_or_none()

        await session.commit()

        return user

# функция для обновления пользователя
async def update_user(user_id: int, **kwargs):
    async with new_session() as session:
        user = await get_user(user_id)

        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)

            await session.commit()
            await session.refresh(user)

            return user
        else:
            return None

# удаление пользователя (ну сдох чувак, удалился тг). Вообще не знаю надо ли нам это, но пусть будет
async def delete_user(user_id: int):
    async with new_session() as session:
        user = await get_user(id)

        if user:
            await session.delete(user)
            await session.commit()

            return True
        else:
            return False