
## Purpose

This application was designed to help manufacturers "tag" their
maintenance work-order data according to [the methods being researched](https://www.researchgate.net/project/Knowledge-Extraction-and-Application-for-Smart-Manufacturing) by the Knowledge Extraction and Applications project at the NIST Engineering Laboratory. The goal of this
application is to give understanding to data sets that previously were
too unstructured or filled with jargon to analyze. The current build is
in very early alpha, so please be patient in using this application. If
you have any questions, please do not hesitate to contact us (see [Who
are we?](#who-are-we). )

### Why?

There is often a large amount of maintenance data *already* available
for use in Smart Manufacturing systems, but in a currently-unusable
form: service tickets and maintenance work orders (MWOs). **Nestor** is
a toolkit for using Natural Language Processing (NLP) with efficient
user-interaction to perform structured data extraction with minimal
annotation time-cost.

### Features


-   Ranks concepts to be annotated by importance, to save you time
-   Suggests term unification by similarity, for you to quickly review
-   Basic concept relationships builder, to assist assembling problem
    code and taxonomy definitions
-   Strucutred data output as tags, whether in readable (comma-sep) or
    computation-friendly (sparse-mat) form.

### What's Inside?

Documentation is contained in the /docs subdirectory, and are hosted as
webpages and
[PDF](https://media.readthedocs.org/pdf/nestor/latest/nestor.pdf)
available at [readthedocs.io](https://nestor.readthedocs.io/en/latest/)
.

Current:

-   Tagging Tool: Human-in-the-loop Annotation Interface (pyqt)
-   Unstructured data processing toolkit (sklearn-style)
-   Vizualization tools for tagged MWOs-style data (under development)

Planned/underway:

-   KPI creation and visualization suite
-   Machine-assisted functional taxonomy generation
-   Quantitative skill assement and training suggestion engine
-   Graph Database creation assistance and query tool

### Pre-requisites

This package was built as compatible with Anaconda python distribution.
See our [default requirements file](https://github.com/usnistgov/nestor/blob/master/requirements/defaults.txt) for a complete list of major dependencies, along with the requirements to run our [experimental dashboard](https://github.com/usnistgov/nestor/blob/master/requirements/dash.txt) or to [compile our documentation locally](https://github.com/usnistgov/nestor/blob/master/requirements/docs.txt)


## Who are we?


This toolkit is a part of the Knowledge Extraction and Application for
Smart Manufacturing (KEA) project, within the Systems Integration
Division at NIST.

### Points of Contact

-   [Michael Brundage](https://www.nist.gov/people/michael-p-brundage)
    Principal Investigator
-   [Thurston Sexton](https://www.nist.gov/people/thurston-sexton) Nestor Technical Lead

### Contributors:
Name             |   GitHub Handle
---              |   ---
Thurston Sexton  |   [@tbsexton](https://github.com/tbsexton)
Sascha Moccozet  |   [@saschaMoccozet](https://github.com/saschaMoccozet)
Michael Brundage |   [@MichaelPBrundage](https://github.com/MichaelPBrundage)
Madhusudanan N.  |   [@msngit](https://github.com/msngit)
Emily Hastings   |   [@emhastings](https://github.com/emhastings)
Lela Bones       |   [@lelatbones](https://github.com/lelatbones)

### Why KEA?

The KEA project seeks to better frame data collection and transformation
systems within smart manufacturing as *collaborations* between human
experts and the machines they partner with, to more efficiently utilize
the digital and human resources available to manufacturers. Kea (*nestor
notabilis*) on the other hand, are the world's only alpine parrots,
finding their home on the southern Island of NZ. Known for their
intelligence and ability to solve puzzles through the use of tools, they
will often work together to reach their goals, which is especially
important in their harsh, mountainous habitat.
