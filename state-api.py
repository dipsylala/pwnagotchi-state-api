import logging
import requests
import pwnagotchi
from pwnagotchi import plugins
from pwnagotchi import utils
from pwnagotchi import grid
from pwnagotchi.ui import web
from requests.exceptions import HTTPError
from flask import jsonify, send_file, render_template, abort


class StateApi(plugins.Plugin):
    __name__ = 'state-api'
    __author__ = 'https://github.com/dipsylala'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Provides JSON state data or a default page'

    DISPLAY = None
    AGENT = None
    _epoch_data = None

    def __init__(self):
        logging.debug("State API plugin created")
        self.display_state = None

    def _return_json(self):
        if self.DISPLAY is None:
            return jsonify({"initialised": "false"})

        # All these fall under the local API
        # https://pwnagotchi.ai/api/local/
        # Typically on http://127.0.0.1:8666
        # BUT the local API can trigger calls to the wider grid
        # so bear in mind that grid calls could fail

        # TODO: Break this up into function calls! Keep it SOLID.

        total_messages = "-"
        unread_messages = "-"

        peers_response = None
        try:
            response = requests.get('http://0.0.0.0:8666/api/v1/mesh/peers')
            peers_response = response.json()
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            logging.error(f'Other error occurred: {err}')

        peers = []
        for peer in peers_response:
            peers.append({
                "fingerprint": peer['advertisement']['identity'],
                "name": peer['advertisement']['name'],
                "face": peer['advertisement']['face'],
                "pwnd_run": peer['advertisement']['pwnd_run'],
                "pwnd_tot": peer['advertisement']['pwnd_tot']
            })

        mesh_data_response = None
        try:
            response = requests.get('http://0.0.0.0:8666/api/v1/mesh/data')
            mesh_data_response = response.json()
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            logging.error(f'Other error occurred: {err}')

        # Get mail data (if connected to internet)
        try:
            if grid.is_connected:
                messages = grid.inbox()
                total_messages = len(messages)
                unread_messages = len([m for m in messages if m['seen_at'] is None])
        except Exception as e:
            logging.exception('error while reading state-api: %s' % str(e))

        # TODO: Need a better way of getting this rather than referencing the display
        handshakes_display = self.DISPLAY.get('shakes').split(" ", 2)
        # In general, any underlying state within the state machine should be used.
        # The display is fluid and unreliable.
        pwnd_run = handshakes_display[0]
        pwnd_tot = utils.total_unique_handshakes(self.AGENT.config()['bettercap']['handshakes'])

        pwnd_last = None
        if len(handshakes_display) > 2:
            pwnd_last = handshakes_display[2][1:-1]

        result = {
            "fingerprint": self.AGENT.fingerprint(),
            "epoch": "-" if mesh_data_response is None else mesh_data_response["epoch"],
            "status": self.DISPLAY.get('status'),
            "channel_text": self.DISPLAY.get('channel'),
            "aps_text": self.DISPLAY.get('aps'),
            "apt_tot": self.AGENT.get_total_aps(),
            "aps_on_channel": self.AGENT.get_aps_on_channel(),
            "channel": self.AGENT.get_current_channel(),
            "uptime": self.DISPLAY.get('uptime'),
            "mode": self.DISPLAY.get('mode'),
            "name": pwnagotchi.name(),
            "face": self.DISPLAY.get('face'),
            "num_peers": len(peers),
            "peers": peers,
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "friend_face_text": self.DISPLAY.get('friend_face'),
            "friend_name_text": self.DISPLAY.get('friend_name'),
            "pwnd_last": pwnd_last,
            "pwnd_run": pwnd_run,
            "pwnd_tot": pwnd_tot,
            "version": pwnagotchi.__version__,
            "memory": pwnagotchi.mem_usage(),  # Scale 0-1
            "cpu": pwnagotchi.cpu_load(),  # Scale 0-1
            "temperature": pwnagotchi.temperature()  # Degrees C
        }

        # TODO See if there is any way of getting a list of plugins and their associated UI components
        # so we can incorporate it into the feedback.
        return jsonify(result)

    def _return_png(self):
        with web.frame_lock:
            return send_file(web.frame_path, mimetype="image/png")

    def on_webhook(self, path, request):
        if request.method != "GET":
            return abort(405)

        if path is None or path == "":
            theme = "theme-default.html"

            if "theme" in self.options:
                theme = "theme-" + self.options["theme"] + ".html"

            try:
                return render_template(theme)
            except Exception:
                return "Could not render the page. Did you put the JS and HTML where you should?<br/>Copy the contents of pwnagotchi-state-api/goes_in_ui_web to /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/web"

        if path not in ["json", "png"]:
            return abort(415)

        if path == "png":
            return self._return_png()

        return self._return_json()

    # called when the plugin is loaded
    def on_loaded(self):
        logging.info("State API loaded")

    def on_ui_update(self, ui):
        self.DISPLAY = ui

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self.AGENT = agent
