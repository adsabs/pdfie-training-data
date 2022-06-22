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
ingest_stream_to_local_data
make_random_index
nbytes_and_sha256_of_path
optional_envpath
try_local_data_path
""".split()

import hashlib
import os.path
from pathlib import Path
import random
import tempfile
from typing import BinaryIO, IO, Optional, Tuple, Union


# Path helpers

# cf. https://stackoverflow.com/questions/53418046/
AnyPath = Union[str, bytes, os.PathLike]


def envpath(env_var_name: str, default: str) -> Path:
    return Path(os.environ.get(env_var_name, default))


def optional_envpath(env_var_name: str) -> Optional[Path]:
    v = os.environ.get(env_var_name)
    if v is None:
        return None
    return Path(v)


# ADS integration helpers


ADS_REFERENCES_PREFIX = envpath("ADS_REFERENCES", "/proj/ads/references")
ADS_FULLTEXT_PREFIX = envpath("ADS_FULLTEXT", "/proj/ads/fulltext")
ADS_ABSTRACTS_PREFIX = envpath("ADS_ABSTRACTS", "/proj/ads/abstracts")
ADS_FULLTEXT_LINKS_PATH = ADS_ABSTRACTS_PREFIX / "config/links/fulltext/all.links"


# Ingest/indexing helpers


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


# Local PDF database helpers

LOCAL_DATA_PREFIX = optional_envpath("PDFIE_LOCAL_DATA")


def try_local_data_path(hexdigest: str, **kwargs) -> Optional[IO]:
    """
    Try to fetch a data file from the local database.

    Files are identified by their SHA256 digest in a standard content-based
    addressing scheme.

    The database location is given by the environment variable
    $PDFIE_LOCAL_DATA. If it is unset, all attempts to fetch files will fail,
    indicated by a None return value.

    kwargs are passed to ``pathlib.Path.open()`` to allow customization of the
    way that the file is opened.
    """

    assert len(hexdigest) == 64, f"{hexdigest!r} not a SHA256 hex digest?"

    if LOCAL_DATA_PREFIX is None:
        return None

    path = LOCAL_DATA_PREFIX / hexdigest[:2] / hexdigest[2:]

    try:
        return path.open(**kwargs)
    except FileNotFoundError:
        return None


def ingest_stream_to_local_data(stream: BinaryIO) -> Tuple[int, str, Path]:
    """
    Ingest a file into the local database.

    The database location is given by the environment variable
    $PDFIE_LOCAL_DATA. If it is unset, an exception will be raised.

    Files are identified by their SHA256 digest in a standard content-based
    addressing scheme, which is why this function's only argument is the stream
    itself, which should be opened in binary mode. The data will be copied into
    the local database tree.

    The return value is a tuple of ``(n_bytes, hexdigest, db_path)``.
    """

    if LOCAL_DATA_PREFIX is None:
        raise Exception(
            "cannot ingest into local database if $PDFIE_LOCAL_DATA is unset"
        )

    # Stream into a temporary path inside the database and calculate the SHA256.
    #
    # NOTE: we leave the tempfile lying around if ingest fails; could be useful for debugging?

    b = bytearray(128 * 1024)
    mv = memoryview(b)
    h = hashlib.sha256()
    n_bytes = 0

    with tempfile.NamedTemporaryFile(
        dir=LOCAL_DATA_PREFIX, delete=False, prefix="ingest"
    ) as ftmp:
        tmp_path = ftmp.name

        while n := stream.readinto(mv):
            n_bytes += n
            h.update(mv[:n])
            ftmp.write(mv[:n])

    # Now determine the final path and move it there.

    hexdigest = h.hexdigest()
    p = LOCAL_DATA_PREFIX / hexdigest[:2]
    p.mkdir(exist_ok=True)

    p = p / hexdigest[2:]
    Path(tmp_path).rename(p)

    return (n_bytes, hexdigest, p)
