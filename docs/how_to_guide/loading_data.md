# Loading/Saving Data

Nestor comes with multiple options for loading your data, depending on if this is the first time you are tagging a dataset or you are returning for a follow up session. 

*New in v0.3*: you are now able to create projects, which persist and can be exported/imported/shared. You will find all projects inside your home folder, in `~/.nestor-tmp` (`/home/<username>` on unix-based sytems, `<root>/Users/<username>` for Windows)

## New Project
If this is the first time tagging a specific file (new project): 
1. You can create a new project under “File” -> “New Project” 
    - Here, Nestor requires a “Project Name” and to load the .csv of the file you want to tag. 
    - Optional entries include a description of the project, the author of the tagging, and naming both the 1-gram and N-gram filenames. 
2. Select the (presumably natural-laguage) columns you want to tag using Nestor. 
3. (Optional) Map columns from the csv to a database schema as defined in [this paper](https://www.nist.gov/publications/developing-maintenance-key-performance-indicators-maintenance-work-order-data). This is detailed more in [SECTION?](blah)
    - Please note, you may map columns from your csv to this schema, which allows other plotting/analysis tools to access them (e.g. `nestor-dash`) while *not* selecting them to be tagged (they remain unchecked).


## Persistence
Nestor has a number of ways to persist your work and make it portable: 

### Disk Location
Nestor version 0.3 allows you to create projects. You will find all projects inside `.nestor-tmp`, found under a folder named after the chosen project name given at creation. 
    Inside each folder, you will find:

- The application configuration file, config.yaml. This file contains information used by the application during the tagging process.
- The csv file you chose to tag.
- The single token vocabulary file
- The multiple token vocabulary file

> By default (if not changed at the time of project creation) the filenames for the vocab files are respectively vocab1g.csv and vocabNg.csv. 


### Import/Export
Nestor allows a user to export an entire project, located under “File” -> “Export Project”, saving it as a portable .zip or .tar file, which can be easily shared among different users of Nestor.


If you are returning to tag a previously tagged dataset, you can either “Open Project,” found in `.nestor-tmp`, or “Import Project” from a .zip or .tar archive in another location.  


You can additionally make use of previous work, such as other projects, by importing from vocabulary sheets that were saved from previous tagging sessions. This option is available under the "Auto-populate>From CSV" toolbar drop down menu. The user can select either single word or Multi-Word vocabulary, and select a compatible csv vocabulary, accordingly. Un-annotated words in the current project that are defined in the selected CSV will be updated with the annotations within.


### Research mode
If you decide to use the research mode, a new project folder will be added to `.nestor-tmp`. In this case, additional folders will be added inside the project folder. These folders will be named after your chosen criteria.
For example, if you choose inside the research mode to save your project according to percentage of tokens tagged, then a new folder named percentage will appear in your project folder. This percentage folder will contain a version of your vocab files at a certain percentage.
