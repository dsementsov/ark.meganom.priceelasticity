import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from io import BytesIO
from sqlalchemy.orm import create_session
from app.model.table import Config
import boto3


def get_data(season, workday, ticket_type):
    print('Reading data from S3')
    s3 = boto3.client('s3')
    bucket_name = Config.query.filter_by(
        config_name='bucket_name').first().config_value
    target_year = Config.query.filter_by(config_name='pe_target_year').first()
    obj = s3.get_object(Bucket=bucket_name, Key='pe_data.csv')
    obj_data = obj['Body'].read()
    data = pd.read_csv(BytesIO(obj_data), encoding='utf-8')
    print('Transforming data')
    if target_year is not None:
        if target_year.config_value != 'all':
            data = data[data.year == int(target_year.config_value)]
    if season != 'all':
        data = data[data.season == season]
    if workday != 'all':
        data = data[data.workday == int(workday)]
    if ticket_type != 'all':
        data = data[data.ticket_type == ticket_type]
    return data


def prep_data(df, bins, log_q=True):
    # Only important columns
    data = df[['price', 'qt']]
    data = data[data.qt != ' ']
    data.price = data.price.astype(float)
    data.qt = data.qt.astype(int)
    # Binning df
    data['bin'] = pd.cut(data.price, bins)
    data['average_price'] = data.bin.apply(
        lambda x: data[data.bin == x].price.mean())
    data['average_price'] = data['average_price'].astype(float)
    data = data[['average_price', 'qt']].groupby(
        by=['average_price']).sum().reset_index()
    data = data[['average_price', 'qt']]
    if log_q:
        data['qt'] = np.log(data.qt)
    data['qt'] = data['qt'].astype(float)
    return data


def get_model(data, intercept=False):
    if intercept:
        intercept_formula = ''
    else:
        intercept_formula = ' - 1'

    model = smf.ols('qt ~ np.square(average_price) + average_price' +
                    intercept_formula, data=data).fit()

    return model


def get_extrenum(model):

    roots = get_model_roots(model, a_multi=((2*np.e) + 1), b_multi=(np.e + 1))
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(roots)
    true_price = roots[1]

    true_quantity = round(
        np.e**model.predict({"average_price": true_price})[0]+0.5, 0)
    true_price = round(true_price, -1)

    return float(round(true_price, 2)), float(round(true_quantity+0.5, 0))


def get_model_roots(ols, a_multi=1, b_multi=1):
    '''Получить корни квадратного уравнения'''
    a = ols.params.get('np.square(average_price)') * a_multi
    b = ols.params.get('average_price') * b_multi
    c = ols.params.get('Intercept')
    return get_roots(a, b, c)


def get_roots(a, b, c):
    if c is None:
        c = 0
    x1 = (-b + np.sqrt(np.square(b) - (4*a*c))) / (2*a)
    x2 = (-b - np.sqrt(np.square(b) - (4*a*c))) / (2*a)
    return x1, x2


if __name__ == '__main__':
    pass
