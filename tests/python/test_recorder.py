import unittest
from . import _paths  # noqa: F401

from avx_sim.recorder import Recorder


class TestRecorder(unittest.TestCase):

    def test_hash_stable(self):
        r1 = Recorder()
        r2 = Recorder()
        for i in range(5):
            r1.append(i * 1000, "A429", "MSG-001", b"\x01\x02\x03\x04")
            r2.append(i * 1000, "A429", "MSG-001", b"\x01\x02\x03\x04")
        self.assertEqual(r1.sha256(), r2.sha256())

    def test_hash_changes_on_diff(self):
        r1 = Recorder()
        r2 = Recorder()
        r1.append(0, "A429", "MSG-001", b"\x00")
        r2.append(0, "A429", "MSG-001", b"\x01")
        self.assertNotEqual(r1.sha256(), r2.sha256())


if __name__ == "__main__":
    unittest.main()
