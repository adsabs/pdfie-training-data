# Bibcodes (`.bc.txt`)

The `.bc.txt` file gives the ground-truth bibcodes for a document. It is a
line-oriented text file.


## Format

- One bibcode per line, followed by a date of the form `YYYY-MM-DD` indicating
  when the bibcode was last validated or updated, then optionally freeform
  commentary text. This text might be used to explain an issue in the associated
  refstring that makes the bibcode resolution surprising or impossible.
- The number of lines in the file should match exactly the number of lines in
  the `.rs.txt` file. Every document with a `.bc.txt` file should have a
  `.rs.txt` file.
- A sequence of 19 periods should be used for refstrings that do not resolve to
  ADS bibcodes.


## Corner Cases

The files are a bit inconsistent as to how thorough they are about specifying
bibcodes in corner cases.

For instance, some reference strings contain different pieces of information
that simply aren't internally consistent; i.e, the page number is just wrong.
These have generally been expressed as “unresolvable”, i.e. 19 periods, even
though an engaged reader can usually figure out which reference was intended.

Other refstrings are internally consistent but need an intelligent reader to
parse; for instance, "Jones et al., in these proceedings". These have generally
been rendered with the intended bibcode.

I forget what I did, if anything, for cases where one bibliography entry
contains multiple references in the source document.


## Notes

The contents of this file may evolve while refstrings stay fixed, because new
records are added to ADS and existing records may be reidentified. (E.g., if the
first author of an entry was wrong, the last character will change when the
mistake is corrected; or a temporary Arxiv bibcode may be updated to the bibcode
for a final published paper.)

The date associated with each bibcode is meant to help deal with such evolution,
although the information is not used by any of the tooling right now. The idea
is that a tool could be written to look for bibcodes with old dates, try to
resolve them, and update the the ones that now resolve. (If the bibcode still
doesn't resolve, its associated date should still be updated so that we know not
to recheck it for a little while.)
