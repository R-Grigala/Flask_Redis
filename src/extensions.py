from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_migrate import Migrate
import redis

from src.config import Config

db = SQLAlchemy()
migrate = Migrate()
api = Api(
    title='IesData',
    version='1.0',
    description='IesData API',
    authorizations=Config.AUTHORIZATION,
    doc='/api'
)

init_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)