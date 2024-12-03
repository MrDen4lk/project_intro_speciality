import pandas as pd
from dask.dataframe import DataFrame


def data(vac_list):
    df = pd.DataFrame(columns=['text', 'employer', 'salary_from', 'salary_to', 'city', 'experience', 'employment'], index=len(vac_list))
    i = 0
    for vac in vac_list:
        salary = vac.get('salary')
        salary_from = vac.get('from')
        salary_to = salary.get('to')
        df.loc[i, 'text'] = vac['text']
        df.loc[i, 'employer'] = vac['employer']
        df.loc[i, 'employment'] = vac['employment']
        df.loc[i, 'experience'] = vac['experience']
        df.loc[i, 'city'] = vac['city']
        df.loc[i, 'salary_from'] = salary_from
        df.loc[i, 'salary_to'] = salary_to
    return df.to_csv(index=False)
