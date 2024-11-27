from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, JSON, ARRAY, select, CheckConstraint, insert
import json

#from config import database_url_asyncpg

# создаем движок нашей БД, c данными из .env (echo - выводит всё )
engine = create_async_engine(url='postgresql+asyncpg://postgres:postgres@localhost:5432/Users', echo=True)
# создаем менеджер асинх сессий (сессия, хаха, сессия...)
new_session = async_sessionmaker(engine, expire_on_commit=False)

# базовый класс для таблички
class Base(DeclarativeBase):
    pass

# класс описывающий структуру таблицы пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False) # имя пользователя
    answer_for_req = Column(JSON, nullable=False) # JSON с ответом на запрос
    page_now = Column(Integer, nullable=False, default=0) # номер показываемой вакансии из списка
    total_page = Column(Integer, nullable=False, default=0) # всего доступно вакансий по запросу
    history_req = Column(ARRAY(String), default=list) # история запросов
    history_ans = Column(ARRAY(String), default=list) # история ответов

# таблица salary
class Salary(Base):
    __tablename__ = 'salary'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)

    # задаём фиксированные значения в таблице 
    '''__table_args__ = (
        CheckConstraint("id IN ('yes', 'no')", name="check_id"),
        CheckConstraint("tg_int IN ('да', 'нет')", name="check_tg_int"),
    )'''

# таблица experience   
class Experience(Base):
    __tablename__ = 'experience'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)

    # задаём фиксированные значения в таблице 
    __table_args__ = (
        CheckConstraint("id IN ('noexp', '1to3', '3to6', 'more6')", name="check_id"),
        CheckConstraint("tg_int IN ('Без опыта', 'От 1 до 3 лет', 'От 3 до 6 лет', 'Больше 6 лет')", name="check_tg_int"),
    )
# таблица employment
class Employment(Base):
    __tablename__ = 'employment'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)

    '''
    # задаём фиксированные значения в таблице 
    __table_args__ = (
        CheckConstraint("id IN ('full', 'part', 'project', 'probation')", name="check_id"),
        CheckConstraint("tg_int IN ('Полный', 'Неполный', 'Проектный', 'Испытательный срок')", name="check_tg_int"),
    )'''

# таблица towns
class Towns(Base):
    __tablename__ = 'towns'

    city_name = Column(String, primary_key=True)
    city_id= Column(Integer, nullable=False)
    file_path = 'inp.txt'

class Sort(Base):
    __tablename__ = 'sort'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)


    __table_args__ = (
        CheckConstraint("id IN ('relevance', 'publication_time', 'salary_down', 'salary_up')", name="check_id"),
        CheckConstraint("tg_int IN ('Релевантности', 'Времени публикации', 'Убыванию ЗП', 'Возрастанию ЗП')", name="check_tg_int"),

    )

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
async def add_user(id : int, name : str, answer_for_req : dict, page_now : int, total_page : int, history_req : list, history_ans : list):

    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=id))
            user = result.scalar_one_or_none()
            if not user:
                new_user = insert(User).values(
                    id=id,
                    name=name,
                    answer_for_req=answer_for_req,
                    page_now=page_now,
                    total_page=total_page,
                    history_req=history_req,
                    history_ans=history_ans
                )
                await session.execute(new_user)
                await session.commit()

# возвращаем JSON с данными о всех пользователях 
async def get_all_users_json():

    async with new_session() as session:
        async with session.begin():
            users = await session.query(User).all()
            
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

            await session.commit()
            # Возвращаем результат в формате JSON
            return json.dumps(results, ensure_ascii=False)

# передаем значения в salary
async def add_salary():
    async with new_session() as session:
        async with session.begin():
            map_of_salary = {"yes" : "Да",
                            "no" : "Нет"
                            }

            for id_value, tg_int_value in map_of_salary.items():
                new_salary = insert(Salary).values(id=id_value, tg_int=tg_int_value)
                await session.execute(new_salary)
    
            await session.commit() 

# передаем значения в experience
async def add_experience():
    async with new_session() as session:
        async with session.begin():
            map_of_experience = {"noexp": "Без опыта",
                                "1to3": "От 1 до 3 лет",
                                "3to6" : "От 3 до 6 лет",
                                "more6" : "Больше 6 лет"
                                }
            for id_value, tg_int_value in map_of_experience.items():
                new_experience = insert(Experience).values(id=id_value, tg_int=tg_int_value)
                await session.execute(new_experience)

            await session.commit()  

# передаем наши фискисрованные значения таблице employment
async def add_employment():
    async with new_session() as session:
        async with session.begin():
            map_of_employment = {"full": "Полный",
                                "part": "Неполный",
                                "project" : "Проектный",
                                "probation" : "Испытательный срок"
                                }
            for id_value, tg_int_value in map_of_employment.items():
                new_employment = insert(Employment).values(id=id_value, tg_int=tg_int_value)
                await session.execute(new_employment)

        await session.commit()    

# включение значений в таблицу towns из файла
async def add_cities(file_path):
    async with new_session() as session: 
        async with session.begin():       
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Преобразуем данные в объекты Towns
            for city_name, city_id in data.items():
                town = insert(Towns).values(city_name=city_name, city_id=city_id)
                await session.execute(town)

            await session.commit()

async def add_sort():
    async with new_session() as session:
        async with session.begin():
            map_of_sort = {"relevance" : "Релевантности",
                            "publication_time" : "Времени публикации",
                            "salary_down" : "Убыванию ЗП",
                            "salary_up" : "Возрастанию ЗП"
                            }
            for id_value, tg_int_value in map_of_sort.items():
                new_sort = insert(Sort).values(id=id_value, tg_int=tg_int_value)
                await session.execute(new_sort)

        await session.commit()

# интерфейс доступа к таблице Salary
async def get_salary(tag: str):
    async with new_session() as session:
        async with session.begin():       
            result = await session.execute(select(Salary).filter_by(id=tag))
            salary = result.scalar_one_or_none()

            #await session.commit()

            return salary


# интерфейс доступа к таблице Salary
async def get_experience(tag: str):
    async with new_session() as session:
        async with session.begin():       
            result = await session.execute(select(Experience).filter_by(id=tag))
            experience = result.scalar_one_or_none()

            await session.commit()

            return experience


# интерфейс доступа к таблице Employment
async def get_employment(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Employment).filter_by(id=tag))
        employment = result.scalar_one_or_none()  # Получаем один результат или None

        return employment  # Возвращаем результат
'''
# возвращаем JSON с данными о пользователе по айдишнику
async def get_user_by_id_json(user_id: int):

    async with new_session() as session:
        async with session.begin():
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
                
                await session.commit()

                return json.dumps(user_dict)
            else:
                await session.commit()

                return json.dumps({"error": "User not found"})
'''     
# функция для получения пользователя по айдишнику
async def get_user(user_id: int):

    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()

            await session.commit()

            return user

# функция для обновления пользователя
async def update_user(user_id: int, dict : dict):

    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()

            for key, value in dict.items():
                setattr(user, key, value)

            #await session.refresh(user)
            #await session.commit()

            return user

# удаление пользователя (ну сдох чувак, удалился тг). Вообще не знаю надо ли нам это, но пусть будет
async def delete_user(user_id: int):

    async with new_session() as session:
        async with session.begin():
            user = await get_user(user_id)

            if user:
                await session.delete(user)
                await session.commit()

                return True
            else:
                return False

# SELECT *колонка* IN *таблица* 
async def get_column(table_name : str, column_name : str) -> list:
    async with new_session() as session:
        async with session.begin():
            # Определим соот. переданного названия таблицы и её модели внутри БД
            table_mapping = {
                'salary' : Salary,
                'experience' : Experience,
                'towns' : Towns,
                'employment' : Employment,
                'sort' : Sort,
            }

            model = table_mapping.get(table_name)

            # Запрос в таблицу model по column_name
            query = select(getattr(model, column_name))
    
            result = await session.execute(query)
            
            return [row[0] for row in result.scalars().all()]
    
        '''если вдруг не заработало
        1) return [str(i) for i in res.all()
        если и это не заработало:
        2)
        query = select(getattr(model, column_name))
    
        result = await session.execute(query)
        
        return [row[0] for row in result.scalars().all()]
        '''

import asyncio

async def main():
    await delete_tables()
    await create_tables()
    await add_salary()
    #await add_cities('inp.txt')
    await add_employment()
    await add_sort()
    await add_experience()
    await add_user(

        id=1,

        name="Имя пользователя",

        answer_for_req={"ключ": "значение"},

        page_now=1,

        total_page=10,

        history_req=["запрос1", "запрос2"],

        history_ans=["ответ1", "ответ2"]

    )
    a = await get_user(1)
    a.name = 'Денис'
    a.page_now = 2
    a.total_page = 15
    # как можешь узреть спокойно вытаскивается абсолютно все 
    #print(a.name, a.page_now, a.total_page)
    await update_user(1, {'name' : 'Денис', 'page_now' : 4}) # передаешь словарь аргумент класса : новое значение
    b = await get_user(1)
    print(b.name, b.page_now)

    # вот эта шняга не работает
    #a = get_column('user','name')
    #print(await get_salary('yes'))

if __name__ == "__main__":
    asyncio.run(main())