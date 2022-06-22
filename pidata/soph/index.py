#! /usr/bin/env python3
# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Generate TOML and refstring files for SoPh.

There are more files with reference data than there are fulltext PDFs. The XML
data are (sometimes) only identified by bibcode, so we need to associate
fulltext files with bibcodes, which we can do through the file
`/proj/ads/abstracts/config/links/fulltext/all.links`. Many of the PDFs listed
there, though, are from ArXiv, not official publisher data.

In some cases the XML reference files are on a per-article basis, e.g.:
`$ADS_REFERENCES/sources/SoPh/0080/10.1007_BF00147969.xref.xml`, with
structure::

    <ADSBIBCODE>$bibcode</ADSBIBCODE>
    <citation_list>
        <citation>
            <unstructured_citation>text...</>
        </>
        <citation>
        ...
    </citation_list>

In other cases, data for several articles are in one file, e.g.:
`$ADS_REFERENCES/sources/SoPh/0209/iss1.springer.xml`::

    <ADSBIBCODE>$bibcode1</ADSBIBCODE>
    <Citation>
        {structured data}
        <BibUnstructured>text...</BibUnstructured>
    </Citation>
    <Citation>
    ...
    </Citation>
    <ADSBIBCODE>$bibcode2</ADSBIBCODE>
    <Citation>
    ...

There are also JATS files with no "unstructured" version of the reference, e.g.
`$ADS_REFERENCES/sources/SoPh/0297/iss.jats.xml`.

"""

from dataclasses import dataclass
import html.entities
import os.path
from pathlib import Path
import toml
from typing import Dict, TextIO

from .. import util


COLL_PREFIX = Path(os.path.dirname(__file__))
REFERENCES_SUBDIR = "sources/SoPh/"
FULLTEXT_SUBDIR = "sources/SoPh/"
PDFS_ARE_RASTER = False


@dataclass
class Doc:
    bibcode: str = None
    pdf_path: str = None

    def create_toml_metadata(self):
        # Rewrite the PDF path to use $ADS_ARTICLES as the prefix instead of
        # $ADS_FULLTEXT so that I can get away with setting up fewer mounts when
        # doing Docker or sshfs-based processing.

        ads_pdf_path = self.pdf_path.replace(
            str(util.ADS_FULLTEXT_PREFIX), "$ADS_ARTICLES/fulltext"
        )

        n_bytes, sha256 = util.nbytes_and_sha256_of_path(self.pdf_path)

        return {
            "bibcode": self.bibcode,
            "pdf_sha256": sha256,
            "pdf_n_bytes": n_bytes,
            "ads_pdf_path": ads_pdf_path,
            "random_index": util.make_random_index(),
            "pdf_is_raster": PDFS_ARE_RASTER,
        }


def scan_candidates() -> Dict[str, Dict[str, Doc]]:
    # Scan the "links" file for bibcodes and PDF paths. Filter by fulltext path
    # to identify the publisher PDFs. NB: `/proj/ads/fulltext` is just a symlink
    # to `/proj/ads/articles/fulltext`, but the former is the prefix used in
    # this file. Group by volume to narrow down the XML loading task.

    by_vol = {}
    n = 0
    prefix = str(util.ADS_FULLTEXT_PREFIX / FULLTEXT_SUBDIR) + os.path.sep

    with util.ADS_FULLTEXT_LINKS_PATH.open("rt") as f:
        for line in f:
            pieces = line.split()
            if len(pieces) > 1 and pieces[1].startswith(prefix):
                bibcode = pieces[0]
                pdf_path = pieces[1]
                doc = Doc(bibcode=bibcode, pdf_path=pdf_path)

                volume = pdf_path[len(prefix) :].split("/", 1)[0]
                by_vol.setdefault(volume, {})[bibcode] = doc
                n += 1

    print(f"Found {n} bibcode/publisher-PDF links in {len(by_vol)} volumes")
    return by_vol


def process_volume(vol: str, docs: Dict[str, Doc]):
    # Currently we only have publisher PDF linkage data for volumes where there
    # are `.springer.xml` and `.jats.xml` files, and we can only obtain the
    # unstructured citation from `.springer.xml`.

    vol_dir = util.ADS_REFERENCES_PREFIX / REFERENCES_SUBDIR / vol
    print(f"Volume {vol}:")

    for fn in vol_dir.iterdir():
        if fn.name.endswith(".springer.xml"):
            print(f"  XML {fn}:")
            process_springer_xml(vol, docs, fn)


class SpringerProcessor:
    """
    These files are called XML but can't be processed with an actual XML
    handler, because there are things like unescaped ">" characters in DOIs, no
    single toplevel element, etc. Fortunately the format is fairly easy to
    process manually. (It would sure be nice if people actually applied escaping
    when generating "XML" from text.)
    """

    vol_dir: Path = None
    docs: Dict[str, Doc] = None
    cur_output: TextIO = None
    n_skipped_no_pdf: int = 0
    n_skipped_preexist: int = 0
    n_created: int = 0

    def __init__(self, volume: str, docs: Dict[str, Doc]):
        self.docs = docs
        self.vol_dir = COLL_PREFIX / volume
        self.vol_dir.mkdir(parents=True, exist_ok=True)

    def cur_done(self):
        if self.cur_output is not None:
            self.cur_output.close()
            self.cur_output = None

    def maybe_start_new(self, bibcode: str):
        self.cur_done()

        doc = self.docs.get(bibcode)
        if doc is None:
            self.n_skipped_no_pdf += 1
            return

        toml_path = self.vol_dir / (bibcode + ".doc.toml")
        if toml_path.exists():
            self.n_skipped_preexist += 1
            return

        with open(toml_path, "wt") as f:
            self.n_created += 1
            toml.dump(doc.create_toml_metadata(), f)

        rs_path = self.vol_dir / (bibcode + ".rs.txt")
        self.cur_output = rs_path.open("wt")

    def handle_line(self, line):
        line = line.strip()
        if not line:
            return

        if line.startswith("<ADSBIBCODE>"):
            bibcode = line[12:]
            bibcode = bibcode[: bibcode.index("<")]
            self.maybe_start_new(bibcode)
        elif self.cur_output is not None:
            try:
                i = line.index("<BibUnstructured>")
            except ValueError:
                pass
            else:
                text = line[i + 17 :]
                # There are cases with additional "XML" content in tags within
                # the `<BibUnstructured>` (e.g. `<ExternalRef>`). Hopefully the
                # XML is un-busted enough that any less-thans in the
                # unstructured references are properly escaped.
                text = text[: text.index("<")]
                text = handle_entities(text)
                print(text.strip(), file=self.cur_output)

    def all_done(self):
        self.cur_done()
        print(f"    Emitted data for {self.n_created} docs")
        print(f"    Skipped {self.n_skipped_no_pdf} docs with no publisher PDF")
        print(f"    Skipped {self.n_skipped_preexist} preexisting docs")


def process_springer_xml(volume: str, docs: Dict[str, Doc], xml_path: Path):
    proc = SpringerProcessor(volume, docs)

    with xml_path.open("rt") as f:
        for line in f:
            proc.handle_line(line)

    proc.all_done()


_MORE_ENTITIES = [
    ("&ecedil;", "ę"),
    ("&gcaron;", "ǧ"),
]


def handle_entities(text: str) -> str:
    text = html.unescape(text)

    for ent, repl in _MORE_ENTITIES:
        text = text.replace(ent, repl)

    return text


def main():
    by_vol = scan_candidates()

    for vol, docs in by_vol.items():
        process_volume(vol, docs)


if __name__ == "__main__":
    main()
