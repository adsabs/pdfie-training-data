# The `misc` Collection

This collection is for miscellaneous documents whose PDFs aren't, and shouldn't
be, part of ADS' holdings.

As always, see also the file `pidata/misc/README.md`.


## Identification

Items within this collection are given one-off, manually-assigned IDs.


## Ingestion

To ingest a new PDF, run:

```
$ python -m pidata.misc.ingest $NAME $PDF_PATH
```

You should then manually edit the generated TOML and add whatever other metadata
files are appropriate. This operation requires the environment variable
`$PDFIE_LOCAL_DATA` to be set. More or less by definition, this operation can't
do anything else helpful for you since “misc” documents should all be *sui
generis*.
