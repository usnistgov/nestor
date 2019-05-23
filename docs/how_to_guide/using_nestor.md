# Using the Nestor GUI

## Settings
This window helps to set various parameters that control how Nestor behaves during the process of tagging. It can be accessed at any time during the tagging process by going to **Python** -> **Preferences** on a Mac. Similar settings can be found for Windows and Linux machines too.
(If you are a first time user, or do not really want to change the default settings, it is perfectly fine to leave these settings as they are).

### Special Replace


### Number of words listed
This setting controls the number of word tokens from your data, that are displayed for tagging. For example, you might be interested in tagging only the top 1000 words from your data. The ordering is decided based on a measure of importance called the [_tf-idf_ score](https://en.wikipedia.org/wiki/Tf%E2%80%93idf).

### Similarity for ticked words
Recall that Nestor shows you a list of similar words (and check boxes) for each word that you are tagging. You can control which words you want to be ticked by default, when you are tagging. This is done by changing the setting for how similar are the tagged word and the word in the list, for the similar word to be ticked by default.

###Threshold for List of Similar Words

##Single Word Tagging

The `Single word analysis` tab of Nestor allows the user to classify and tag individual words. Likewise, the `Multi word analysis` tab will allow classification and tagging of two word phrases.
 
 ### Word annotation Overview
Present on these tabs are several boxes, which let you interface with concepts found in your data, and assist you in annotating them First is the Word annotation" box, which has four columns: 
- `words`: Also called "tokens". Single words are presented in order of importance with respect to the user-loaded data. 
- `classification`: The user’s classification, or "tag-type", are stored here 
- `tag`: This column will display the given "alias" (cannonical representation) defined for the given word/token
- `note`: This column stores any relevant notes from picking a given alias or classification. 
 
### Similar Words
The “Similar words from csv” box will present similar words to the highlighted selection in the “Words” column. These suggestions are taken directly from the user-loaded data. The slider on the bottom of this box can be adjusted to view more or less words, with decreasing similarity score further down the list. The user can select the words that should share a cannonical representation (alias) checking the checkbox. 
> For example, the user might highlight "replace" and decide that the “repalce” suggestion should refer to the same tag, by checking the box.
> Note - all selected words will receive the same alias, classification, and notes. 

If the user hovers over the word in this column, a box will appear and display examples that contain the word from the loaded data 

### User-Input
The “Tag current word” box contains three different fields:
- `Preferred Alias`: The user can input a preferred alias for the selected word any checked similar words. 
- `Classification`: The user can select the classification for the selected word and checked similar words. The user has five options for classifications in v0.3 
    - Item
    - Problem
    - Solution
    - Ambiguous (Unknown) 
    - Irrelevant (Stop-Word) 

> Ambiguous words will commonly arise in cases where *surrounding* words are needed to know the "right" classification. These can then be classified in the Multi word analysis tab.

- `Notes` (if necessary): The user can type notes for a specific word and checked similar words here.
The “Overall Progress” at the bottom of the app will track how much progress is completed while the user has annotated words in the single word analysis tab. 
The next word button allows the user to navigate between different words when annotated. 


##Multi Word Tagging

The Multi word analysis tab allows the user to classify two word phrases. 
There are the same four boxes in the Word Annotation window of nestor as the Single word analysis tab, with a few changes. 

### Special options
The “Word Composition” box (replaces "Similar words") provides the user with the information on each constituent token comprising the two word phrase. 
> For example “Replace Hydraulic” will give the user all of the previously stored information for both “Replace” and “Hydraulic” tokens.

The “Tag current words” tab has added/changed the following options from before, as well, to capture meanings for the bi-gram *as a whole*:

- `Classification`: There are two new options to account for:
    - Problem Item
    - Solution Item
    
The “Overall Progress” at the bottom of the this tab will track how much progresshas been made *specifically* on annotated words in the Multi word analysis tab. 

### Auto-classification
The user can choose auto-populate the `classification` column on the multi-word tab using the “Auto-populate>Multi word from Single word vocabulary” toolbar drop down menu. This applies a set of logic rules to guess what classification a particular multi-word should receive, based on its constituents.
> Note: auto-populated classifications must still be verified by the user. This is done upon entering/keeping the `alias` annotation. Only then will it be counted as "complete"

Nestor v0.3 provides the user with predefined rules based on auto population.
- `Problem` + `Item` = `Problem Item` 
- `Solution` + `Item` = `Solution Item` 
- `Item` + `Item` = `Item` 
- `Problem` + `Solution` = `Irrelevant` 

Additionally, Nestor will suggest a default alias for `word1`+`word2`, namely, `word1_word2`.


## Reporting and Data Transfer
After a sufficient time spent annotating concepts from your corpus, you might like to know what coverage your annotation has on the detected information within. Nestor provides some metrics and functions on the `Report` tab, both for exporting your hard work and giving you visual feedback on just how far you've come. 

First, you will need to process the data using your annotations! 
> Always start by pressing the `UPDATE TAG EXTRACTION` button. 

### Exporting 
Nestor parses through the original text and unifies detected words into the tags you have now created. This is done in two ways: human-readable (CSV) and binary file store (HDFS)

- `create new CSV`: a new csv, containing your *mapped* column headers and new headers for each type of tag, will be exported. Each work-order will now have a list of tags of each type in its corresponding cell. Tags not annotated explicitly will be ommitted.

- `create a HDFS (binary)`: This is a rapid-access filestore (`*.h5`), excellent for powering visualizations or analysis in other toolkits. Three keys represent three automatically created tables containing your annotated data: 
 - `df`: columns from original dataset whose csv headers have been mapped
 - `tags`: binary tag-occurrence matrix for each tag-document pair
 - `rels` PI/SI-document pair occurrence matrix. 
 
The binary file is a requirement to utilize the (beta) `nestor-dash` functionality. You can use the dashboard by uploading your `.h5` file to the dashboard, provided you have marked at least one column as being a `.name` type (e.g. machine.name is "Asset ID", technician.name is Technician, etc.)

### Progress Report
The bottom half of this window contains various metrics for annotation rates in a table, along with a histogram that shows a distribution of "completion" over all entries in your corpus. This is the completion-fraction distribution, where "1.0" means *all* extracted tokens in a work-order have a valid user-given tag and classification, while "0.0" means that none of them are annotated. 