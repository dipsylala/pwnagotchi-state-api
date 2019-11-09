import logging
import os
import pwnagotchi.plugins as plugins
from flask import jsonify, Response
from pathlib import Path


class StateApi(plugins.Plugin):
    __name__ = 'state-api'
    __author__ = 'Dipsylala on Github'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Returns state.html if called with no parameters, otherwise sends JSON'

    DISPLAY = None
    AGENT = None

    def __init__(self):
        logging.debug("State API plugin created")
        self.display_state = None

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        if path is None or path == '':
            return Response(Path(os.path.dirname(os.path.realpath(__file__)) + '/state.html').read_text(), 'text/html')

        if self.DISPLAY is None or self.AGENT is None:
            return jsonify({"initialised": "false"})

        result = {
            "status": self.DISPLAY.get('status'),
            "channel": self.DISPLAY.get('channel'),
            "aps": self.DISPLAY.get('aps'),
            "uptime": self.DISPLAY.get('uptime'),
            "mode": self.DISPLAY.get('mode'),
            "name": self.DISPLAY.get('name'),
            "face": self.DISPLAY.get('face'),
            "friend_face": self.DISPLAY.get('friend_face'),
            "friend_name": self.DISPLAY.get('friend_name'),
            "shakes": self.DISPLAY.get('shakes')
        }

        return jsonify(result)

    # called when the plugin is loaded
    def on_loaded(self):
        logging.warning("State API loaded")

    def on_ui_update(self, ui):
        self.DISPLAY = ui

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info("unit is ready")
        self.AGENT = agent

