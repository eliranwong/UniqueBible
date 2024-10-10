## Original Author

Tim Morton

Thanks to Tim Morton for sharing this work on github.com!

## Original Source

https://github.com/tsmorton60/Strongs2csv

## Strongs2CSV

Strongs2CSV is a Python script to generate a CSV file for Excel or any other spreadsheet program of Strong's data on words in the King James Bible. 

The user provides the Strong's number(s) he wishes to search for to the script and it will search the included King James Bible database for every instance of the number plus its associated English word. The CSV file will contain several columns of relevant Strongs and King James Bible data, such as *Book, Verse Reference, Verse text, English Word, Original Word, Transliteration, and Definition.* 

### Usage

The user can add the Strong number(s) as an argument or run the script without arguments and provide the number(s) via a prompt.

strongs2csv.py G25

Multiple numbers must be comma separated without any spaces,

strongs2csv.py H234,G25,G4556

### Benefit

When opened in a speadsheet program the CSV data can be manipulated in several ways. Columns can be sorted, filtered, and otherwise enhanced. For instance, if one wanted to view the rows in English word order, original word order, etc., they can simply sort the appropriate column. If he only wanted to see the results of certain Bible books, the Books column can be filtered to do so.
