"""
REST API Resource Routing
http://flask-restplus.readthedocs.io
"""

from datetime import datetime
from flask import request
from flask_restx import Resource

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

        from app.model.table import PriceData, Config

        f = request.files['file']
        df = pd.read_excel(f)
        cols = df.cols
        df = df[[cols[0], cols[1], cols[2], cols[3]]]

        pe_season_start = datetime.strptime(Config.query.filterby(config_name='pe_seasion_start').first(), 'dd/mm/yyyy')
        pe_seasion_end = datetime.strptime(Config.query.filterby(config_name='pe_seasion_end').first(), 'dd/mm/yyy')

        pe_weak_start = datetime.strptime(Config.query.filterby(config_name='pe_weak_start').first(), 'dd/mm/yyyy')
        pe_weak_end = datetime.strptime(Config.query.filterby(config_name='pe_weak_end').first(), 'dd/mm/yyyy')

        def check_season(x):
            if x >= pe_season_start and x<= pe_seasion_end:
                return 'high'
            elif x>= pe_weak_start and x<= pe_weak_end:
                return 'mid'
            else:
                return 'low'

        df['season'] = df.date.apply(check_season)
        df['day_week'] = df.date.apply(lambda x: x.weekday())
        df['workday'] = df.day_week.apply(lambda x: 1 if x < 6 else 0)

        df.cols = ['ticket_type', 'date', 'price', 'count', 'season', 'day_week', 'workday']

        df.to_sql('price_data', con=PriceData.season, if_exists='replace')

        return {'status': 'OK', 'message': 'OK'}
