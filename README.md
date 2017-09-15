# BD2K-CaseReportsDataset
UCLA Heart BD2K Case Reports Dataset metadata extraction script.

## Abbreviations and Syntax

* *CCR*: Clinical case report
* *Indexed By MeSH*: Metadata obtained from PubMed, including from MeSH terms
* *Contained in Context*: Other metadata obtained elsewhere, usually from Web of Science or the full text of the article.

## Usage Instructions

### File Explanations
You should be able to download the following files from this GitHub page.
* [**ExtractionScript.py**](./ExtractionScript.py): This is the main script you will be using. 
* [**prep_journals.py**](./prep_journals.py): This is used to create impact_dict.txt, and journal_dict.txt, which ExtractionScript.py reads in as dictionaries.  The impact_dict.txt file maps journal names to journal impact factors, and is taken directly from Journal_Impact_factor_2017.txt, while journal_dict.txt maps journal name synonyms to the version of the journal name used in impact_dict.txt, and is taken from both Journal_Impact_factor_2017.txt and nlmcatalog_result.xml. 
* [**nlmcatalog_result.xml¹**](./nlmcatalog_result.xml): This is necessary for prep_journals.py.  This file contains journal xml information retrieved from the NLM catalog¹.
* [**requirements.txt**](./requirements.txt): Used to create the virtual environment using virtualenv.

You should be able to download the following file online.
* [**Journal_Impact_factor_2017.txt²**](https://www.researchgate.net/file.PostFileLoader.html?id=59421163eeae3996516e41ae&assetKey=AS%3A524678465638401%401502104502262): This is an excel file with the InCites™ 2017 Journal Citation Reports© and is necessary for running prep_journals.py. 

You should be able to make these files by running prep_journals.py.
* **impact_dict.txt**: This is necessary for ExtractionScript.py, and is created by prep_journals.py.  Once you activate the virtual environment you can run prep_journals.py to create this.
* **journal_dict.txt**: This is necessary for ExtractionScript.py, and is created by prep_journals.py.  Once you activate the virtual environment you can run prep_journals.py to create this. 

The following file is not neccessary for running any of the scripts, but is a template showing how I manually extracted my metadata files, and is provided for help in normalization of the data, so that you know how I decided what to include in various cells.
* [**template_metadata-SS.xlsx**](./template_metadata-SS.xlsx)


### Input Data
You will need to have a directory that contains the Excel sheets you want to process.  For example, could have a “1800” directory containing our 1800 metadata extraction excel files. 

Download these from Google Drive directory.

Go through and move all the files into the main directory and then delete the empty subfolders.  (Unless you want to change the script and tell it to go check all those directories.) Note, the correct versions of Jessica's files are in the "Homogenized Files" folder under her subfolder.  Ignore the other file versions.

*__Note: there are still a few duplicates and problem files on the Google Drive.  See terminal output when you read the script.  See also “Errors” column in main output file.__*

### Setting Up Virtual Environment
This script uses [virtualenv](https://virtualenv.pypa.io/en/stable/) to create a virtual environment in which to run the script.  This ensures that the necessary python version and packages are installed.  The “requirements.txt” file will allow you to create your own copy of this environment in your own file system. Here I will give directions on how to create and use this virtual environment. For the sake of the example, we will call it “my_env,” but it doesn’t matter what you call it.

The first time, run the following to create the virtual environment:
```
sudo pip install virtualenv
virtualenv my_env
source my_env/bin/activate
pip install –r <path to wherever you have requirements.txt saved>
```

Every other time, as long as you are in the same place in our filesystem, you simply need to run the following to activate the virtual environment:
```
source my_env/bin/activate
```

### Running prep_journals.py
You only really need to run this once to create  the journal_dict.txt and impact_dict.txt files, unless you edit the prep_journals.py file.  *(You actually may want to edit this file to try to see if you can catch any more journal name variations. But if you do modify the file, then be sure to rerun it before running ExtractionScript.py so that you have updated versions of journal_dict.txt and impact_dict.txt.)*
```
python prep_journals.py 
```

### Running ExtractionScript.py
Make sure you are still inside the correct directory, containing this script, the virtual environment folder, and the files created by prep_journals.py.  You also need to know the file path of the directory containing the desired Excel files.  I usually just put the Excel files in a subdirectory of the directory I am working in. For this example, we will run the script on the files in a “TEST” directory that is assumed to be inside the directory you are working in.

Decide on a base name for your output files (In this case we will use “testing.txt”)

Run the following line:
```
python ExtractionScript.py TEST/ testing.txt
```
*__Note: Make sure you include the extra “/” at the end of the file path where the Excel files are stored!!__*

If you want to save the terminal output to a file called "testing_terminal_output.txt", you can do the following:
```
python ExtractionScript.py TEST/ testing.txt > testing_terminal_output.txt
```

### Explanation of Output Files
* **testing.txt**: Main output summary table.  Each line represents one CCR.  Summarizes the most important pieces of information from the dataset, including indicating which disease systems each CCR is related to.  In addition it also parses some of the data (like demographics) into a more analyzable form.  *__Note: We may want to edit which pieces of information are contained here slightly.__*
     * Not all the pieces of metadata are summarized here, but in my script I made a variable for each metadata item based on which column (either contained in context or indexed by MeSH) normally has the best version of that piece of metadata, and so it should be a relatively simple thing to add any piece of metadata you desire. 
     * Information about how data-parsing was accomplished can be found at the bottom of this document.
* **AGES_testing.txt**: Look at this to verify that the age and gender were parsed correctly from the demographics.  Each line represents one CCR.
* **CCR_NUMS_testing.txt**: Gives a list of the CCR number, the PMID, and contributor initials for each CCR. 
* **JOURNALS_MISSING_IMPACT_FACTOR_testing.txt**: Gives a list of all the journal names the script didn’t recognize, and thus was unable to assign an updated impact factor.  
* **RAW_IN_CONTEXT_testing.txt**: Contains raw, unparsed information from the “Contained in Context” column.  Each line represents one CCR.
* **RAW_INDEX_BY_MESH_testing.txt**: Contains raw, unparsed information form the “Indexed by MeSH” column.  Each line represents one CCR.
* **SCORE_testing.txt**: Score table.  Contains all the scores from the dataset.  Unlike the other output tables, this file has two lines per CCR, one for each of the two columns of scores *Note: You may want to edit this to get rid of the scores in the Identification section, since this information was often copied and pasted, and thus the scores are uninformative*

### Explanation of Terminal Output
The terminal output has three parts

1. Selected Problems with Individual Files:
     * The terminal will print out some of the most important errors it encounters when reading the data (For example, if the PMID in a file name does not match the PMID given inside the file).
     * All of the errors and warnings generated for each CCR (except for information about missing/duplicate case report numbers, see below) can be found by examining the “Errors” column of the main output file (“testing.txt” in this case).
2. Impact Factor Problems:
     * While there were too many problems of this sort to print them all out above, I print out summary information of the amount of errors of this sort we have.  
     * If you are interested in which specific CCRs had journals the script had problems with, see the Errors column in the output file as noted above.
     * In addition, the JOURNALS_MISSING_IMPACT_FACTOR file lists each unique journal that was not recognized. 
3. Missing and Duplicate Case Report Numbers:
     * My script keeps track of which case report numbers are used and prints out which are duplicated and which are missing (assuming you desire CCRs from 0001 to 1800).  Feel free to edit the code to look for a different CCR number range if needed.
     * Be careful, the “duplicates” may really be duplicates, but they may also simply be unique files that were accidentally given the same CCR number

## Parsing And Quality Control Explanations
Here I will explain how we parsed and double checked some of the information.
#### Standardization of Journal Name and Impact Factor
(coming soon)
#### Checking in file PMID with PMID in File Name
(coming soon)
#### Parsing Age and Gender from "Demographics" Text
(coming soon)
#### Parsing "Disease System" Text into Binary Values Representing Each of 15 Disease Systems
(coming soon)
#### Parsing Number of Database Crosslinks from "Crosslink with Database" Text
(coming soon)
#### Parsing the Number of Images, Illustrations, Videos, and Tables from "Diagnostic Imaging/Videotape Recording" Text
(coming soon)
#### Parsing the Number of References
(coming soon)

## Future Work
There are several improvements that can be made to this part of the project.
* There are still some journal names that we don't have impact factors for. I am not sure what percentage of those is due to those journals not having impact factors, and what percentage is because we are missing name variations.  It would be good for someone to look into this and do some optimizations to make sure all journals that have impact factors are covered.  Edit the prep_journals.py file to do this, and then rerun the file to get updated dictionary files.
* Clement came up with a good way to condense some of the code into fewer lines.  He is planning on working on that.
* There are still some formatting inconcsistencies and errors in the datafiles. See "errors" column in main output file. Throughout my code I generate various error and warning messages and then concatenate these into the error column at the end of the file. It would be very good for someone to go through those warnings and errors and try to account for them.
* As has been discussed previously, there will probably be normalizations and such to do on the data to help make up for some of the inconsistencies in data extraction methods.
* It would also be good for someone to look at the AGES files and make sure there are no weirdly formatted genders/ages we are parsing wrong.  You could also do more general error checking to make sure we are returning everything right. 

## Sources
1. NLM Catalog [Internet]. Bethesda MD: National Library of Medicine (US). [date unknown] - . Results from searching currentlyindexed[All] and downloading in XML format; [cited 2017 Sep 14]. Available from: https://www.ncbi.nlm.nih.gov/nlmcatalog?Db=journals&Cmd=DetailsSearch&Term=currentlyindexed%5BAll%5D.
2. InCites™ 2017 Journal Citation Reports© [Internet].  Thomson Reuters [date unknown] - . Excel file downloaded from Research Gate post by Murtaza Sayed; [cited 2017 Sep 14]. Available from: https://www.researchgate.net/post/New_Impact_factors_2017_for_Journals_are_released_now.

## Acknowledgements
* Thanks to the many contributors on [StackOverflow](https://stackoverflow.com).  This was an invaluable resource in developing the scripts.
* Selection of other helpful resources:
     * For further information about using virtualenv see [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and [here](https://stackoverflow.com/questions/14684968/how-to-export-virtualenv)
     * GitHub README [template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
     * The [word2number](https://pypi.python.org/pypi/word2number/1.1) package
     * Pandas [documentation](https://pandas.pydata.org/pandas-docs/stable/)and [cheatsheet](https://s3.amazonaws.com/assets.datacamp.com/blog_assets/PandasPythonForDataScience.pdf)









