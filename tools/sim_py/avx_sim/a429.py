"""ARINC 429-lite encoder/decoder.

Layout (LSB → MSB):
  bits  0..7   label   (8 bits, transmitted LSB-first in real A429; we keep
                        the natural integer here for clarity)
  bits  8..9   SDI     (2 bits)
  bits 10..28  data    (19 bits, signed two's complement allowed)
  bits 29..30  SSM     (2 bits)
  bit  31      parity  (odd parity over bits 0..30)

This is a *lite* encoding intended for testability and recorder hashing,
not for hardware compatibility.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum

LABEL_MASK = 0xFF
SDI_MASK = 0x3
DATA_MASK = 0x7FFFF       # 19 bits
SSM_MASK = 0x3


class A429SSM(IntEnum):
    NORMAL = 0
    NO_COMP = 1
    FUNCT_TEST = 2
    FAILURE = 3


@dataclass(frozen=True)
class A429Word:
    label: int
    sdi: int
    data: int           # 19-bit signed
    ssm: A429SSM = A429SSM.NORMAL


def _odd_parity(value: int) -> int:
    v = value & 0x7FFFFFFF
    bits = bin(v).count("1")
    return 0 if (bits % 2 == 1) else 1


def encode_a429(word: A429Word) -> int:
    if not 0 <= word.label <= LABEL_MASK:
        raise ValueError("label out of range")
    if not 0 <= word.sdi <= SDI_MASK:
        raise ValueError("sdi out of range")
    # 19-bit signed range
    if not -(1 << 18) <= word.data < (1 << 18):
        raise ValueError("data out of 19-bit signed range")
    data19 = word.data & DATA_MASK
    ssm = int(word.ssm) & SSM_MASK
    raw = (word.label & LABEL_MASK)
    raw |= (word.sdi & SDI_MASK) << 8
    raw |= (data19 & DATA_MASK) << 10
    raw |= (ssm & SSM_MASK) << 29
    raw |= _odd_parity(raw) << 31
    return raw & 0xFFFFFFFF


def decode_a429(raw: int) -> A429Word:
    raw &= 0xFFFFFFFF
    parity_bit = (raw >> 31) & 1
    expected = _odd_parity(raw & 0x7FFFFFFF)
    if parity_bit != expected:
        raise ValueError("parity error")
    label = raw & LABEL_MASK
    sdi = (raw >> 8) & SDI_MASK
    data19 = (raw >> 10) & DATA_MASK
    if data19 & (1 << 18):
        data = data19 - (1 << 19)
    else:
        data = data19
    ssm = A429SSM((raw >> 29) & SSM_MASK)
    return A429Word(label=label, sdi=sdi, data=data, ssm=ssm)
