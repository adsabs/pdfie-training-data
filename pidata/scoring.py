# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Scoring PDF processing results.
"""

import argparse
from pathlib import Path
import re
from typing import Generator, Iterable, FrozenSet, List, Tuple

from . import scan_for_ext
from .resolve import get_resolver_items

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


def load_bc_data(stream) -> FrozenSet[str]:
    """
    Load a ``.bc.txt`` formatted file into a set of bibcodes.
    """
    bibcodes = (line.split(None, 1)[0] for line in stream)
    return frozenset(bc for bc in bibcodes if bc != "...................")


_LEADING_REF_NUM_TEXT = re.compile(r"^(\[\d+\]|\(\d+\)|\d+\.\s)\s*")


def _ads_refs_raw_lines(stream) -> Generator[str, None, None]:
    """
    Load clean-up lines from a ``.raw`` formatted file as used in the ADS
    references tree.
    """
    _bibcode = stream.readline()
    zee = stream.readline()
    assert zee.strip() == b"%Z"

    for line in stream:
        line = line.decode("utf-8", "replace")
        # Strip leading reference number text.
        yield _LEADING_REF_NUM_TEXT.sub("", line)


def load_ads_refs_raw_data(stream) -> str:
    """
    Load a ``.raw`` formatted file as used in the ADS references
    tree.
    """

    def linewords():
        first = True

        for line in _ads_refs_raw_lines(stream):
            if first:
                first = False
            else:
                yield REF_SEP_TAG

            yield from line.split()

    return " ".join(linewords())


def normalize_refstring(rs: str) -> str:
    # XXX this is duplicating ads_ref_extract.classic_analytics._maybe_load_raw_file

    from ads_ref_extract.normalize import refstring_normalizer, to_ascii

    MAX_RS_LEN = 512
    rs = rs.strip()
    rs = rs[:MAX_RS_LEN]
    rs = refstring_normalizer.normalize(rs)
    rs = to_ascii(rs)
    return rs


def load_ads_refs_raw_resolution_inputs(stream) -> Generator[str, None, None]:
    for line in _ads_refs_raw_lines(stream):
        yield normalize_refstring(line)


def load_ads_refs_raw_bibcodes(stream, cache, threshold, logger) -> FrozenSet[str]:
    # This is not going to make efficient use of the resolver if there are lots
    # of resolutions to do. Better to load *all* of the refstrings and resolve
    # all of them in a bigger batch.

    refstrings = frozenset(load_ads_refs_raw_resolution_inputs(stream))
    resolved = cache.resolve(refstrings, logger=logger)
    return frozenset(ri.bibcode for ri in resolved.values() if ri.score > threshold)


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

    def load_as_merged_string(self, gid: str) -> str:
        with (self.root / (gid + ".rs.txt")).open("rt") as f:
            return load_rs_data(f)

    def load_as_bibcodes(self, gid: str) -> FrozenSet[str]:
        with (self.root / (gid + ".bc.txt")).open("rt") as f:
            try:
                return load_bc_data(f)
            except Exception as e:
                raise Exception(f"failed to load refstring GID {gid}") from e

    def load_as_resolution_inputs(self, gid: str) -> List[str]:
        with (self.root / (gid + ".rs.txt")).open("rt") as f:
            return list(normalize_refstring(l) for l in f)


class AdsRefsRawDatabase(object):
    root: Path

    def __init__(self, root: Path):
        self.root = Path(root)

    def scan(self) -> Generator[str, None, None]:
        for gid, path in scan_for_ext(self.root, ".raw"):
            yield gid

    def load_as_merged_string(self, gid: str) -> str:
        with (self.root / (gid + ".raw")).open("rb") as f:
            return load_ads_refs_raw_data(f)

    def load_as_bibcodes(
        self, gid: str, cache, threshold: float, logger
    ) -> FrozenSet[str]:
        with (self.root / (gid + ".raw")).open("rb") as f:
            return load_ads_refs_raw_bibcodes(f, cache, threshold, logger)

    def load_as_resolution_inputs(self, gid: str) -> List[str]:
        with (self.root / (gid + ".raw")).open("rb") as f:
            return list(load_ads_refs_raw_resolution_inputs(f))


def wer_scores_from_ground_truth(
    gt_db, hy_db
) -> Generator[Tuple[str, float], None, None]:
    for gid in gt_db.scan():
        ground_truth = gt_db.load_as_merged_string(gid)

        try:
            hypothesis = hy_db.load_as_merged_string(gid)
            # score = score_wer(ground_truth, hypothesis)
            score = score_lost_refs(ground_truth, hypothesis)
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

    # print("Scores based on Word Error Rate metric:")
    # _summarize_scores(scores)
    _worst_scores(scores)


def _do_score_bibcodes(settings):
    gt_path = Path(settings.export_dir) / "references" / "groundtruth" / "pdfietd"
    hy_path = Path(settings.run_dir) / "references" / "sources" / "pdfietd"

    gt_db = RefstringDatabase(gt_path)
    hy_db = AdsRefsRawDatabase(hy_path)

    cache, logger, threshold = get_resolver_items()

    n_items = 0
    n_possible = 0
    n_extracted = 0
    n_true_pos = 0
    n_false_pos = 0
    n_false_neg = 0

    for gid in gt_db.scan():
        try:
            ground_truth = gt_db.load_as_bibcodes(gid)
        except FileNotFoundError:
            continue

        try:
            hypothesis = hy_db.load_as_bibcodes(gid, cache, threshold, logger)
        except FileNotFoundError:
            hypothesis = frozenset(())

        n_items += 1
        n_possible += len(ground_truth)
        n_extracted += len(hypothesis)
        n_true_pos += len(hypothesis & ground_truth)
        n_false_pos += len(hypothesis - ground_truth)
        n_false_neg += len(ground_truth - hypothesis)

    print(f"Examined {n_items} items")
    print(f"Number of possible bibcodes: {n_possible}")
    print(f"Number of extracted bibcodes: {n_extracted}")
    print(
        f"Number true positives (found): {n_true_pos} = {100 * n_true_pos / n_possible:.1f}%"
    )
    print(
        f"Number false positives (bogus): {n_false_pos} = {100 * n_false_pos / n_possible:.1f}%"
    )
    print(
        f"Number false negatives (missed): {n_false_neg} = {100 * n_false_neg / n_possible:.1f}%"
    )
    print(
        f"F1 score: {n_true_pos / (n_true_pos + 0.5 * (n_false_pos + n_false_neg)):.3f}"
    )


def _do_resolve_bibcodes(settings):
    gt_path = Path(settings.export_dir) / "references" / "groundtruth" / "pdfietd"
    hy_path = Path(settings.run_dir) / "references" / "sources" / "pdfietd"

    gt_db = RefstringDatabase(gt_path)
    hy_db = AdsRefsRawDatabase(hy_path)

    cache, logger, _threshold = get_resolver_items()

    def refstrings():
        for gid in gt_db.scan():
            try:
                _check_exists = gt_db.load_as_bibcodes(gid)
                hy_strings = hy_db.load_as_resolution_inputs(gid)
            except FileNotFoundError:
                continue

            yield from hy_strings

    refstrings = frozenset(refstrings())
    cache.resolve(refstrings, logger=logger)


def entrypoint():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="subcommand")

    p = commands.add_parser("resolve-bibcodes")
    # XXXX redundancy
    p.add_argument(
        "export_dir",
        metavar="PATH",
        help="Path to the results directory created by export_arxiv",
    )
    p.add_argument(
        "run_dir",
        metavar="PATH",
        help="Path to a results directory",
    )

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

    p = commands.add_parser("score-bibcodes")
    # XXXX redundancy
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

    if settings.subcommand == "resolve-bibcodes":
        _do_resolve_bibcodes(settings)
    elif settings.subcommand == "score-arxiv-extractor":
        _do_score_arxiv_extractor(settings)
    elif settings.subcommand == "score-bibcodes":
        _do_score_bibcodes(settings)
    else:
        raise Exception(
            f"unknown subcommand `{settings.subcommand}`; run without arguments for a list"
        )


if __name__ == "__main__":
    entrypoint()
