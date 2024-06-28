import pathlib


class settings:
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    db_url = f"sqlite:///{base_dir}/file-tag.db"
    autocommit = False
    autoflush = False
    connect_args = {
        "check_same_thread": False
    }


setting = settings()
