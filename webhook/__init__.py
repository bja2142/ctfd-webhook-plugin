import os
from json import load as json_load
from .hooks import load_hooks
from .executor import WebhookExecutor
from flask import current_app

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json_load(open(f"{PLUGIN_PATH}/config.json"))


def load(app):
    with app.app_context():
        current_app.webhook_plugin_executor = WebhookExecutor()
        current_app.webhook_plugin_secret = CONFIG["webhook_secret"]
        current_app.webhook_plugin_url = CONFIG["webhook_url"]
        current_app.webhook_plugin_levels = CONFIG["point_levels"]
        current_app.webhook_report_all_solves = CONFIG["report_all_solves"]
        if not CONFIG["report_all_solves"]:
            current_app.webhook_reported_solves = CONFIG["reported_solves"]
    load_hooks()

