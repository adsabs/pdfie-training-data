# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Export the database into a format suitable for use with the
arxiv-reference-extractor pipeline.
"""

import argparse
import os
from pathlib import Path
import shutil

from . import scan, util


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

    # Possible elaboration: group everything into different sessions in
    # different ways? One obvious way to do that would be by collection, but
    # it's not obvious to me that that's actually useful.
    session_id = "all"

    fulltext_prefix = "pdfietd"

    docs = list(scan(rs=True, no_raster=True))
    print(f"Scan yielded {len(docs)} documents.")

    # Do the log files

    logs_dir = out_dir / "logs" / session_id
    logs_dir.mkdir(parents=True, exist_ok=True)

    with (logs_dir / "extractrefs.out").open("wt") as f:
        for doc in docs:
            arxiv_id = doc.global_id.replace(".", "_")
            fake_pdf_path = f"{fulltext_prefix}/{arxiv_id}.pdf"
            refs_path = os.path.join(
                util.ADS_REFERENCES_PREFIX,
                "sources",
                fulltext_prefix,
                arxiv_id + ".raw",
            )
            print(fake_pdf_path, refs_path, file=f)

    print(f"Wrote `{logs_dir / 'extractrefs.out'}`")
    fake_bibcode_serial = 0

    with (logs_dir / "fulltextharvest.out").open("wt") as f:
        for doc in docs:
            arxiv_id = doc.global_id.replace(".", "_")
            fake_pdf_path = f"{fulltext_prefix}/{arxiv_id}.pdf"

            if doc.bibcode:
                bibcode = doc.bibcode
            else:
                bibcode = "9999" + str(fake_bibcode_serial).rjust(14, ".") + "."
                fake_bibcode_serial += 1

            print(fake_pdf_path, bibcode, "fakeaccno", "fakesubdate", file=f)

    print(f"Wrote `{logs_dir / 'fulltextharvest.out'}`")

    # Copy out the ground-truth refstring files.

    gt_dir = out_dir / "references" / "groundtruth"

    for doc in docs:
        arxiv_id = doc.global_id.replace(".", "_")
        ap = Path(arxiv_id)
        ref_dir = gt_dir / fulltext_prefix / ap.parent
        ref_dir.mkdir(parents=True, exist_ok=True)
        ref_path = ref_dir / (ap.name + ".rs.txt")
        shutil.copy(doc.ext_path(".rs.txt"), ref_path)

    print(f"Wrote files in `{gt_dir}`")

    # If `--ads-arxiv-fulltext-shadow` is given, treat the argument as a
    # fulltext tree that the ArXiv reference extractor framework might use for
    # its containerized processing, and create symlinks out of that tree to the
    # ADS PDF paths. So, this functionality can only work when running on the
    # ADS system, since otherwise those PDF paths are not useful.

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
                )
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
