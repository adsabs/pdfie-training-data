# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Scoring PDF processing results.
"""

import argparse
from pathlib import Path
import re
from typing import Generator, Iterable, Tuple

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

    return " ".join(linewords())


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

    return " ".join(linewords())


_WER_TRANSFORM = None


def score_wer(truth: str, hypothesis: str) -> float:
    """
    Score with a Word Error Rate.

    Perfect agreement yields a WER of zero.
    """

    global _WER_TRANSFORM

    import jiwer

    if _WER_TRANSFORM is None:
        _WER_TRANSFORM = jiwer.Compose(
            [
                jiwer.ToLowerCase(),
                jiwer.Strip(),
                jiwer.RemoveWhiteSpace(replace_by_space=True),
                jiwer.RemoveMultipleSpaces(),
                jiwer.ReduceToListOfListOfWords(word_delimiter=" "),
            ]
        )

    return jiwer.wer(
        truth,
        hypothesis,
        truth_transform=_WER_TRANSFORM,
        hypothesis_transform=_WER_TRANSFORM,
    )


def score_lost_refs(truth: str, hypothesis: str) -> float:
    """
    Dumb hack to look for cases with segmentation issues.
    """
    n_refs_gt = truth.count(REF_SEP_TAG) + 1
    n_refs_hy = hypothesis.count(REF_SEP_TAG) + 1

    if n_refs_hy >= n_refs_gt:
        return 0.0

    return n_refs_gt - n_refs_hy


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


def wer_scores_from_ground_truth(
    gt_db, hy_db
) -> Generator[Tuple[str, float], None, None]:
    for gid in gt_db.scan():
        ground_truth = gt_db.load(gid)

        try:
            hypothesis = hy_db.load(gid)
            score = score_wer(ground_truth, hypothesis)
        except FileNotFoundError:
            score = 1.0

        yield (gid, score)


# CLI


def _summarize_scores(scores: Iterable[Tuple[str, float]]):
    """
    Need to think about what stats are the best here.
    """
    import numpy as np

    all = list(t[1] for t in scores)
    all = np.array(all)
    n_all = all.size
    print("  Number of items:", n_all)

    n_fail = (all == 1.0).sum()
    print(f"  Number of failures: {n_fail} = {100 * n_fail / n_all:.3}%")

    n_perf = (all == 0.0).sum()
    print(f"  Number of perfect extractions: {n_perf} = {100 * n_perf / n_all:.3}%")
    print(f"  Mean score: {all.mean():.2}")
    pct = np.percentile(all, [30, 50, 70, 90])
    pct = ", ".join(f"{x:.2}" for x in pct)
    print(f"  [30, 50, 70, 90]th percentiles: {pct}")


def _worst_scores(scores: Iterable[Tuple[str, float]]):
    scores = sorted(scores, reverse=True, key=lambda t: t[1])

    print("Worst scores:")
    print()

    for gid, score in scores[:30]:
        print(f"{gid:32} {score:.2f}")


def _do_score_arxiv_extractor(settings):
    gt_path = Path(settings.export_dir) / "references" / "groundtruth" / "pdfietd"
    hy_path = Path(settings.run_dir) / "references" / "sources" / "pdfietd"

    gt_db = RefstringDatabase(gt_path)
    hy_db = AdsRefsRawDatabase(hy_path)
    scores = wer_scores_from_ground_truth(gt_db, hy_db)

    print("Scores based on Word Error Rate metric:")
    _summarize_scores(scores)


def entrypoint():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="subcommand")

    p = commands.add_parser("score-arxiv-extractor")
    p.add_argument(
        "export_dir",
        metavar="PATH",
        help="Path to the results directory created by export_arxiv",
    )
    p.add_argument(
        "run_dir",
        metavar="PATH",
        help="Path to a results directory that reprocessed the export",
    )

    settings = parser.parse_args()
    if settings.subcommand is None:
        raise Exception("use a subcommand: score-arxiv-extractor")

    if settings.subcommand == "score-arxiv-extractor":
        _do_score_arxiv_extractor(settings)
    else:
        raise Exception(
            f"unknown subcommand `{settings.subcommand}`; run without arguments for a list"
        )


if __name__ == "__main__":
    entrypoint()
