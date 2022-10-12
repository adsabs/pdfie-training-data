# `arxivads`: ArXiv as processed by ADS

- References (text): `/proj/ads/references/resolved/${ARXIV/ID}.raw`
- PDFs: `/proj/ads/abstracts/sources/ArXiv/fulltext/${ARXIV/ID}`
- Where `${ARXIV/ID}` might be something like `arXiv/2111/03644` for a newer
  item, or `astro-ph/1998/9804042` for an older one.
- But we also have TeX source! Which we can use to extract refstrings in an
  automatic-but-not-circular way.

I see some artifacts in the refstrings that ADS has extracted:

- Sometimes doubled DOI
- Sometimes doubled commas
- Em-dashes expressed as `--` ligatures.
- Loss of accents on characters :-(
- `astrophysics` in text became `astro-physics` in resolved ref file?? (arXiv/2111/00012, Rybicki&Lightman)
- Duplications of references containing `[]` characters (arXiv/2111/00665)

## Known issues

The ADS PDFs change over time! Because Arxiv papers get updated and ADS updates
PDFs when that happens — it has no sense of Arxiv revisions. Some of our PDF
metadata are now out of data, as are our refstrings and other derived products.
Gross.

The `check.py` script in this directory will scan an Arxiv-month, look for
updated PDFs, and rewrite the data for anything that's changed. Since this goes
back to the original ADS data, which have various problems, one should then
manually review the diffs in Git to make sure that corrections are not lost.
