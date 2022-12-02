# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Export the database into a format suitable for use with the
arxiv-reference-extractor pipeline.

Environment variables to set:

- ``PDFIE_LOCAL_DATA`` for PDFs that need local copies
"""

import argparse
import contextlib
import os
from pathlib import Path
import shutil
import typing

from . import scan, util


class ArxivSession(object):
    er_path: Path
    er_handle: typing.TextIO
    fth_handle: typing.TextIO
    n: int

    def __init__(self, out_dir: Path, session_id: str):
        logs_dir = out_dir / "logs" / session_id
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.er_path = logs_dir / "extractrefs.out"
        self.er_handle = self.er_path.open("wt")
        self.fth_handle = (logs_dir / "fulltextharvest.out").open("wt")
        self.n = 0

    def append(self, bibcode: str, pdf_path: str, refs_path: str):
        print(pdf_path, refs_path, file=self.er_handle)
        print(pdf_path, bibcode, "fakeaccno", "fakesubdate", file=self.fth_handle)
        self.n += 1

    def close(self):
        if self.er_handle is not None:
            self.er_handle.close()
            print(f"Wrote {self.n} entries to `{self.er_path}`")
            self.er_handle = None

        if self.fth_handle is not None:
            self.fth_handle.close()
            self.fth_handle = None

    def __enter__(self):
        return self

    def __exit__(self, _etype, _evalue, _etraceback):
        self.close()
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ads-arxiv-fulltext-shadow",
        metavar="PATH",
        help="ArXiv reference extractor fulltext directory for custom symlinking (see script, sorry)",
    )
    parser.add_argument("out_dir")
    settings = parser.parse_args()

    out_dir = Path(settings.out_dir)

    fulltext_prefix = "pdfietd"

    docs = list(scan(rs=True, no_raster=True))
    print(f"Scan yielded {len(docs)} documents.")

    # Export to the log files that feed the Arxiv pipeline. We have an "all"
    # session that covers all documents, and a "bibcodes" session that only
    # includes those with bibcode ground-truth information.

    fake_bibcode_serial = 0

    with contextlib.ExitStack() as stack:
        all = stack.enter_context(ArxivSession(out_dir, "all"))
        bibcodes = stack.enter_context(ArxivSession(out_dir, "bibcodes"))

        for doc in docs:
            arxiv_id = doc.global_id.replace(".", "_")

            if doc.bibcode:
                bibcode = doc.bibcode
            else:
                bibcode = "9999" + str(fake_bibcode_serial).rjust(14, ".") + "."
                fake_bibcode_serial += 1

            fake_pdf_path = f"{fulltext_prefix}/{arxiv_id}.pdf"
            refs_path = os.path.join(
                util.ADS_REFERENCES_PREFIX,
                "sources",
                fulltext_prefix,
                arxiv_id + ".raw",
            )

            all.append(bibcode, fake_pdf_path, refs_path)

            if ".bc.txt" in doc.extensions:
                bibcodes.append(bibcode, fake_pdf_path, refs_path)

    # Copy out the ground-truth refstring and bibcode files.

    gt_dir = out_dir / "references" / "groundtruth"

    for doc in docs:
        arxiv_id = doc.global_id.replace(".", "_")
        ap = Path(arxiv_id)
        ref_dir = gt_dir / fulltext_prefix / ap.parent
        ref_dir.mkdir(parents=True, exist_ok=True)
        ref_path = ref_dir / (ap.name + ".rs.txt")
        shutil.copy(doc.ext_path(".rs.txt"), ref_path)

        if ".bc.txt" in doc.extensions:
            bc_path = ref_dir / (ap.name + ".bc.txt")
            shutil.copy(doc.ext_path(".bc.txt"), bc_path)

    print(f"Wrote files in `{gt_dir}`")

    # If `--ads-arxiv-fulltext-shadow` is given, treat the argument as a
    # fulltext tree that the ArXiv reference extractor framework might use for
    # its containerized processing, and create symlinks out of that tree to the
    # ADS PDF paths. So, this functionality can only work when running on the
    # ADS system or NFS/sshfs mounts have been set up to emulate it, because
    # otherwise those PDF paths are not useful.

    if settings.ads_arxiv_fulltext_shadow is not None:
        ft_root_dir = Path(settings.ads_arxiv_fulltext_shadow)

        for doc in docs:
            arxiv_id = doc.global_id.replace(".", "_")
            ap = Path(arxiv_id)
            ft_dir = ft_root_dir / fulltext_prefix / ap.parent
            ft_dir.mkdir(parents=True, exist_ok=True)
            shadow_ft_path = ft_dir / (ap.name + ".pdf")

            if doc.ads_pdf_path_symbolic is not None:
                real_pdf_path = doc.ads_pdf_path_symbolic.replace(
                    "$ADS_ARTICLES", str(util.ADS_ARTICLES_PREFIX)
                ).replace("$ADS_ABSTRACTS", str(util.ADS_ABSTRACTS_PREFIX))
            elif doc.pdf_sha256_hex is not None:
                real_pdf_path = util.try_local_data_path(doc.pdf_sha256_hex)
            else:
                real_pdf_path = None

            if real_pdf_path is None:
                util.warn(
                    f"cannot set up fulltext shadow document for doc `{doc.global_id}`"
                )
                continue

            try:
                shadow_ft_path.unlink()
            except FileNotFoundError:
                pass

            shadow_ft_path.symlink_to(real_pdf_path)

        print(f"Created symlinks in `{ft_root_dir}`")


if __name__ == "__main__":
    main()
