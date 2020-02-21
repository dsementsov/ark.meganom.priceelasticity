import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sqlalchemy.orm import create_session
from app.model.table import PriceData


def get_data(season, workday, ticket_type):
    query = PriceData.query
    if season:
        query = query.filter_by(season=season)
    if workday:
        query = query.filter_by(workday=workday)
    if ticket_type:
        query = query.filter_by(ticket_type=ticket_type)
    df = pd.read_sql(query, PriceData.session)
    return df

def prep_data(df, bins, log_q=True):

    data = df[['price', 'count']]

    data['bin'] = pd.cut(df.Price, bins)
    data['average_price'] = data.bin.apply(lambda x: data[data.bin == x].price.mean())
    data = data.groupby(by=['average_price']).sum().reset_index()
    data = data[['average_price', 'count']]
    if log_q:
        data['count'] = np.log(data.count)

    return data


def get_model(data, intercept=False):
    if intercept:
        intercept_formula = ' - 1'
    else:
        intercept_formula = ''

    model = smf.ols('count ~ np.square(average_price) + average_price'+intercept_formula, data=data).fit()

    return model

def get_extrenum(model):

    roots = get_roots(model, a_multi = ( (2*np.e) + 1), b_multi = (np.e + 1))
    true_root = roots[1]

    true_quantity = round(np.e**model.predict({"average_price": true_root})[0]+0.5, 0)
    true_price = round(true_price, -1)

    return true_price, true_quantity


def get_roots(ols, a_multi=1, b_multi=1):
    '''Получить корни квадратного уравнения'''
    a = ols.params.get('np_square(average_price)') * a_multi
    b = ols.params.get('average_price') * b_multi
    c = ols.params.get('Intercept')
    if c is None:
        c = 0
        x1 = 0
        x2 = -b / a
    else:
        x1 = (-b + np.sqrt(np.square(b) - (4*a*c)) ) / (2*a)
        x2 = (-b - np.sqrt(np.square(b) - (4*a*c) )) / (2*a)
    return x1, x2


if __name__ == '__main__':
    pass