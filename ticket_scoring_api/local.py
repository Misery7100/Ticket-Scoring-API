import os
import yaml

from pathlib import Path

from ticket_scoring_api.utils import dotdict

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent.parent

with open(os.path.join(BASE_DIR, 'secret/credentials.yml'), 'r') as stream:
    credentials = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'secret/databases.yml'), 'r') as stream:
    databases = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'secret/staticdata.yml'), 'r') as stream:
    staticdata = dotdict(yaml.load(stream, Loader=yaml.Loader))

