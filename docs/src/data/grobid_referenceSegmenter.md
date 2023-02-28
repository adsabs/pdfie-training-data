# GROBID Reference Segmenter Training Data

Files with extensions `grobid_referenceSegmenter.raw` and
`.grobid_referenceSegmenter.tei.xml` file contain training data that can be used
to train [GROBID]'s classifier that segments streams of reference text into
individual references: the “reference segmenter”.

[GROBID]: https://grobid.readthedocs.io/

This information has been created for a few files in this framework and used for
pilot tests, but **it has not yet been wired into a functioning pipeline**.

The initial 8 files for which the training *has* been created were selected
because GROBID seemed to be handling them very poorly. Retraining the reference
segmenter with the new data led to measurably improved results.


## Format

The "raw" data are generated by GROBID from the PDF. See information below about
how to obtain them.

The XML data should be in a specialized subset of GROBID’s TEI XML format. See
[GROBID's annotation guidelines for bibliographical references][1] and the
examples already in this repo.

[1]: https://grobid.readthedocs.io/en/latest/training/Bibliographical-references/


## Fine-tuning GROBID's training

This is the bit that should be automated a bit more. If you want to fine-tune
the training, you need to add new files to the directories
`grobid-trainer/resources/dataset/reference-segmenter/corpus/raw/` and
`grobid-trainer/resources/dataset/reference-segmenter/corpus/tei/` in the GROBID
source tree. Retraining the segmenter is then a simple as:

```
$ ./gradlew train_reference_segmentation
```

On Peter's laptop, it takes about an hour to run. Once this is done your GROBID
instance should start using the new settings, I think? There may be some steps
needed to update the running service to use the new training outputs, though —
consult the GROBID docs.

For reference, GROBID's stock `referenceSegmenter` corpus contains 73 "raw"
files, 83 TEI XML files. There's 1 raw file without corresponding TEI, 11 TEI
without corresponding raw. (No idea why.)


## Creating New Training Data

Here are some sketchy notes about how to generate new training data for the
Grobid reference segmenter.

Start by creating a directory containing some number of PDFs that you want to
create training data for. Below this is called `$MY_PDF_INPUT_DIRECTORY`.

Next run GROBID's `createTraining` command, which seems to only be available
through the command line ("batch mode") and not the web service. Need to run
`./gradlew install` to create the `onejar` JAR file to run.

```
$ java -Xmx4G \
  -jar grobid-core/build/libs/grobid-core-0.7.0-onejar.jar
  -gH grobid-home
  -dIn $MY_PDF_INPUT_DIRECTORY
  -dOut $MY_XML_OUTPUT_DIRECTORY
  -exe createTraining
```

This should create outputs including ones with names like
`*.training.references.referenceSegmenter.tei.xml`. If these are ones where
GROBID is performing really badly on the input PDFs, you may well be able to see
that that the segmenter has failed badly here. The no-extension file
`*.training.references.referenceSegmenter` corresponds to the "raw" input used
in the training.

Once you have the XMLs, it's pretty straightforward to edit them to correct the
segmentation. To save the new training data in this repo, copy the files into
appropriate `pidata/` locations, renaming as appropriate.