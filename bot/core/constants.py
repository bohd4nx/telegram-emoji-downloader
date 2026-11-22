from pathlib import Path

ROOT_PATH: Path = Path(__file__).resolve().parents[2]
LOCALES_PATH: str = str(ROOT_PATH / "locales" / "{locale}" / "LC_MESSAGES")

POLLING_TIMEOUT: int = 30
POLLING_TASKS_CONCURRENCY_LIMIT: int = 100
