#! /usr/bin/env python3
# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Utilities.
"""

__all__ = """
ADS_REFERENCES_PREFIX
ADS_FULLTEXT_PREFIX
ADS_ABSTRACTS_PREFIX
ADS_FULLTEXT_LINKS_PATH
AnyPath
envpath
make_random_index
nbytes_and_sha256_of_path
""".split()

import hashlib
import os.path
from pathlib import Path
import random
from typing import Union, Tuple


# cf. https://stackoverflow.com/questions/53418046/
AnyPath = Union[str, bytes, os.PathLike]


def envpath(env_var_name: str, default: str) -> Path:
    return Path(os.environ.get(env_var_name, default))


ADS_REFERENCES_PREFIX = envpath("ADS_REFERENCES", "/proj/ads/references")
ADS_FULLTEXT_PREFIX = envpath("ADS_FULLTEXT", "/proj/ads/fulltext")
ADS_ABSTRACTS_PREFIX = envpath("ADS_ABSTRACTS", "/proj/ads/abstracts")
ADS_FULLTEXT_LINKS_PATH = ADS_ABSTRACTS_PREFIX / "config/links/fulltext/all.links"


def nbytes_and_sha256_of_path(p: AnyPath) -> Tuple[int, str]:
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    h = hashlib.sha256()
    n_bytes = 0

    with open(p, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
            n_bytes += n

    return (n_bytes, h.hexdigest())


def make_random_index() -> int:
    return random.randint(0, 999999)
