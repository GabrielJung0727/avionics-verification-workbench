import unittest
from . import _paths  # noqa: F401

from avx_sim.a429 import A429Word, A429SSM, encode_a429, decode_a429


class TestA429(unittest.TestCase):

    def test_round_trip(self):
        for label, sdi, data, ssm in [
            (0x10, 0, 12345, A429SSM.NORMAL),
            (0x20, 1, -100, A429SSM.NO_COMP),
            (0xFF, 3, 0, A429SSM.FAILURE),
            (0x00, 0, (1 << 18) - 1, A429SSM.NORMAL),
            (0x00, 0, -(1 << 18), A429SSM.NORMAL),
        ]:
            w = A429Word(label, sdi, data, ssm)
            raw = encode_a429(w)
            self.assertEqual(decode_a429(raw), w)

    def test_parity_error_detected(self):
        raw = encode_a429(A429Word(0x10, 0, 1234))
        flipped = raw ^ 1  # flip a data bit so parity no longer matches
        with self.assertRaises(ValueError):
            decode_a429(flipped)

    def test_range_validation(self):
        with self.assertRaises(ValueError):
            encode_a429(A429Word(0x100, 0, 0))   # label too big
        with self.assertRaises(ValueError):
            encode_a429(A429Word(0x10, 0, 1 << 18))  # data too big


if __name__ == "__main__":
    unittest.main()
