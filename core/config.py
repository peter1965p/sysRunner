import json
import yaml
from pathlib import Path

class ConfigEngine:
    def __init__(self, path: str):
        self.path = Path(path)
        self.data = {}

    def load(self):
        if self.path.suffix == ".yaml":
            self.data = yaml.safe_load(self.path.read_text())
        elif self.path.suffix == ".json":
            self.data = json.loads(self.path.read_text())
        else:
            raise ValueError("Unsupported config format")
        return self.data
