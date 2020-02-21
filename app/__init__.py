import os

from flask import Flask, current_app, send_file
from flask_heroku import Heroku
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='../dist/static')
heroku = Heroku(app)
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
