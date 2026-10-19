import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault("DB_PATH", str(pathlib.Path(tempfile.mkdtemp()) / "test.db"))
os.environ.setdefault("JWT_SECRET", "test-secret")
