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

from app.price_elasticity import price


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
class SecureResourceOne(SecureResource):
    """ Unsecure Resource Class: Inherit from Resource """

    def get(self, resource_id):
        timestamp = datetime.utcnow().isoformat()
        return {'timestamp': timestamp}


@api_rest.route('/price-elasticity/roots/<string:ticket_type>/<string:season>/<string:workday>/<string:intercept>')
class PriceElasticiyRoots(SecureResource):

    def get(self, ticket_type, season, workday, intercept):
        data = price.get_data(ticket_type=ticket_type, season=season, workday=int(workday))
        model = price.get_model(model, bool(intercept))
        p, q = price.get_extrenum(model)

        return {'status': 'OK', 'message': {'p': p, 'q': q}}

@api_rest.rout('/price-elasticity/data')
class PriceElasticityData(SecureResource):

    def post(self):
        f = request.files.get('file')

        df = pd.read_excel(f)

        return {'status': 'OK', 'message': 'OK'}
