"""Recorder replay round-trip tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.recorder import Recorder


class TestRecorderReplay(unittest.TestCase):

    def test_round_trip(self):
        r = Recorder()
        for i in range(10):
            r.append(i * 1000, "A429", f"MSG-00{i % 3}", bytes([i, i + 1]))
        data = r.to_bytes()
        r2 = Recorder.from_bytes(data)
        self.assertEqual(r.sha256(), r2.sha256())
        self.assertEqual(len(r2), len(r))

    def test_iter_replay_filters(self):
        r = Recorder()
        r.append(0, "A429", "MSG-001", b"")
        r.append(1, "AFDX", "MSG-004", b"")
        r.append(2, "A429", "MSG-002", b"")
        a429 = list(r.iter_replay(bus="A429"))
        self.assertEqual(len(a429), 2)
        msg001 = list(r.iter_replay(msg="MSG-001"))
        self.assertEqual(len(msg001), 1)

    def test_from_bytes_rejects_bad_magic(self):
        with self.assertRaises(ValueError):
            Recorder.from_bytes(b"GARBAGE\x00" + b"\x00" * 32)


if __name__ == "__main__":
    unittest.main()
