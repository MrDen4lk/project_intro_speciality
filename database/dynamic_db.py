from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, JSON, ARRAY, select, insert
import json
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# создаем движок нашей БД, c данными из .env (echo - выводит всё)
path = "postgresql+asyncpg://" + os.getenv("DB_USER") + ":" + os.getenv("DB_PASS") + "@"\
       + os.getenv("DB_HOST") + ":" + os.getenv("DB_PORT") + "/" + os.getenv("DB_NAME")
engine = create_async_engine(url=path,
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
    vac_now = Column(Integer, nullable=False, default=0) # номер показываемой вакансии из списка
    vac_total = Column(Integer, nullable=False, default=0) # всего доступно вакансий по запросу
    page = Column(Integer, nullable=False, default=0) # текущая страница поиска в парсере
    history_req = Column(ARRAY(String), default=list) # история запросов
    history_ans = Column(ARRAY(String), default=list) # история ответов
    history_req_stat = Column(ARRAY(String), default=list) # история запросов статистики 

# таблица citis
class Cities(Base):
    __tablename__ = 'cities'

    city_name = Column(String, primary_key=True)
    city_id= Column(Integer, nullable=False)
    file_path = 'inp.txt'

# таблица towns
class Towns(Base):
    __tablename__ = 'towns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

# таблица salary
class Salary(Base):
    __tablename__ = 'salary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

# таблица experience   
class Experience(Base):
    __tablename__ = 'experience'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

# таблица employment
class Employment(Base):
    __tablename__ = 'employment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

# таблица sort
class Sort(Base):
    __tablename__ = 'sort'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

# создаем таблицу с исп. PostgreSQL
async def create_tables() -> None:
   async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.create_all)

# сносим таблицу с исп. PostgreSQL
async def delete_tables() -> None:
   async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.drop_all)

''' ИНТЕРФЕЙС ВЗАИМОДЕЙТСВИЯ '''
# добавляем пользователя в таблицу
async def add_user(user_id : int, vac_now : int, vac_total : int, page : int, history_req : list, history_ans : list, history_req_stat : list) -> None:

    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()
            if not user:
                new_user = insert(User).values(
                    id=user_id,
                    vac_now=vac_now,
                    vac_total=vac_total,
                    page=page,
                    history_req=history_req,
                    history_ans=history_ans,
                    history_req_stat=history_req_stat
                )
                await session.execute(new_user)
                await session.commit()
            else:
                pass

# включение значений в таблицу cities из файла
async def add_cities(file_path : str) -> None:
    async with new_session() as session:
        async with session.begin():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Преобразуем данные в объекты Towns
            for city_name, city_id in data.items():
                town = insert(Cities).values(city_name=city_name, city_id=city_id)
                await session.execute(town)

            await session.commit()

# включение значений в таблицу towns
async def add_towns() -> None:
    async with new_session() as session:
        async with session.begin():
            map_of_towns = {
                "Moscow": "Москва",
                "Petersburg": "Санкт-Петербург",
                "Novosibirsk": "Новосибирск",
                "Yekaterinburg": "Екатеринбург",
                "Kazan": "Казань",
                "Nizhny": "Нижний Новгород",
                "any_town" : "None"
            }
            
            for id_value, tg_int_value in map_of_towns.items():
                new_town = insert(Towns).values(key=id_value, value=tg_int_value)
                
                await session.execute(new_town)

        await session.commit()

# передаем значения в salary
async def add_salary() -> None:
    async with new_session() as session:
        async with session.begin():
            map_of_salary = {
                "True": "Да",
                "False": "Нет"
            }
            
            for id_value, tg_int_value in map_of_salary.items():
                new_salary = insert(Salary).values(key=id_value, value=tg_int_value)
                
                await session.execute(new_salary)
    
            await session.commit() 

# передаем значения в experience
async def add_experience() -> None:
    async with new_session() as session:
        async with session.begin():
            map_of_experience = {
                "noExperience": "Без опыта",
                "between1And3": "От 1 до 3 лет",
                "between3And6": "От 3 до 6 лет",
                "moreThan6": "Больше 6 лет",
                "any_exp": "None"
                }
            
            for id_value, tg_int_value in map_of_experience.items():
                new_experience = insert(Experience).values(key=id_value, value=tg_int_value)
                
                await session.execute(new_experience)

            await session.commit()  

# передаем значения таблице employment
async def add_employment() -> None:
    async with new_session() as session:
        async with session.begin():
            map_of_employment = {
                "full": "Полный",
                "part": "Неполный",
                "project": "Проектный",
                "probation": "Испытательный срок",
                "any_empl": "None"
            }
            
            for id_value, tg_int_value in map_of_employment.items():
                new_employment = insert(Employment).values(key=id_value, value=tg_int_value)
                
                await session.execute(new_employment)

        await session.commit()

# передаем значения таблице sort
async def add_sort() -> None:
    async with new_session() as session:
        async with session.begin():
            map_of_sort = {
                "relevance": "Релевантности",
                "publication_time": "Свежести",
                "salary_desc": "Убыванию ЗП",
                "salary_asc": "Возрастанию ЗП",
                "any_sort" : "None"
            }

            for id_value, tg_int_value in map_of_sort.items():
                new_sort = insert(Sort).values(key=id_value, value=tg_int_value)
                await session.execute(new_sort)

        await session.commit()

# интерфейс доступа к таблице Cities
async def get_city(tag: str) -> Cities:
    async with new_session() as session:
        result = await session.execute(select(Cities).filter_by(city_name=tag))
        city = result.scalar_one_or_none()

        return city

# интерфейс доступа к таблице Towns
async def get_town(tag: str, find_tag: str) -> Towns:
    async with new_session() as session:
        if find_tag == "id":
            result = await session.execute(select(Towns).filter_by(id=int(tag)))
        elif find_tag == "key":
            result = await session.execute(select(Towns).filter_by(key=tag))
        else:
            result = await session.execute(select(Towns).filter_by(value=tag))
        town = result.scalar_one_or_none()

        return town

# интерфейс доступа к таблице Salary
async def get_salary(tag: str, find_tag: str) -> Salary:
    async with new_session() as session:
        if find_tag == "id":
            result = await session.execute(select(Salary).filter_by(id=int(tag)))
        elif find_tag == "key":
            result = await session.execute(select(Salary).filter_by(key=tag))
        else:
            result = await session.execute(select(Salary).filter_by(value=tag))
        salary = result.scalar_one_or_none()

        return salary

# интерфейс доступа к таблице Experience
async def get_experience(tag: str, find_tag: str) -> Experience:
    async with new_session() as session:
        if find_tag == "id":
            result = await session.execute(select(Experience).filter_by(id=int(tag)))
        elif find_tag == "key":
            result = await session.execute(select(Experience).filter_by(key=tag))
        else:
            result = await session.execute(select(Experience).filter_by(value=tag))
        experience = result.scalar_one_or_none()

        return experience

# интерфейс доступа к таблице Employment
async def get_employment(tag: str, find_tag: str) -> Employment:
    async with new_session() as session:
        if find_tag == "id":
            result = await session.execute(select(Employment).filter_by(id=int(tag)))
        elif find_tag == "key":
            result = await session.execute(select(Employment).filter_by(key=tag))
        else:
            result = await session.execute(select(Employment).filter_by(value=tag))
        employment = result.scalar_one_or_none()  # Получаем один результат или None

        return employment  # Возвращаем результат

# интерфейс доступа к таблице Sort
async def get_sort(tag: str, find_tag: str) -> Sort:
    async with new_session() as session:
        if find_tag == "id":
            result = await session.execute(select(Sort).filter_by(id=int(tag)))
        elif find_tag == "key":
            result = await session.execute(select(Sort).filter_by(key=tag))
        else:
            result = await session.execute(select(Sort).filter_by(value=tag))
        sort = result.scalar_one_or_none()

        return sort

# функция для получения пользователя по айдишнику
async def get_user(user_id: int) -> User:

    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()

            await session.commit()

            return user

# удаление пользователя (ну сдох чувак, удалился тг). Вообще не знаю надо ли нам это, но пусть будет
async def delete_user(user_id: int) -> bool:

    async with new_session() as session:
        async with session.begin():
            user = await get_user(user_id)

            if user:
                await session.delete(user)
                await session.commit()

                return True
            else:
                return False

# функция для обновления данных пользователя
async def update_user(user_id: int, user_dict: dict) -> None:
    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()

            for key, value in user_dict.items():
                if key == 'history_req' or key == 'history_ans' or key == 'history_req_stat':
                    ar = user.history_req.copy()
                    for el in value:
                        ar.append(el)
                    setattr(user, key, ar)
                else:
                    setattr(user, key, value)

            await session.commit()

# SELECT *колонка* IN *таблица*
async def get_column(table_name: str, column_name: str) -> list:
    async with new_session() as session:
        # Определим соот. переданного названия таблицы и её модели внутри БД
        table_mapping = {
            'users': User,
            'salary': Salary,
            'experience': Experience,
            'towns': Towns,
            'cities': Cities,
            'employment': Employment,
            'sort': Sort,
        }

        model = table_mapping.get(table_name)

        # Запрос в таблицу model по column_name
        query = select(getattr(model, column_name))

        result = await session.execute(query)

        return [row for row in result.scalars().all()]

async def start_database() -> None:
    await delete_tables()
    await create_tables()
    await add_towns()
    #await add_cities("inp.txt")
    await add_salary()
    await add_experience()
    await add_employment()
    await add_sort()
    # тащим все id
    id_all = await get_column('sort','key')
    # проверяем корректность работы get_tablename 
    get_sort_checker = await get_sort('1','id')
    get_towns_checker = await get_town('1','id')
    get_salary_checker = await get_salary('1','id')
    get_experience_checker = await get_experience('1','id')
    get_employment_checker = await get_employment('1','id')
    print(id_all)
    print(get_sort_checker.key, get_towns_checker.key, get_salary_checker.key, get_experience_checker.key, get_employment_checker.key, sep='\n')
if __name__ == "__main__":
    asyncio.run(start_database())