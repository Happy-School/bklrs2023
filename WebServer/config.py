from dotenv import load_dotenv
import os
import redis
load_dotenv()

class ApplicationConfig:

    SECRET_KEY = os.environ["SECRET_KEY"]
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    db_directory = '/home/demf/Desktop/FX_BOT/WebServer'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_directory}/db.sqlite3'

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")
    PERMANENT_SESSION_LIFETIME = 1800
    SESSION_COOKIE_SAMESITE = 'None'