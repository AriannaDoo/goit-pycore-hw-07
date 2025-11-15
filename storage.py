import pickle
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_PATH = DATA_DIR / "addressbook.pkl"


def save_data(book, filename: Path = DEFAULT_PATH):
    with open(filename, "wb") as fh:
        pickle.dump(book, fh)


def load_data(filename: Path = DEFAULT_PATH):
    if filename.exists():
        with open(filename, "rb") as fh:
            return pickle.load(fh)
    return None
