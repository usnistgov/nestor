




Using the Tagging Tool
======================

This section will walk through the steps for using the tagging tool
application.

Start the Application
---------------------

#. Click on the nist-tagging-tool environment button |image|

#. Click on the "run" button |image|

#. Select "Open Terminal" |image|

#. A new terminal will open that will look like the below: |image|

#. Within the terminal, navigate to the top level folder of the
   application. Here, the folder is located at

#. Type the command \|python -m app.taggingUI.main\| |image|

#. The application should open as seen below: |image|

#. Open your .csv file with your MWOs. Included in the application, is a
   publicly available dataset. We will use this file (mine_raw.csv) as
   the example. |image| |image|

#. If you are using the application for the first time, hit “Next”
   |image|

#. Select the column(s) that you would like to “tag.” In this example,
   the column is “OriginalShorttext.” Hit “Next”. |image|

#. The application window will open as seen below: |image|

1 Gram Token tab
----------------

This subsection will describe the features of the application and goes
into detail on the “1 Gram Token” tab.

-  This window contains the following information: |image|

   -  “tokens”: The token as seen in the corpus and ranked by TF-IDF
      weighting.

   -  “NE”: This is a “Named Entity.” This column will track the
      classifications of the tokens, which will be explained in more
      detail later.

   -  “alias”: This column tracks any aliases for tokens as made by the
      tool. These represent your new “tags."

   -  “notes”: This column tracks your notes for any tokens you have
      mapped to an alias.

-  Next, select a token to “tag.” In this example, we use “replace.”
   |image|

-  The “similar pattern” field will display words similar to the token
   using an “edit-distance"-based metric, via
   *`fuzzywuzzy <https://github.com/seatgeek/fuzzywuzzy>`__*. Any term
   that is selected here will be given the same alias and classification
   as the original token. So in this example, if “replaced” is selected,
   it will be given the same alias, notes, and classification as
   “replace” |image|

-  The “alias” field will allow a user to enter any alias they would
   like for a token. The field will auto suggest the “token” as-is as
   the initial alias, but the user has the ability to change it to any
   alias they desire. |image|

-  This field is where the user can classify the “token.” The
   classifications provided are:

   -  “Item”: The objects directly relevant to the issue such as
      machine, resources, parts, etc. An example is a “pump” is always
      an item, however, “pumping” would not be an item.

   -  “Problem”: The problem that is occurring at an item. An example is
      “leak” is always a problem.

   -  “Solution”: The solution action taken on an item. An example is
      “replace” is always a solution.

   -  “Ambiguous (Unknown)”: Words that are unknown without more
      context. An example is “oil” as this can be an item or a solution.
      This is further described in the N Gram Token tab section
      `4.3 <#sec:Ngram>`__

   -  “Stop-word”: A word that does not matter for analysis. For
      example, “see” or “according” are stop-words.

   |image|

-  The “Notes” field allows users to enter notes about the
   token/classifications. |image|

.. _sec:Ngram:

N Gram Token tab
----------------

This subsection will describe the features of the application and goes
into detail on the “N Gram Token” tab.

-  The N Gram token tab will provide detail on common 2 grams tokens,
   ordered in TF-IDF ranking, for the corpus (e.g., “hydraulic leak” is
   a common 2 gram in some data sets). The 2 grams can also provide more
   context for the “Uknown” classifications from the above section. For
   example, “oil” is unknown until the user is provided more context.
   |image|

-  When a user selects the N Gram Token tab, the window below is
   presented: |image|

-  The user is presented with the Composition of the 2 gram, which are
   composed of two 1 gram tokens. Each 1 gram is presented, with the
   classification (“type”) and the synonyms (the other words that were
   linked with the Similar Pattern subwindow in the above section). In
   this example, “oil” is an “unknown (U)” classification and has no
   other synonyms at this point; “leak” is a “problem (P)” and has no
   other synonyms at this point. |image|

-  There are a number of classifications that a user can select for a 2
   grams. The user will have to classify any 2 grams that contain an “U”
   classification. Please note that some 2 grams will be pre-classified
   based on a ruleset as seen below: |image|

   -  Problem Item: This is a problem-item (or item-problem) pair. For
      example, “hydraulic” is an item and “leak” is a problem so
      “hydraulic leak” is a problem-item pair. The tool will
      pre-populate some problem-item pairs using the 1 grams that are
      classified as problems and items.

   -  Solution Item: This is a solution-item (or item-solution) pair.
      For example, “hydraulic” is an item and “replace” is a solution so
      “replace hydraulic” is a solution-item pair. The tool will
      pre-populate some solution-item pairs using the 1 grams that are
      classified as solutions and items.

   -  Item: This is for pairs of items that are de facto 1-grams. For
      example “grease” is an item, line is an “item”, but a
      “grease_line” is most likely its own “item". The tool will
      pre-populate some items based on 1 grams that are both items.
      Please note that 2 gram items, since they are really being treated
      as 1-grams, must have an underscore (_) in their alias, between
      the 2 individual items as seen below: |image|

   -  Problem: This is a problem that is a 2 gram. This will be left up
      to the user to classify as these will not be pre-populated using 1
      gram classifications. Please note that 2 gram problems, since they
      are really being treated as 1-grams, must have an underscore (_)
      in their alias, between the 2 individual problems.

   -  Solution: This is a solution that is a 2 gram. This will be left
      up to the user to classify as these will not be pre-populated
      using 1 gram classifications. Please note that 2 gram solutions,
      since they are really being treated as 1-grams, must have an
      underscore (_) in their alias, between the 2 individual solutions.

   -  Ambigious (Unknown): This is an unknown 2 gram that needs more
      context. This will be left up to the user to classify as these
      will not be pre-populated using 1 gram classifications.

   -  Stop-word: This is 2 gram stop-word. This will be pre-populated
      when a “solution” 1 gram is paired with a “problem” ‘ gram. The
      user can decide if any other 2 grams are not useful.

Report tab
----------------------------------

Once the user is done tagging their desired amount of tokens, they can
begin using the report tab.

-  Please make sure to hit the “update tag extraction” button before
   proceeding. This may take some time to compute. |image|

-  The bottom graph will update. It explains the amount of tagging that
   has been completed. The distribution of documents (shown as a
   histogram) is calculated over the precision for each document (i.e.
   of the tokens found in a document, what fraction have a valid
   classification defined). |image|

-  Summary statistics are also shown. |image|

-  The “create new CSV” button will create an .csv with the original
   dataset and 7 new columns (“I”,“P”,”PI”, “S”,“SI”,“U”, and “X”) ,
   which contain the new tags from each category. Please note that “X”
   contains any stop words. |image|

-  The “create a binary CSV” button will create 2 new .csv files. Each
   file will contain the work order number (starting with 0), and is
   ordered identically to the .csv file that was originally loaded. Two
   new files are created: binary_tags and binary_relations. |image|

   -  binary_tags: The left most column contains the work order number,
      while the headers contain all 1 gram tags. A “0” is placed when
      the work order does not contain the tag in the header and a “1” is
      placed when the tag in the header is contained in the work order.

   -  binary_relations: The left most column contains the work order
      number, while the headers contain Problem-Item and Solution-Item
      tag combinations. A “0” is placed when the work order does not
      contain the tag in the header and a “1” is placed when the tag in
      the header is contained in the work order.






.. |image| image:: images/Graphic29_v2.png
.. |image| image:: images/Graphic30_v2.png
.. |image| image:: images/Graphic31_v2.png
.. |image| image:: images/Graphic32_v2.png
.. |image| image:: images/Graphic33_v2.png
.. |image| image:: images/Graphic34_v2.png
.. |image| image:: images/Graphic35_v2.png
.. |image| image:: images/Graphics36_v2.png
.. |image| image:: images/Graphics37_v2.png
.. |image| image:: images/Graphics38_v2.png
.. |image| image:: images/Graphics40_v2.png
.. |image| image:: images/Graphics41_v2.png
.. |image| image:: images/Graphics42_v2.png
.. |image| image:: images/Graphics43_v2.png
.. |image| image:: images/Graphics44_v2.png
.. |image| image:: images/Graphics45_v2.png
.. |image| image:: images/Graphics46_v2.png
.. |image| image:: images/Graphics47_v2.png
.. |image| image:: images/Graphics48_v2.png
.. |image| image:: images/Graphics49_v2.png
.. |image| image:: images/Graphics50_v2.png
.. |image| image:: images/Graphics51_v2.png
.. |image| image:: images/Graphics52_v2.png
.. |image| image:: images/Graphics53_v2.png
.. |image| image:: images/Graphics54_v2.png
.. |image| image:: images/Graphics55_v2.png
.. |image| image:: images/Graphics56_v2.png

