import time

import main
import asyncio
from main import Parser

if __name__ == '__main__':
    params1 = {
        'area': 1,
        'text': "ML engineer",
        'per_page': 50,
        'only_with_salary': "True",
        'experience': "between3And6",
        'employment': "full",
        'sort': "publication_time"
    }
    params2 = {
        'area': 1,
        'text': "Водитель",
        'per_page': 50,
        'only_with_salary': "True",
        'experience': "between3And6",
        'employment': "full",
        'sort': "publication_time"
    }
    a = Parser(params1)
    b = Parser(params2)
    for i in range(1000):
        print(asyncio.run(a.main(i)))
        print(asyncio.run(b.main(i)))