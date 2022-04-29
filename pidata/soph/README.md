# `soph`: Solar Physics

- References (XML): `/proj/ads/references/sources/SoPh`
- PDFs: `/proj/ads/articles/fulltext/sources/SoPh`

The structured reference data is called "XML" but it's not valid for a variety
of reasons. See `index.py` for some of the details.

The "unstructured" reference data are largely very good but there are some lingering
TeX-isms in the data. Try:

```
grep -E '\\|{|}|~|\$|\^|_' *.rs.txt
```
