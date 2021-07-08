import os
import yaml

class ConfigHelper(object):
    def __init__(self):
        config = self.read_yml('config')
        self.url = config['deploy']['url']
        self.port = config['deploy']['port']
        self.protocol = config['deploy']['protocol']
        self.ca_path = config['deploy']['ca_path']

    @classmethod
    def read_yml(self, f):
        yml_path = os.path.join(os.path.dirname(__file__), "../config/%s.yml" % f)
        with open(yml_path,'r') as stream:
            return yaml.safe_load(stream)
