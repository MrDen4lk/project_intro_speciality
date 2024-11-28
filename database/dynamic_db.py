from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, JSON, ARRAY, select, insert
import json
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# создаем движок нашей БД, c данными из .env (echo - выводит всё )
engine = create_async_engine(url="postgresql+asyncpg://postgres:postgres@localhost:5432/Users",
                                    echo=True)
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

# таблица experience   
class Experience(Base):
    __tablename__ = 'experience'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)

# таблица employment
class Employment(Base):
    __tablename__ = 'employment'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)

# таблица citis
class Cities(Base):
    __tablename__ = 'cities'

    city_name = Column(String, primary_key=True)
    city_id= Column(Integer, nullable=False)
    file_path = 'inp.txt'


# таблица towns
class Towns(Base):
    __tablename__ = 'towns'

    id = Column(String, primary_key=True)
    tg_int= Column(String, nullable=False)

class Sort(Base):
    __tablename__ = 'sort'

    id = Column(String, primary_key=True)
    tg_int = Column(String, nullable=False)

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
            else:
                # напиши что нужно
                pass

# передаем значения в salary с проверкой на невозможность повторной передачи
async def add_salary():
    async with new_session() as session:
        async with session.begin():
            map_of_salary = {
                "True" : "Да",
                "False" : "Нет"
            }

            for id_value, tg_int_value in map_of_salary.items():
                
                res = await session.execute(select(Salary).filter_by(id=id_value))
                salary = res.scalar_one_or_none()
                
                if not salary:
                    new_salary = insert(Salary).values(
                        id=id_value, 
                        tg_int=tg_int_value
                        )
                    await session.execute(new_salary)
                else:
                    pass

            await session.commit() 

# передаем значения в experience
async def add_experience():
    async with new_session() as session:
        async with session.begin():
            map_of_experience = {
                "noExperience": "Без опыта",
                "between1And3": "От 1 до 3 лет",
                "between3And6" : "От 3 до 6 лет",
                "moreThan6" : "Больше 6 лет",
                }
            
            for id_value, tg_int_value in map_of_experience.items():

                res = await session.execute(select(Experience).filter_by(id=id_value))
                experience = res.scalar_one_or_none()
                
                if not experience:
                    new_experience = insert(Experience).values(
                        id=id_value,
                        tg_int=tg_int_value
                        )
                    await session.execute(new_experience)
                else:
                    pass

            await session.commit()  

# передаем наши фискисрованные значения таблице employment
async def add_employment():
    async with new_session() as session:
        async with session.begin():
            map_of_employment = {
                "full": "Полный",
                "part": "Неполный",
                "project" : "Проектный",
                "probation" : "Испытательный срок",
            }
            for id_value, tg_int_value in map_of_employment.items():
                
                res = await session.execute(select(Employment).filter_by(id=id_value))
                employment = res.scalar_one_or_none()
                
                if not employment:
                    new_employment = insert(Employment).values(
                        id=id_value, 
                        tg_int=tg_int_value
                        )
                    await session.execute(new_employment)
                else:
                    pass

        await session.commit()    

# включение значений в таблицу cities из файла
async def add_cities(file_path):
    async with new_session() as session: 
        async with session.begin():       
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Преобразуем данные в объекты Towns
            for city_name, city_id in data.items():

                res = await session.execute(select(Cities).filter_by(id=city_name))
                cities = res.scalar_one_or_none()
                
                if not cities:
                    town = insert(Cities).values(
                        city_name=city_name,
                        city_id=city_id
                        )
                    await session.execute(town)
                else:
                    pass

            await session.commit()

# включение значений в таблицу towns
async def add_towns():
    async with new_session() as session:
        async with session.begin():
            map_of_towns = {
                "Moscow": "Москва",
                "Petersburg": "Санкт-Петербург",
                "Novosibirsk": "Новосибирск",
                "Yekaterinburg": "Екатеринбург",
                "Kazan": "Казань",
                "Nizhny": "Нижний Новгород",
                "other": "Другой"
            }
            for id_value, tg_int_value in map_of_towns.items():

                res = await session.execute(select(Towns).filter_by(id=id_value))
                cities = res.scalar_one_or_none()
                
                if not cities:
                    new_town = insert(Towns).values(
                        id=id_value,
                        tg_int=tg_int_value
                        )
                    await session.execute(new_town)
                else:
                    pass
                

        await session.commit()

async def add_sort():
    async with new_session() as session:
        async with session.begin():
            map_of_sort = {
                "relevance" : "Релевантности",
                "publication_time" : "Свежести",
                "salary_desc" : "Убыванию ЗП",
                "salary_asc" : "Возрастанию ЗП"
            }
            for id_value, tg_int_value in map_of_sort.items():
                res = await session.execute(select(Sort).filter_by(id=id_value))
                sort = res.scalar_one_or_none()
                
                if not sort:
                    new_sort = insert(Sort).values(
                        id=id_value, 
                        tg_int=tg_int_value
                        )
                    await session.execute(new_sort)
                else:
                    pass

        await session.commit()

# интерфейс доступа к таблице Cities
async def get_city(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Cities).filter_by(city_name=tag))
        city = result.scalar_one_or_none()

        return city

# интерфейс доступа к таблице Towns
async def get_town(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Towns).filter_by(id=tag))
        town = result.scalar_one_or_none()

        return town

# интерфейс доступа к таблице Salary
async def get_salary(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Salary).filter_by(id=tag))
        salary = result.scalar_one_or_none()

        return salary

# интерфейс доступа к таблице Salary со значение-ключ
async def rev_get_salary(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Salary).filter_by(tg_int=tag))
        salary = result.scalar_one_or_none()

        return salary

# интерфейс доступа к таблице Experience
async def get_experience(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Experience).filter_by(id=tag))
        experience = result.scalar_one_or_none()

        return experience

# интерфейс доступа к таблице Experience со значение-ключ
async def rev_get_experience(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Experience).filter_by(tg_int=tag))
        experience = result.scalar_one_or_none()

        return experience

# интерфейс доступа к таблице Employment
async def get_employment(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Employment).filter_by(id=tag))
        employment = result.scalar_one_or_none()  # Получаем один результат или None

        return employment  # Возвращаем результат

# интерфейс доступа к таблице Employment со значение-ключ
async def rev_get_employment(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Employment).filter_by(tg_int=tag))
        employment = result.scalar_one_or_none()  # Получаем один результат или None

        return employment  # Возвращаем результат

# интерфейс доступа к таблице Sort
async def get_sort(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Sort).filter_by(id=tag))
        sort = result.scalar_one_or_none()

        return sort

# интерфейс доступа к таблице Sort со значение-ключ
async def rev_get_sort(tag: str):
    async with new_session() as session:
        result = await session.execute(select(Sort).filter_by(tg_int=tag))
        sort = result.scalar_one_or_none()

        return sort

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
                'cities' : Cities,
                'employment' : Employment,
                'sort' : Sort,
            }

            model = table_mapping.get(table_name)

            # Запрос в таблицу model по column_name
            query = select(getattr(model, column_name))
    
            result = await session.execute(query)
            
            return [row[0] for row in result.scalars().all()]

async def start_database() -> None:
    await delete_tables()
    await create_tables()
    await add_towns()
    #await add_cities("inp.txt")
    await add_salary()
    await add_experience()
    await add_employment()
    await add_sort()
    await add_towns()
    await add_salary()
    await add_experience()
    await add_employment()
    await add_sort()

if __name__ == "__main__":
    asyncio.run(start_database())