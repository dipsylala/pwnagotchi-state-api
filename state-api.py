import logging
import pwnagotchi.plugins as plugins
import pwnagotchi
import pwngotchi.utils as utils
from flask import jsonify, Response, send_file, render_template, abort
import pwnagotchi.grid as grid
import pwnagotchi.ui.web as web

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

    def _return_json(self):
        if self.DISPLAY is None:
            return jsonify({"initialised": "false"})

        # All these fall under the local API
        # https://pwnagotchi.ai/api/local/
        # Typically on http://127.0.0.1:8666

        total_messages = "-"
        unread_messages = "-"
        mesh_data = None
        mesh_peers = None

        grid_memory = grid.memory()

        try:
            if grid.is_connected:
                mesh_data = grid.call("/mesh/data")

                messages = grid.inbox()
                total_messages = len(messages)
                unread_messages = len([m for m in messages if m['seen_at'] is None])
        except Exception as e:
            logging.exception('error while reading state-api: %s' % str(e))

        peers = []
        for peer in grid_memory:
            peers.append({
                "fingerprint": peer.advertisement.fingerprint,
                "name": peer.advertisement.name,
                "face": peer.advertisement.face,
                "pwnd_run": peer.advertisement.pwnd_run,
                "pwnd_tot": peer.advertisement.pwnd_tot,
            })

        handshakes_display = self.DISPLAY.get('shakes').splt(" ")
        # Need a better way of getting this rather than referencing the display
        pwnd_run = handshakes_display[0]
        pwnd_tot = utils.total_unique_handshakes(self._config['bettercap']['handshakes'])

        result = {
            "fingerprint": mesh_data["identity"],
            "epoch": "*" if mesh_data is None else mesh_data["epoch"],
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
            "pwnd_run": pwnd_run,
            "pwnd_tot": pwnd_tot,
            "version": pwnagotchi.version,
            "memory": pwnagotchi.mem_usage(),   # Scale 0-1
            "cpu": pwnagotchi.cpu_load(),       # Scale 0-1
            "temperature": pwnagotchi.temperature()  # Degrees C
        }

        return jsonify(result)

    def _return_png(self):
        with web.frame_lock:
            return send_file(web.frame_path, mimetype="image/png")

    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template/render_template_string)
    def on_webhook(self, path, request):
        if request.method != "GET":
            return abort(405)

        if path is None or path == "":
            theme = "theme-default.html"

            if "theme" in self.options:
                theme = "theme-" + self.options["theme"] + ".html"

            return render_template(theme)

        if path not in ["json", "png"]:
            return abort(415)

        if path == "png":
            return self._return_png()

        return self._return_json()

    # called when the plugin is loaded
    def on_loaded(self):
        logging.warning("State API loaded")

    def on_ui_update(self, ui):
        self.DISPLAY = ui

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self.AGENT = agent
