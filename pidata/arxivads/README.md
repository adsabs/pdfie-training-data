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
- Loss off accents on characters :-(
- `astrophysics` in text became `astro-physics` in resolved ref file?? (arXiv/2111/000012, Rybicki&Lightman)
