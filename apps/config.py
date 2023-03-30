# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY. NECESSARY TO RUN SESSIONS
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'Xat8H6nWC9SjYXs')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_DISABLED = True
    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')    
    
class ProductionConfig(Config):
    DEBUG = False
    os.environ['DEBUG'] = 'False'
    print('yayyaa')
    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600
    LOGIN_DISABLED = True
    # PostgreSQL database
    # SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
    #    os.getenv('DB_ENGINE'   , 'mysql'),
    #    os.getenv('DB_USERNAME' , 'appseed_db_usr'),
    #    os.getenv('DB_PASS'     , 'pass'),
    #    os.getenv('DB_HOST'     , 'localhost'),
    #    os.getenv('DB_PORT'     ,s 3306),
    #    os.getenv('DB_NAME'     , 'appseed_db')
    #)
    SQLALCHEMY_DATABASE_URI = "postgresql://"

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
