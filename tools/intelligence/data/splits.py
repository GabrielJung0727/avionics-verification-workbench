"""Non-random splits.

The dataset contract forbids random splits because it leaks information
across campaign families (parameter neighbours look almost identical so a
random split inflates accuracy). Phase B uses split_by_key (e.g.
``campaign_family``) or split_by_date.
"""
from __future__ import annotations
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def split_by_key(records: list[T], key_fn: Callable[[T], str],
                 holdout_keys: Iterable[str]
                 ) -> tuple[list[T], list[T]]:
    holdout = set(holdout_keys)
    train = [r for r in records if key_fn(r) not in holdout]
    test = [r for r in records if key_fn(r) in holdout]
    return train, test


def split_by_date(records: list[T], key_fn: Callable[[T], str],
                  cutoff_iso: str
                  ) -> tuple[list[T], list[T]]:
    train = [r for r in records if key_fn(r) < cutoff_iso]
    test = [r for r in records if key_fn(r) >= cutoff_iso]
    return train, test
