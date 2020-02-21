import os

from flask import Flask, current_app, send_file
from flask_heroku import Heroku
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='../dist/static')


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vmakgvbbcwowcs:700f51ca8d1fc965b4eb13314926b24b0b6f9bb14ba5cff4ebd8cc6e2c2a70a4@ec2-54-195-247-108.eu-west-1.compute.amazonaws.com:5432/d6ilunbfdjmhmm'

#heroku = Heroku(app)
db = SQLAlchemy(app)

from app.api import api_bp
from app.client import client_bp

app.register_blueprint(api_bp)
app.register_blueprint(client_bp)


from .config import Config

app.logger.info('>>> {}'.format(Config.FLASK_ENV))


@app.route('/')
def index_client():
    dist_dir = current_app.config['DIST_DIR']
    entry = os.path.join(dist_dir, 'index.html')
    return send_file(entry)
