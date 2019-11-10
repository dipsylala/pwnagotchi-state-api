import logging
import os
import pwnagotchi.plugins as plugins
import pwnagotchi
from flask import jsonify, Response
from pathlib import Path
import pwnagotchi.grid as grid

class StateApi(plugins.Plugin):
    __name__ = 'state-api'
    __author__ = 'https://github.com/dipsylala'
    __version__ = '0.9.0'
    __license__ = 'GPL3'
    __description__ = 'Provides JSON state data or a default page'

    DISPLAY = None
    AGENT = None

    def __init__(self):
        logging.debug("State API plugin created")
        self.display_state = None


    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        if path is None or path == "":
            theme = "state-default.html"

            if 'theme' in self.options:
                theme = "state-" + self.options["theme"] + ".html"

            return Response(Path(os.path.dirname(os.path.realpath(__file__)) + '/state-api/' + theme).read_text(), 'text/html')

        if path != "json":
            return jsonify({"message": "Unsupported Media Type"}), 415

        if self.DISPLAY is None:
            return jsonify({"initialised": "false"})

        mesh_data = grid.call("/mesh/data")
        mesh_peers = grid.peers()
        # inbox = grid.inbox()

        peers = []
        for peer in mesh_peers:
            peers.append({
                "identity": peer["advertisement"]["identity"],
                "name": peer["advertisement"]["name"],
                "face": peer["advertisement"]["face"],
                "pwnd_run": peer["advertisement"]["pwnd_run"],
                "pwnd_tot": peer["advertisement"]["pwnd_tot"],
            })

        result = {
            "identity": mesh_data["identity"],
            "epoch": mesh_data["epoch"],
            "status": self.DISPLAY.get('status'),
            "channel": self.DISPLAY.get('channel'),
            "aps": self.DISPLAY.get('aps'),
            "uptime": self.DISPLAY.get('uptime'),
            "mode": self.DISPLAY.get('mode'),
            "name": mesh_data["name"],
            "face": mesh_data["face"],
            "num_peers": len(mesh_peers),
            "peers": peers,
            "friend_face_text": self.DISPLAY.get('friend_face'),
            "friend_name_text": self.DISPLAY.get('friend_name'),
            "pwnd_run": mesh_data["pwnd_run"],
            "pwnd_tot": mesh_data["pwnd_tot"],
            "version": pwnagotchi.version,
            "memory": pwnagotchi.mem_usage(),   # Scale 0-1
            "cpu": pwnagotchi.cpu_load(),       # Scale 0-1
            "temperature": pwnagotchi.temperature() # Degrees C
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
