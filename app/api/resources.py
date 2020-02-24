"""
REST API Resource Routing
http://flask-restplus.readthedocs.io
"""

from datetime import datetime
from flask import request
from flask_restx import Resource
import json
from io import StringIO
import boto3

import pandas as pd

from .security import require_auth
from . import api_rest


class SecureResource(Resource):
    """ Calls require_auth decorator on all requests """
    method_decorators = [require_auth]


@api_rest.route('/resource/<string:resource_id>')
class ResourceOne(Resource):
    """ Unsecure Resource Class: Inherit from Resource """

    def get(self, resource_id):
        timestamp = datetime.utcnow().isoformat()
        return {'timestamp': timestamp}

    def post(self, resource_id):
        json_payload = request.json
        return {'timestamp': json_payload}, 201


@api_rest.route('/secure-resource/<string:resource_id>')
class SecureResourceOne(Resource):
    """ Unsecure Resource Class: Inherit from Resource """

    def get(self, resource_id):
        timestamp = datetime.utcnow().isoformat()
        return {'timestamp': timestamp}


@api_rest.route('/price-elasticity/roots', defaults={'ticket_type': None, 'season': None, 'workday':None, 'intercept': 0})
@api_rest.route('/price-elasticity/roots/<string:ticket_type>/<string:season>/<string:workday>/<int:intercept>')
class PriceElasticiyRoots(Resource):

    def get(self, ticket_type, season, workday, intercept):
        from app.price_elasticity import price
        from app.model.table import Config
        data = price.get_data(ticket_type=ticket_type, season=season, workday=workday)
        res = []
        for t in data.ticket_type.unique():
            for s in data.season.unique():
                for w in data.workday.unique():
                    print([t,s,w, intercept])
                    df = data[data.ticket_type == t]
                    df = df[df.workday == w]
                    df = df[df.season == s]
                    if not df.empty:
                        try:
                            bins = int(Config.query.filter_by(config_name='pe_bins').first().config_value)
                            df = price.prep_data(df, bins)
                            model = price.get_model(df, bool(int(intercept)))
                            print(model.summary())
                            p, q = price.get_extrenum(model)

                        except Exception:
                            p, q = ('Ошибка', 'Ошибка')
                        res.append({'type': t, 'season': s, 'workday': str(w),
                                    'p': str(p), 'q': str(q), 'adj_r': str(getattr(model, 'rsquared_adj', 'Ошибка'))})
                    else:
                        res.append({'type': t, 'season': s, 'workday': str(w),
                                    'p': 'Недостаточно данных',
                                    'q': 'Недостатчно данных',
                                    'adj_r': 'Недостаточно данных'})
        return {'status': 'OK', 'message': res}

@api_rest.route('/price-elasticity/data')
class PriceElasticityData(Resource):

    def post(self):
        print('Uploading the file to s3')
        from app.model.table import Config
        from app import db

        f = request.files['file']
        df = pd.read_excel(f)

        # get config values (prob should do single table read, but the table is not big
        # enough to see significant performance increase)
        high = Config.query.filter_by(config_name='pe_season_high').first().config_value
        weak = Config.query.filter_by(config_name='pe_season_weak').first().config_value
        price_col = Config.query.filter_by(config_name='pe_price_column').first().config_value
        type_col = Config.query.filter_by(config_name='pe_ticket_type_column').first().config_value
        quantity_col = Config.query.filter_by(config_name='pe_quantity_column').first().config_value
        date_col = Config.query.filter_by(config_name='pe_date_column').first().config_value
        bucket_name = Config.query.filter_by(config_name='bucket_name').first().config_value

        df = df[[type_col, date_col, price_col, quantity_col]]

        pe_season_high = json.loads(high)
        pe_season_weak = json.loads(weak)

        def check_season(x):
            if x.month in pe_season_high:
                return 'high'
            elif x.month in pe_season_weak:
                return 'mid'
            else:
                return 'low'

        df['season'] = df[date_col].apply(check_season)
        df['day_week'] = df[date_col].apply(lambda x: x.weekday())
        df['workday'] = df.day_week.apply(lambda x: 1 if x < 5 else 0)
        df['year'] = df[date_col].apply(lambda x: x.year)

        df.columns = ['ticket_type', 'date', 'price', 'qt', 'season', 'day_week', 'workday', 'year']

        # save data on s3 in csv format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        s3_resource = boto3.resource('s3')
        # deleting file
        try:
            s3_resource.Object(bucket_name, 'pe_data.csv').delete()
        except:
            print('File did not exist')

        s3_bucket = s3_resource.Bucket(bucket_name)
        s3_bucket.put_object(Key='pe_data.csv', Body=csv_buffer.getvalue(), ACL='public-read', )
        print('DONE!')

        return {'status': 'OK', 'message': 'OK'}



@api_rest.route('/price-elasticity/ticket-types')
class PriceElasticityTicketTypes(Resource):

    def get(self):
        from app.price_elasticity import price
        df = price.get_data('all', 'all', 'all')
        ticket_types = df.ticket_type.unique()

        return {'status': 'OK', 'message': list(ticket_types)}

@api_rest.route('/price-elasticity/config')
class PriceElasticityConfig(Resource):

    def get(self):
        from app.model.table import Config
        configs = Config.query.all()
        config_values = {}
        for c in configs:
            config_values[c.config_name] = c.config_value

        return {'status': 'OK', 'message': config_values}

    def post(self):
        from app.model.table import Config
        print(request.get_json())
        payload = request.json

        for key, value in payload.items():
            c = Config.query.filter_by(config_name=key).first()
            c.config_value = value
            c.update()

        return {'status': 'OK', 'message': {}}
