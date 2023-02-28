# Reference Strings (`.rs.txt`)

The `.rs.txt` file contains the list of ground-truth reference strings for a
document. It is a line-oriented text file.


## Format

- Reference strings are folded to one per line.
- They should use Unicode to match typography as precisely as possible
- They should *not* use HTML or other markup.
- Numbering typography such as leading `[3]` should not be included.
- Hyphens introduced for linebreaks should be removed.


## Known Issues / Corner Cases

Some PDF refstrings include important markup. For instance, a PDF refstring
might have the text “DOI” with a hyperlink to the DOI for an article. A
reference extractor that understands this should be able to pull out the DOI
from the link, thereby getting an ultra-reliable resolution of the reference.
However, we have no way to express this kind of ground-truth right now. We
are not aware of any reference extractors that are aware of hyperlinks or
other kinds of markup.

The Unicode that we use to capture typography does not always match the Unicode
that is actually contained in a PDF. Sometimes, a proper Unicodification of the
reference string does not exist, or is at least highly debatable: some reference
sections include the titles of papers in their refstrings, and if those papers
are physics papers, they may contain fairly complicated mathematical expressions
(“Cross section of the α² → μμ¯ reaction ...”).

I have lost track of my example, but in at least some cases, a single reference
entry in an article's bibliography may contain multiple references. I forget how
I handled this.