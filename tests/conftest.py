import json
import os

# config reads the environment at import time
os.environ.setdefault("BOT_TOKEN", "123456:TEST")

LOTTIE = json.dumps(
    {"v": "5.5.2", "fr": 30, "ip": 0, "op": 1, "w": 512, "h": 512, "nm": "t", "ddd": 0, "assets": [], "layers": []}
)
