"""
REST API Resource Routing
http://flask-restplus.readthedocs.io
"""

from datetime import datetime
from flask import request
from flask_restx import Resource
import json

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


@api_rest.route('/price-elasticity/roots/<string:ticket_type>/<string:season>/<string:workday>/<string:intercept>')
class PriceElasticiyRoots(Resource):

    def get(self, ticket_type, season, workday, intercept):
        from app.price_elasticity import price
        data = price.get_data(ticket_type=ticket_type, season=season, workday=int(workday))
        model = price.get_model(model, bool(intercept))
        p, q = price.get_extrenum(model)

        return {'status': 'OK', 'message': {'p': p, 'q': q}}

@api_rest.route('/price-elasticity/data')
class PriceElasticityData(Resource):

    def post(self):

        from app.model.table import Config
        from app import db

        f = request.files['file']
        df = pd.read_excel(f)
        cols = df.columns
        df = df[[cols[0], cols[1], cols[2], cols[3]]]
        df.columns = ['ticket_type', 'date', 'price', 'count']

        high = Config.query.filter_by(config_name='pe_season_high').first().config_value
        weak = Config.query.filter_by(config_name='pe_season_weak').first().config_value

        pe_season_high = json.loads(high)
        pe_season_weak = json.loads(weak)

        def check_season(x):
            if x.month in pe_season_high:
                return 'high'
            elif x.month in pe_season_weak:
                return 'mid'
            else:
                return 'low'

        df['season'] = df.date.apply(check_season)
        df['day_week'] = df.date.apply(lambda x: x.weekday())
        df['workday'] = df.day_week.apply(lambda x: 1 if x < 6 else 0)

        df.columns = ['ticket_type', 'date', 'price', 'count', 'season', 'day_week', 'workday']

        df.to_sql('price_data', con=db.engine, if_exists='replace')

        return {'status': 'OK', 'message': 'OK'}
