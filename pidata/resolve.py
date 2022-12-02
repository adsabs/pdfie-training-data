# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Tools for resolving reference strings into ADS bibcodes.

Environment variables of note:

- ``PDFIE_RESOLVER_DB_PATH`` - the path to the local resolver database
- ``ADS_DEV_KEY`` - to actually resolve

"""

import argparse
import os
import time
import typing

from . import util

__all__ = ["get_resolver_items"]


RESOLVER_DB_PATH = util.optional_envpath("PDFIE_RESOLVER_DB_PATH")


def get_resolver_items() -> typing.Tuple[
    "ads_ref_extract.resolver_cache.ResolverCache", "logging.Logger", float
]:
    try:
        from ads_ref_extract.classic_analytics import SUCCESSFUL_RESOLUTION_THRESHOLD
        from ads_ref_extract.resolver_cache import ResolverCache
        from ads_ref_extract.utils import get_quick_logger
    except ImportError as e:
        util.die(f"unable to import from `ads_ref_extract`: {e}")

    cache = ResolverCache(str(RESOLVER_DB_PATH))
    logger = get_quick_logger("pidata.resolve")
    return (cache, logger, SUCCESSFUL_RESOLUTION_THRESHOLD)


def main():
    from . import scan

    parser = argparse.ArgumentParser()
    _settings = parser.parse_args()
    cache, logger, SUCCESSFUL_RESOLUTION_THRESHOLD = get_resolver_items()

    # Read in everything. Buffer it *all* to try to maximize efficiency of our
    # usage of the resolver microservice.

    docs = []
    to_resolve = {}

    for doc in scan(rs=True):
        with open(doc.ext_path(".rs.txt"), "rt") as f:
            refstrings = [s.rstrip() for s in f]

        try:
            with open(doc.ext_path(".bc.txt"), "rt") as f:
                bcstrings = [s.rstrip() for s in f]
        except FileNotFoundError:
            bcstrings = [""] * len(refstrings)

        if len(bcstrings) != len(refstrings):
            util.warn(f"ignoring `{doc.global_id}`: len(refstrings) != len(bcstrings)")
            continue

        for idx, (refstring, bcstring) in enumerate(zip(refstrings, bcstrings)):
            if not bcstring or bcstring.startswith("..................."):
                to_resolve.setdefault(refstring, []).append((len(docs), idx))

        docs.append((doc, refstrings, bcstrings))

    print(f"Scanned {len(docs)} documents with refstrings")
    print(f"There are {len(to_resolve)} refstrings to investigate")
    print(f"{cache.count_need_rpc(to_resolve.keys())} need RPC")

    # Do it!

    resolved = cache.resolve(to_resolve.keys(), logger=logger)

    # Update internal data structures

    datecode = time.strftime("%Y-%m-%d")
    n_updated = 0

    for rs, info in resolved.items():
        bc = (
            info.bibcode
            if info.score > SUCCESSFUL_RESOLUTION_THRESHOLD
            else "..................."
        )
        bcstring = f"{bc} {datecode}"

        for doc_idx, ref_idx in to_resolve[rs]:
            docs[doc_idx][2][ref_idx] = bcstring
            n_updated += 1

    # Rewrite

    print(f"Rewriting bibcode files with {n_updated} new entries ...")

    for doc, refstrings, bcstrings in docs:
        with open(doc.ext_path(".bc.txt"), "wt") as f:
            for bcstring in bcstrings:
                print(bcstring, file=f)

    print("All done.")


if __name__ == "__main__":
    main()
