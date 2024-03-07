# Nestor

**Machine-augmented annotation for technical text**

[![Downloads](https://pepy.tech/badge/nist-nestor)](https://pepy.tech/project/nist-nestor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

*You can do it; your machine can help.*

## Purpose

**Nestor** is a toolkit for using Natural Language Processing (NLP) with efficient user-interaction to perform structured data extraction with minimal annotation time-cost.
 
### The Problem
NLP in technical domains requires context sensitivity.
Whether for medical notes, engineering work-orders, or social/behavioral coding, experts often use specialized vocabulary with over-loaded meanings and jargon.
This is incredibly difficult for off-the-shelf NLP systems to parse through. 

The common solution is to contextualize and adapt NLP models to technical text -- Technical Language Processing (TLP)[@brundage2020technical].
For instance, medical research has been greatly advanced with the advent of labeled, bio-specific datasets, which have domain-relevant named-entity tags and vocabulary sets. 
Unfortunately for analysts of these types of data, creating resources like this is incredibly time consuming. 
This is where `nestor` comes in. 

### Why Maintenance and Manufacturing?

A reader may notice a heavy focus on maintenance and manufacturing in the Nestor documentation and design. 
While this is a common problem in technical domains, generally, Nestor got its start in manufacturing data analysis. 
A large amount of maintenance data is *already* available for use in advanced manufacturing systems, but in a currently-unusable form: service tickets and maintenance work orders (MWOs).

For further reading, see [@sexton2017hybrid] [@sharp2017toward] [@brundage2020technical]. 

## Quick Links

- [Get started](getting-started.md)
- [Use a GUI](gui-links.md)
- Go to our [Project Page](https://www.nist.gov/services-resources/software/nestor)

Nestor and all of it's associated gui's/projects are in the public domain (see the [License](LICENSE.md)). For more information and to provide feedback, please open an issue, submit a pull-request, or email us at <nestor@nist.gov>.

## How does it work? 

See the [Getting Started](getting-started.md) page. 

This application was originally designed to help manufacturers "tag" their maintenance work-order data according to the methods being researched by the [Knowledge Extraction and Applications project](https://www.nist.gov/programs-projects/knowledge-extraction-and-application-manufacturing-operations) at NIST.
The goal is to help  build context-rich labels in data sets that previously were too unstructured or filled with jargon to analyze.
The current build is in very early alpha, so please be patient in using this application. If you have any questions, please do not hesitate to contact us (see [Who are we?](#who-are-we). ) 



-   Rank keywords found in your data by importance, saving you time
-   Suggest term unification by similarity (e.g. spelling), for quick review
-   Basic entity relationship builder, to assist assembling problem
    code and taxonomy definitions
-   Strucutred data output as named-entity tags, whether in readable (comma-sep) or
    computation-friendly (sparse-mat) form.

Planned: 

- Customizable entity types and rules,
- Export to NER training formats,
- Command-line app and REST API.


## Who are we?

This toolkit is a part of the [Knowledge Extraction and Application for Smart Manufacturing (KEA)](https://www.nist.gov/programs-projects/knowledge-extraction-and-application-manufacturing-operations) project, within the [Systems Integration Division](https://www.nist.gov/el/systems-integration-division-73400) at NIST. 


### Projects that use Nestor

- Various [Nestor GUIs](gui-links.md): ways to use the full human-centered Nestor workflow in a user-interface. 
- [`nestor-eda`](https://github.com/usnistgov/nestor-eda): (exploratory data analysis): things to do with Nestor-annotated data (dashboard, viz, etc.)


### Points of Contact
- Email the development team at <nestor@nist.gov>
-   [Rachael Sexton](https://www.nist.gov/people/rachael-sexton) [@rtbs-dev](https://github.com/rtbs-dev) Nestor Technical Lead, Associate Project Leader 
-   [Michael Brundage](https://www.nist.gov/people/michael-p-brundage) Project Leader


### Why "KEA"?

The KEA project seeks to better frame data collection and transformation systems within smart manufacturing as *collaborations* between human experts and the machines they partner with, to more efficiently utilize the digital and human resources available to manufacturers.
Kea (*nestor notabilis*) on the other hand, are the world's only alpine parrots, finding their home on the southern Island of NZ.
Known for their intelligence and ability to solve puzzles through the use of tools, they will often work together to reach their goals, which is especially important in their harsh, mountainous habitat. 

## Development/Contribution Guidelines
More to come, but primary requirement is the use of [Poetry](https://python-poetry.org/). 
Plugins are installed as development dependencies through poetry (e.g. `taskipy` and `poetry-dynamic-versioning`), though if not using `conda` environments, `poetry-dynamic-versioning` may require being installed to the global python installation. 

Notebooks should be kept nicely git-friendly with [Jupytext](https://github.com/mwouts/jupytext)

## Other Tools/Resources
Know of other tools? Or want to find similar resources as Nestor? A community driven [TLP Community of Interest (COI)](https://www.nist.gov/el/technical-language-processing-community-interest) has been created to provide publicly available resources to the community. Check out our [awesomelist](https://github.com/TLP-COI/awesome-tlp).

\bibliography
