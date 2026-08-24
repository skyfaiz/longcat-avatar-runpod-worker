import base64
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


fake_runpod = types.SimpleNamespace(serverless=types.SimpleNamespace(start=lambda _: None))
sys.modules.setdefault("runpod", fake_runpod)
spec = importlib.util.spec_from_file_location("worker_handler", Path(__file__).with_name("handler.py"))
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


class HandlerTests(unittest.TestCase):
    def test_materialize_data_uri(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "input.bin"
            worker._materialize("data:x;base64," + base64.b64encode(b"ok").decode(), target)
            self.assertEqual(target.read_bytes(), b"ok")

    def test_validation(self) -> None:
        self.assertEqual(worker._validated({"prompt": "talk", "segments": 2}), ("talk", 2, "480p"))
        with self.assertRaises(ValueError):
            worker._validated({"prompt": "", "segments": 1})
        with self.assertRaises(ValueError):
            worker._validated({"prompt": "talk", "segments": 21})


if __name__ == "__main__":
    unittest.main()
