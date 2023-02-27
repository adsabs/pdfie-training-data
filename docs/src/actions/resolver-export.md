# Export for testing the reference resolver microservice

To export this corpus into a file that can be used to test the ADS [reference
resolver service][refsvc], use:

[refsvc]: https://github.com/adsabs/reference_service

```
$ python -m pidata.export_resolver_test
  [--normalize]
  [--ascii]
  outfile.txt
```

This will create a file `outfile.txt` containing ground-truth refstrings and the
bibcodes that they *should* resolve to. The `--normalize` option will normalize
Unicode punctuation in the output refstrings; for instance, the curly double
quote `“` will be changed into the straight double quote `"`. The `--ascii`
option will further drop the output down into plain ASCII; for instance, `é`
will become `e`, and Unicode codepoints with no corresponding ASCII values will
be dropped.

This is a pretty simple operation that basically just flattens down the database
into the specific inputs and outputs that are the responsibility of the
microservice.
