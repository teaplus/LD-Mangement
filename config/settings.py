import json
import os

class Settings:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

    @property
    def ldplayer_path(self):
        return self.config['ldplayer']['path']

    @property
    def default_properties(self):
        return self.config['ldplayer']['default_properties']

    @property
    def max_instances(self):
        return self.config['instances']['max_count']

settings = Settings()