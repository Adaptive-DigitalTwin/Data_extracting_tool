# Data_extraction
This tool for extraction of the data from both structured and unstructured data source which could be in text, image, or any other formats.
Particyularly, our field of interest is Corrosion related data.

1.	Install Python IDE (Recommendation anaconda(package) which has Jupyter notebooks and Spyder for Python)
2.	Install the following packages:
a.	Pdfminer
b.	Io
c.	Camelot – See the description to install this package (needs ghostscript and tkinter)  https://pypi.org/project/camelot-py/
d.	difflib
e.	numpy
f.	re
g.	nltk
h.	dateutil
i.	pandas
3.	Save the given codes in the working directory.
4.	Also set the directory for Input and output from the code.
5.	Run the ‘main’ file considering the following.
a.	Give file name with location for ‘pdf_file_with_path’
b.	If available, location name can be given manually under ‘manually_feeding_location_name’.
c.	Also repeat the same as ‘b’ for ‘sub_parts_string_list’
(Note: The tool will detect the location name available in the pdf file under the tables with column title ‘location’
Output:
1.	The extracted pages are saved in ‘pickle’ format which saves time allowing us to read from it, instead of reading the pdf page again in case needed further.
2.	The result is extracted in csv format. 
a.	Merged tables related to the data of interest like (‘CP’)
b.	Individual tables related to the data of interest are also exported to the csv format.
c.	DataFrame is constructed from the plain text data with the basis of Ontology creation and exported.
