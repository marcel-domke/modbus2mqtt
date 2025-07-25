from flask import Flask, render_template, request, Response, jsonify
import json
import os
import base64

DEFAULT_CONFIG = {
    "modbus": {
        "baud": 9600,
        "stopbits": 1,
        "bytesize": 8,
        "parity": "N",
        "timeout": 1,
        "device": 1
    },
    "mqtt": {
        "address": "127.0.0.1",
        "username": "",
        "password": "",
        "prefix": "modbus2mqtt"
    },
    "registers": [],
    "ui": {
        "password": "admin"
    }
}

class App:
    def __init__(self, config_file="config.json"):
        self.app = Flask(__name__)
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_routes()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return DEFAULT_CONFIG.copy()

        with open(self.config_file, 'r') as f:
            config = json.load(f)

        config.setdefault("ui", DEFAULT_CONFIG["ui"])
        config.setdefault("modbus", DEFAULT_CONFIG["modbus"])
        config.setdefault("mqtt", DEFAULT_CONFIG["mqtt"])
        config.setdefault("registers", DEFAULT_CONFIG["registers"])

        return config

    def save_config(self, data):
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
        self.config = data
    def check_auth(self, auth_header):
        expected_password = self.config.get("ui", {}).get("password", "admin")
        expected_username = "admin"

        if not auth_header or not auth_header.startswith("Basic "):
            return False

        try:
            encoded_credentials = auth_header.split(" ")[1]
            decoded = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            return False

        return username == expected_username and password == expected_password

    def authenticate(self):
        return Response(
            'Access denied.\n', 401,
            {'WWW-Authenticate': 'Basic realm="Login required"'}
        )

    def requires_auth(self, f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.headers.get("Authorization")
            if not self.check_auth(auth):
                return self.authenticate()
            return f(*args, **kwargs)
        return decorated

    def setup_routes(self):
        @self.app.route('/')
        @self.requires_auth
        def index():
            return render_template("index.html", config=self.config)

        @self.app.route('/save', methods=['POST'])

        @self.app.route('/restart', methods=['POST'])
        def restart_service():
            try:
                os.system('bash -c "/usr/bin/systemctl restart modbus2mqtt"')
                return jsonify({"status": "success"}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        @self.requires_auth
        def save():
            data = request.get_json()
            self.save_config(data)
            return jsonify({"status": "success"})

    def run(self):
        self.app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
