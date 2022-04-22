# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Scoring PDF processing results.
"""

from pathlib import Path
import re
from typing import Generator, Tuple

from . import scan_for_ext

# Is this dumb? Trying to weight the importance of getting the separation right.
# I think it makes life a lot easier overall to treat all of the references as
# one big string, though, since that gets us out of the business of trying to
# align across missing whole refstrings, etc.
REF_SEP_TAG = "<SEP1> <SEP2> <SEP3>"


def load_rs_data(stream) -> str:
    """
    Load a ``.rs.txt`` formatted file into a string for scoring.
    """
    def linewords():
        first = True

        for line in stream:
            if first:
                first = False
            else:
                yield REF_SEP_TAG

            yield from line.split()

    return ' '.join(linewords())


_LEADING_REF_NUM_TEXT = re.compile(r"^(\[\d+\]|\(\d+\)|\d+\.\s)\s*")

def load_ads_refs_raw_data(stream) -> str:
    """
    Load a ``.raw`` formatted file as used in the ADS references
    tree.
    """
    def linewords():
        _bibcode = stream.readline()
        zee = stream.readline()
        assert zee.strip() == "%Z"

        first = True

        for line in stream:
            if first:
                first = False
            else:
                yield REF_SEP_TAG

            # Strip leading reference number text.
            line = _LEADING_REF_NUM_TEXT.sub("", line)

            yield from line.split()

    return ' '.join(linewords())


_WER_TRANSFORM = None

def score_wer(truth: str, hypothesis: str) -> float:
    """
    Score with a Word Error Rate.

    Perfect agreement yields a WER of zero.
    """

    global _WER_TRANSFORM

    import jiwer

    if _WER_TRANSFORM is None:
        _WER_TRANSFORM = jiwer.Compose([
            jiwer.ToLowerCase(),
            jiwer.Strip(),
            jiwer.RemoveWhiteSpace(replace_by_space=True),
            jiwer.RemoveMultipleSpaces(),
            jiwer.ReduceToListOfListOfWords(word_delimiter=" ")
        ])

    return jiwer.wer(truth, hypothesis, truth_transform=_WER_TRANSFORM, hypothesis_transform=_WER_TRANSFORM)


class RefstringDatabase(object):
    root: Path

    def __init__(self, root: Path):
        self.root = Path(root)

    def scan(self) -> Generator[str, None, None]:
        for gid, path in scan_for_ext(self.root, ".rs.txt"):
            yield gid

    def load(self, gid: str) -> str:
        with (self.root / (gid + ".rs.txt")).open("rt") as f:
            return load_rs_data(f)


class AdsRefsRawDatabase(object):
    root: Path

    def __init__(self, root: Path):
        self.root = Path(root)

    def scan(self) -> Generator[str, None, None]:
        for gid, path in scan_for_ext(self.root, ".raw"):
            yield gid

    def load(self, gid: str) -> str:
        with (self.root / (gid + ".raw")).open("rt") as f:
            return load_ads_refs_raw_data(f)


def wer_scores_from_ground_truth(gt_db, hy_db) -> Generator[Tuple[str, float], None, None]:
    for gid in gt_db.scan():
        ground_truth = gt_db.load(gid)

        try:
            hypothesis = hy_db.load(gid)
            score = score_wer(ground_truth, hypothesis)
        except FileNotFoundError:
            score = 1.0

        yield (gid, score)
