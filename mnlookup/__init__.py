from flask import Flask
from flask_apscheduler import APScheduler

from .config import Config


scheduler = APScheduler()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from mnlookup.api.controller import api
    app.register_blueprint(api, url_prefix='/api')

    from mnlookup.mainapp import main_app
    dash_apps = [
        main_app(),
    ]
    for dapp in dash_apps:
        dapp.init_app(app)
    
    # Cron Jobs
    from mnlookup.mainapp.cron import run_spider
    scheduler.add_job('run_spider', run_spider,
                      trigger='cron', hour=0)

    return app
