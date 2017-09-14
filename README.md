# BD2K-CaseReportsDataset
UCLA Heart BD2K Case Reports Dataset metadata extraction script

## Abbreviations and Syntax

* *CCR*: Clinical case report
* *Indexed By MeSH*: Metadata obtained from PubMed, including from MeSH terms
* *Contained in Context*: Other metadata obtained elsewhere, usually from Web of Science or the full text of the article.

## Usage Instructions
 
### File Explanations

You should be able to download the following files from this GitHub page.
* [*ExtractionScript.py*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/ExtractionScript.py): This is the main script you will be using. 
* [*impact_dict.txt*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/impact_dict.txt): This is necessary for ExtractionScript.py, and was created by *prep_journals.py*. If you do not have this, once you activate the virtual environment you can run *prep_journals.py* to create this.
* [*ji_list.txt(1)*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/ji_list.txt): This is necessary for *prep_journals.py*, and is a text file version of the 2016 Journal Data from InCites Journal Citation Reports. I have an updated version from John that I am going to end up using instead, especially because it has a source whereas the other doesn’t. 
* [*journal_dict.txt*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/journal_dict.txt): This is necessary for *ExtractionScript.py*, and was created by *prep_journals.py*. If you do not have this, once you activate the virtual environment you can run *prep_journals.py* to create this. 
* [*nlmcatalog_result.xml(2)*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/nlmcatalog_result.xml): This is necessary for *prep_journals.py*. This file contains journal xml information retrieved from the NLM catalog(2).
* [*prep_journals.py*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/prep_journals.py): This was used to create *impact_dict.txt*, and *journal_dict.txt*, which *ExtractionScript.py* reads in as dictionaries. *impact_dict.txt* maps journal names to journal impact factors, and is taken directly from *ji_list.txt*, while *journal_dict.txt* maps journal name synonyms to the version of the journal name used in *impact_dict.txt*, and is taken from both *ji_list.txt* and *nlmcatalog_result.xml*. 
* [*requirements.txt*](https://github.com/Spendlove/BD2K-CaseReportsDataset/blob/master/requirements.txt): Used to create the virtual environment using ____.

### Input Data

You will need to have a directory that contains the Excel sheets you want to process. For example, could have a “1800” directory containing our 1800 metadata extraction excel files. 

Download these from Google Drive directory

Go through and move all the files into the main directory and then delete the empty subfolders. (Unless you want to change the script and tell it to go check all those directories.  It’s easier if all the files are in one directory though.)

Note, there are still a few duplicates and problem files on the Google Drive. See terminal output when you read the script.  See also “Errors” column in main output file.

### Setting Up Virtual Environment

This script uses virtualenv(3) to create a virtual environment in which to run the script.  This ensures that the necessary python version and packages are installed.  The “requirements.txt” file will allow you to create your own copy of this environment in your own file system. Here I will give directions on how to create and use this virtual environment. For the sake of the example, we will call it “my_env,” but it doesn’t matter what you call it.

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
For further information about using virtualenv see [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and here(https://stackoverflow.com/questions/14684968/how-to-export-virtualenv)

### Running prep_journals.py

You only really need to run this if you need the journal_dict.txt and impact_dict.txt files, and you only need to run it once, unless you edit the prep_journals.py file.  You actually may want to edit this file to try to see if you can catch any more journal name variations. If you do change it, then be sure to rerun this file before running ExtractionScript.py
```
python prep_journals.py 
```

### Running ExtractionScript.py

Make sure you are still inside the correct directory, containing this script, the virtual environment folder, and the files created by prep_journals.py.  You also need to know the file path of the directory containing the desired Excel files.  I usually just put the Excel files in a subdirectory of the directory I am working in. For this example, we will run the script on the files in a “TEST” directory that is assumed to be inside the directory you are working in.

Decide on a base name for your output files (In this case we will use “testing.txt”)

Run the following line:
```
python ExtractionScript.py TEST/ testing.txt
#Make sure you include the extra “/” at the end of the file path where the Excel files are stored
```
### Output Files









